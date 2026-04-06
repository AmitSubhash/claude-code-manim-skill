"""voiceover command: generate single-speaker narration audio."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click

from .edit_scene import _discover_scenes, _find_project_dir

DEFAULT_MODEL_PATH = "microsoft/VibeVoice-Realtime-0.5B"
DEFAULT_BACKEND = "vibevoice"
DEFAULT_SPEAKER = "Carter"
DEFAULT_SOURCE_MODE = "auto"
DEFAULT_VOICE_DIR_ENV = "VIBEVOICE_VOICES_DIR"
DEFAULT_KOKORO_LANG = "a"
DEFAULT_KOKORO_SPEAKER = "af_bella,af_sarah"
DEFAULT_KOKORO_SPEED = 1.15
DEFAULT_KOKORO_PYTHON_ENV = "THREE_B1B_KOKORO_PYTHON"
REPO_ROOT = Path(__file__).resolve().parents[2]

_MARKDOWN_CANDIDATES = (
    "narration.md",
    "plan.md",
    "video_plan.md",
    "storyboard.md",
)

_LATEX_SPOKEN = {
    "alpha": "alpha",
    "beta": "beta",
    "gamma": "gamma",
    "delta": "delta",
    "epsilon": "epsilon",
    "theta": "theta",
    "lambda": "lambda",
    "mu": "mu",
    "nu": "nu",
    "pi": "pi",
    "sigma": "sigma",
    "tau": "tau",
    "phi": "phi",
    "psi": "psi",
    "omega": "omega",
}


@dataclass
class NarrationBeat:
    """A narration unit aligned to one scene beat."""

    beat_index: int
    text: str
    source_label: str
    target_duration: float


@dataclass
class NarrationChunk:
    """A narration block destined for one output audio file."""

    slug: str
    text: str
    source_label: str
    beats: Optional[list[NarrationBeat]] = None


def _normalize_for_tts(text: str) -> str:
    """Clean markdown and LaTeX-ish notation into TTS-friendly prose."""
    cleaned = text
    cleaned = re.sub(r"```.*?```", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = cleaned.replace("->", " to ")
    cleaned = cleaned.replace("=>", " then ")
    cleaned = cleaned.replace("&", " and ")
    cleaned = cleaned.replace("%", " percent")
    cleaned = cleaned.replace("~", " approximately ")
    cleaned = cleaned.replace("vs.", "versus")
    cleaned = cleaned.replace("e.g.", "for example")
    cleaned = cleaned.replace("i.e.", "that is")
    cleaned = re.sub(r"\\text\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\mathcal\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(
        r"\\([A-Za-z]+)",
        lambda match: _LATEX_SPOKEN.get(match.group(1), match.group(1)),
        cleaned,
    )
    cleaned = cleaned.replace("{", " ")
    cleaned = cleaned.replace("}", " ")
    cleaned = cleaned.replace("_", " ")
    cleaned = re.sub(r"^\s*[-*]\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*>\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().strip('"').strip("'")


def _extract_scene_comment_narration(scene_file: Path) -> list[str]:
    """Extract '# NARRATION:' comments from a scene file."""
    matches: list[str] = []
    for line in scene_file.read_text().splitlines():
        match = re.match(r'^\s*#\s*NARRATION:\s*(.+?)\s*$', line)
        if not match:
            continue
        text = match.group(1).strip().strip('"').strip("'")
        if text:
            matches.append(text)
    return matches


def _collect_call(lines: list[str], start_idx: int, token: str) -> tuple[str, int]:
    """Collect a multi-line self.play()/self.wait() call."""
    parts: list[str] = []
    depth = 0
    started = False
    idx = start_idx
    while idx < len(lines):
        line = lines[idx]
        if not started:
            pos = line.find(token)
            if pos == -1:
                return "", start_idx + 1
            fragment = line[pos:]
            parts.append(fragment)
            depth = fragment.count("(") - fragment.count(")")
            started = True
            idx += 1
            if depth <= 0:
                return "\n".join(parts), idx
            continue

        parts.append(line)
        depth += line.count("(") - line.count(")")
        idx += 1
        if depth <= 0:
            return "\n".join(parts), idx

    return "\n".join(parts), idx


def _duration_from_statement(statement: str) -> float:
    """Estimate duration from self.play()/self.wait() source."""
    stripped = statement.strip()
    if stripped.startswith("self.wait("):
        match = re.search(r"self\.wait\(\s*([0-9.]+)", stripped)
        return float(match.group(1)) if match else 1.0
    if stripped.startswith("self.play("):
        match = re.search(r"run_time\s*=\s*([0-9.]+)", stripped)
        return float(match.group(1)) if match else 1.0
    return 0.0


def _sum_statement_durations(lines: list[str]) -> float:
    """Sum durations of self.play()/self.wait() calls in a block."""
    total = 0.0
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if "self.play(" in line:
            statement, idx = _collect_call(lines, idx, "self.play(")
            total += _duration_from_statement(statement)
            continue
        if "self.wait(" in line:
            statement, idx = _collect_call(lines, idx, "self.wait(")
            total += _duration_from_statement(statement)
            continue
        idx += 1
    return total


def _extract_scene_comment_beats(scene_file: Path) -> list[NarrationBeat]:
    """Extract grouped narration beats from a scene file."""
    lines = scene_file.read_text().splitlines()
    beats: list[NarrationBeat] = []
    idx = 0
    while idx < len(lines):
        match = re.match(r'^\s*#\s*NARRATION:\s*(.+?)\s*$', lines[idx])
        if match is None:
            idx += 1
            continue

        comment_lines: list[str] = []
        while idx < len(lines):
            match = re.match(r'^\s*#\s*NARRATION:\s*(.+?)\s*$', lines[idx])
            if match is None:
                break
            text = match.group(1).strip().strip('"').strip("'")
            if text:
                comment_lines.append(text)
            idx += 1

        block_end = idx
        while block_end < len(lines):
            if re.match(r'^\s*#\s*NARRATION:\s*(.+?)\s*$', lines[block_end]):
                break
            block_end += 1

        beat_text = _normalize_for_tts(" ".join(comment_lines))
        if beat_text:
            beats.append(
                NarrationBeat(
                    beat_index=len(beats) + 1,
                    text=beat_text,
                    source_label=f"{scene_file.name} beat {len(beats) + 1}",
                    target_duration=_sum_statement_durations(lines[idx:block_end]),
                )
            )
        idx = block_end
    return beats


def _chunks_from_scene_comments(project_dir: Path) -> list[NarrationChunk]:
    """Build narration chunks from scene-level NARRATION comments."""
    chunks: list[NarrationChunk] = []
    for scene in _discover_scenes(project_dir):
        beats = _extract_scene_comment_beats(scene["file"])
        if not beats:
            continue
        text = _normalize_for_tts(" ".join(beat.text for beat in beats))
        if text:
            chunks.append(
                NarrationChunk(
                    slug=scene["file"].stem,
                    text=text,
                    source_label=scene["file"].name,
                    beats=beats,
                )
            )
    return chunks


def _extract_narration_section(markdown: str) -> str:
    """Return the 'Narration Script' section if present."""
    match = re.search(
        r"(?ms)^##\s+Narration Script\s*$\n?(.*?)(?=^##\s+\S|^#\s+\S|\Z)",
        markdown,
    )
    return match.group(1).strip() if match else ""


def _chunks_from_section_blocks(
    section: str,
    scene_slugs: list[str],
) -> list[NarrationChunk]:
    """Parse scene headings, timestamp blocks, or paragraphs from a section."""
    chunks: list[NarrationChunk] = []

    heading_pattern = re.compile(
        r"(?ms)^(?:###|##)\s*Scene\s+(\d+)[^\n]*\n(.*?)(?=^(?:###|##)\s*Scene\s+\d+|\Z)"
    )
    heading_blocks = list(heading_pattern.finditer(section))
    if heading_blocks:
        for idx, match in enumerate(heading_blocks, 1):
            slug = (
                scene_slugs[idx - 1]
                if idx - 1 < len(scene_slugs)
                else f"scene_{idx:02d}"
            )
            text = _normalize_for_tts(match.group(2))
            if text:
                chunks.append(
                    NarrationChunk(
                        slug=slug,
                        text=text,
                        source_label=f"Scene {match.group(1)}",
                    )
                )
        return chunks

    timestamp_pattern = re.compile(
        r"(?ms)^\[([^\]]+)\]\s*([^\n]*)\n(.*?)(?=^\[[^\]]+\]\s*[^\n]*\n|\Z)"
    )
    timestamp_blocks = list(timestamp_pattern.finditer(section))
    if timestamp_blocks:
        for idx, match in enumerate(timestamp_blocks, 1):
            slug = (
                scene_slugs[idx - 1]
                if idx - 1 < len(scene_slugs)
                else f"segment_{idx:02d}"
            )
            title = match.group(2).strip() or match.group(1).strip()
            text = _normalize_for_tts(match.group(3))
            if text:
                chunks.append(
                    NarrationChunk(
                        slug=slug,
                        text=text,
                        source_label=title,
                    )
                )
        return chunks

    paragraphs = [
        _normalize_for_tts(block)
        for block in re.split(r"\n\s*\n+", section)
        if block.strip()
    ]
    paragraphs = [paragraph for paragraph in paragraphs if len(paragraph.split()) >= 4]
    for idx, paragraph in enumerate(paragraphs, 1):
        slug = (
            scene_slugs[idx - 1]
            if idx - 1 < len(scene_slugs)
            else f"segment_{idx:02d}"
        )
        chunks.append(
            NarrationChunk(
                slug=slug,
                text=paragraph,
                source_label=f"Block {idx}",
            )
        )
    return chunks


def _chunks_from_storyboard(markdown: str, scene_slugs: list[str]) -> list[NarrationChunk]:
    """Fallback parser for storyboard files using 'Narration concept:' lines."""
    pattern = re.compile(
        r"(?ms)^##\s*Scene\s+(\d+):[^\n]*\n(.*?)(?=^##\s*Scene\s+\d+:|\Z)"
    )
    chunks: list[NarrationChunk] = []
    for idx, match in enumerate(pattern.finditer(markdown), 1):
        body = match.group(2)
        concept = re.search(r"(?m)^Narration concept:\s*(.+?)\s*$", body)
        if concept is None:
            continue
        slug = (
            scene_slugs[idx - 1]
            if idx - 1 < len(scene_slugs)
            else f"scene_{idx:02d}"
        )
        text = _normalize_for_tts(concept.group(1))
        if text:
            chunks.append(
                NarrationChunk(
                    slug=slug,
                    text=text,
                    source_label=f"Scene {match.group(1)}",
                )
            )
    return chunks


def _scene_slugs(project_dir: Optional[Path]) -> list[str]:
    """Return scene stems from a project directory."""
    if project_dir is None:
        return []
    return [scene["file"].stem for scene in _discover_scenes(project_dir)]


def _find_markdown_candidate(project_dir: Path) -> Optional[Path]:
    """Find a narration-capable markdown document in a project directory."""
    for name in _MARKDOWN_CANDIDATES:
        candidate = project_dir / name
        if candidate.exists():
            return candidate
    return None


def _load_narration_chunks(
    source: Path,
    project_dir: Optional[Path],
    source_mode: str,
) -> tuple[list[NarrationChunk], Optional[Path]]:
    """Load narration chunks from a file or project directory."""
    if source.is_dir():
        project_dir = _find_project_dir(source)
        chunks = _chunks_from_scene_comments(project_dir)
        if chunks:
            return chunks, project_dir

        markdown = _find_markdown_candidate(project_dir)
        if markdown is None:
            return [], project_dir
        source = markdown

    if project_dir is not None and source_mode in ("auto", "scene-comments"):
        comment_chunks = _chunks_from_scene_comments(project_dir)
        if comment_chunks:
            return comment_chunks, project_dir

    if source.suffix == ".py":
        beats = _extract_scene_comment_beats(source)
        if beats:
            return [
                NarrationChunk(
                    slug=source.stem,
                    text=_normalize_for_tts(" ".join(beat.text for beat in beats)),
                    source_label=source.name,
                    beats=beats,
                )
            ], project_dir

        lines = _extract_scene_comment_narration(source)
        text = _normalize_for_tts(" ".join(lines))
        if not text:
            return [], project_dir
        return [
            NarrationChunk(
                slug=source.stem,
                text=text,
                source_label=source.name,
            )
        ], project_dir

    markdown = source.read_text()
    scene_slugs = _scene_slugs(project_dir)
    section = _extract_narration_section(markdown)
    if section:
        return _chunks_from_section_blocks(section, scene_slugs), project_dir

    storyboard_chunks = _chunks_from_storyboard(markdown, scene_slugs)
    if storyboard_chunks:
        return storyboard_chunks, project_dir

    return _chunks_from_section_blocks(markdown, scene_slugs), project_dir


def _scan_voice_prompts(voices_dir: Path) -> dict[str, Path]:
    """Return available VibeVoice prompt files keyed by preset name."""
    prompts: dict[str, Path] = {}
    for path in sorted(voices_dir.rglob("*.pt")):
        prompts[path.stem.lower()] = path
    return prompts


def _resolve_voice_prompt(
    voice_prompt: Optional[Path],
    voices_dir: Optional[Path],
    speaker_name: str,
) -> tuple[Optional[Path], dict[str, Path]]:
    """Resolve the voice prompt path and return the discovered voice registry."""
    if voice_prompt is not None:
        return voice_prompt, {}

    resolved_dir = voices_dir
    if resolved_dir is None:
        env_dir = os.environ.get(DEFAULT_VOICE_DIR_ENV, "").strip()
        if env_dir:
            resolved_dir = Path(env_dir)

    if resolved_dir is None:
        return None, {}
    if not resolved_dir.exists():
        click.echo(f"Voice prompt directory not found: {resolved_dir}")
        sys.exit(1)

    prompts = _scan_voice_prompts(resolved_dir)
    if not prompts:
        click.echo(f"No .pt voice prompts found under {resolved_dir}")
        sys.exit(1)

    speaker_key = speaker_name.strip().lower()
    if speaker_key in prompts:
        return prompts[speaker_key], prompts

    matches = [
        path for name, path in prompts.items()
        if speaker_key in name or name in speaker_key
    ]
    if len(matches) == 1:
        return matches[0], prompts
    if len(matches) > 1:
        click.echo(
            f"Speaker '{speaker_name}' matches multiple presets. "
            f"Use --voice-prompt or a more specific --speaker-name."
        )
        sys.exit(1)

    default_name, default_path = next(iter(prompts.items()))
    click.echo(
        f"No preset matched '{speaker_name}'. Using default voice '{default_name}'."
    )
    return default_path, prompts


def _resolve_device(torch_module, device: str) -> str:
    """Pick an execution device following the VibeVoice demo behavior."""
    if device != "auto":
        return device
    if torch_module.cuda.is_available():
        return "cuda"
    if torch_module.backends.mps.is_available():
        return "mps"
    return "cpu"


def _load_vibevoice_runtime(model_path: str, device: str, ddpm_steps: int):
    """Load VibeVoice-Realtime runtime objects."""
    try:
        import torch
        from vibevoice.modular.modeling_vibevoice_streaming_inference import (
            VibeVoiceStreamingForConditionalGenerationInference,
        )
        from vibevoice.processor.vibevoice_streaming_processor import (
            VibeVoiceStreamingProcessor,
        )
    except ImportError:
        click.echo(
            "VibeVoice-Realtime is not installed.\n"
            "Install it from a local clone of microsoft/VibeVoice, for example:\n"
            "  git clone https://github.com/microsoft/VibeVoice.git\n"
            "  cd VibeVoice\n"
            "  pip install -e .[streamingtts]"
        )
        sys.exit(1)

    resolved_device = _resolve_device(torch, device)
    if resolved_device == "mps":
        load_dtype = torch.float32
        attn_impl_primary = "sdpa"
    elif resolved_device == "cuda":
        load_dtype = torch.bfloat16
        attn_impl_primary = "flash_attention_2"
    else:
        load_dtype = torch.float32
        attn_impl_primary = "sdpa"

    processor = VibeVoiceStreamingProcessor.from_pretrained(model_path)
    try:
        if resolved_device == "mps":
            model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                model_path,
                torch_dtype=load_dtype,
                attn_implementation=attn_impl_primary,
                device_map=None,
            )
            model.to("mps")
        else:
            model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                model_path,
                torch_dtype=load_dtype,
                device_map=resolved_device,
                attn_implementation=attn_impl_primary,
            )
    except Exception:
        if attn_impl_primary != "flash_attention_2":
            raise
        click.echo("flash_attention_2 load failed. Retrying with sdpa.")
        model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
            model_path,
            torch_dtype=load_dtype,
            device_map=resolved_device,
            attn_implementation="sdpa",
        )

    model.eval()
    model.set_ddpm_inference_steps(num_steps=ddpm_steps)
    return torch, processor, model, resolved_device


def _generate_audio_file(
    torch_module,
    processor,
    model,
    device: str,
    voice_prompt: Path,
    text: str,
    output_path: Path,
    cfg_scale: float,
) -> None:
    """Run one VibeVoice-Realtime generation and write the wav file."""
    import copy

    prompt_cache = torch_module.load(
        voice_prompt,
        map_location=device,
        weights_only=False,
    )
    inputs = processor.process_input_with_cached_prompt(
        text=text,
        cached_prompt=prompt_cache,
        padding=True,
        return_tensors="pt",
        return_attention_mask=True,
    )
    for key, value in inputs.items():
        if torch_module.is_tensor(value):
            inputs[key] = value.to(device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=None,
        cfg_scale=cfg_scale,
        tokenizer=processor.tokenizer,
        generation_config={"do_sample": False},
        verbose=True,
        all_prefilled_outputs=copy.deepcopy(prompt_cache),
    )
    processor.save_audio(outputs.speech_outputs[0], output_path=str(output_path))


def _concat_wavs(
    beat_paths: list[Path],
    output_path: Path,
    target_durations: list[float],
) -> None:
    """Concatenate beat wavs into one scene wav, padding short beats with silence."""
    try:
        import numpy as np
        import soundfile as sf
    except ImportError:
        click.echo("Run: pip install soundfile numpy")
        sys.exit(1)

    pieces = []
    sample_rate: Optional[int] = None
    for idx, beat_path in enumerate(beat_paths):
        data, sr = sf.read(beat_path)
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            click.echo(f"Sample rate mismatch in {beat_path.name}")
            sys.exit(1)

        if getattr(data, "ndim", 1) > 1:
            data = data[:, 0]

        target_seconds = target_durations[idx] if idx < len(target_durations) else 0.0
        target_samples = int(round(max(target_seconds, 0.0) * sr))
        if target_samples > len(data):
            pad = np.zeros(target_samples - len(data), dtype=data.dtype)
            data = np.concatenate([data, pad])

        pieces.append(data)

    if not pieces or sample_rate is None:
        click.echo("No beat audio generated.")
        sys.exit(1)

    sf.write(output_path, np.concatenate(pieces), sample_rate)


def _write_manifests(output_dir: Path, chunks: list[NarrationChunk]) -> tuple[Path, Path]:
    """Write markdown and JSON voiceover manifests."""
    manifest_md = output_dir / "manifest.md"
    lines = [
        "# Voiceover Manifest",
        "",
    ]
    for chunk in chunks:
        lines.append(f"- `{chunk.slug}.wav`: {chunk.source_label}")
        if chunk.beats:
            for beat in chunk.beats:
                beat_name = f"_beats/{chunk.slug}/beat_{beat.beat_index:02d}.wav"
                lines.append(
                    f"  - `{beat_name}`: target {beat.target_duration:.2f}s"
                )
    manifest_md.write_text("\n".join(lines) + "\n")

    manifest_json = output_dir / "manifest.json"
    payload = {
        "version": 1,
        "scenes": [],
    }
    for chunk in chunks:
        scene_entry = {
            "slug": chunk.slug,
            "source_label": chunk.source_label,
            "scene_audio": f"{chunk.slug}.wav",
            "beats": [],
        }
        if chunk.beats:
            for beat in chunk.beats:
                scene_entry["beats"].append(
                    {
                        "beat_index": beat.beat_index,
                        "text": beat.text,
                        "source_label": beat.source_label,
                        "target_duration": beat.target_duration,
                        "audio": f"_beats/{chunk.slug}/beat_{beat.beat_index:02d}.wav",
                    }
                )
        payload["scenes"].append(scene_entry)
    manifest_json.write_text(json.dumps(payload, indent=2) + "\n")
    return manifest_md, manifest_json


def _resolve_kokoro_python(explicit_path: Optional[Path]) -> Path:
    """Resolve the Python executable used for Kokoro synthesis."""
    if explicit_path is not None:
        return explicit_path.resolve()

    env_path = os.environ.get(DEFAULT_KOKORO_PYTHON_ENV, "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()

    local_env = REPO_ROOT / ".tts311" / "bin" / "python"
    if local_env.exists():
        return local_env.resolve()

    raise click.ClickException(
        "Kokoro backend requested, but no helper runtime was found.\n"
        f"Set {DEFAULT_KOKORO_PYTHON_ENV}, or create {local_env}."
    )


def _run_kokoro_bridge(args: list[str]) -> str:
    """Run the Kokoro helper script and return stdout."""
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown Kokoro error"
        raise click.ClickException(stderr)
    return result.stdout.strip()


def _list_kokoro_voices(kokoro_python: Path) -> list[str]:
    """Return published Kokoro voices from the helper runtime."""
    output = _run_kokoro_bridge(
        [
            str(kokoro_python),
            str(REPO_ROOT / "src" / "three_b1b" / "kokoro_bridge.py"),
            "--list-voices",
        ]
    )
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise click.ClickException("Could not parse Kokoro voice list.") from exc
    return list(payload.get("voices", []))


def _build_kokoro_job(
    chunks: list[NarrationChunk],
    output_dir: Path,
    speaker_name: str,
    lang_code: str,
    device: str,
    speech_speed: float,
) -> dict:
    """Serialize narration chunks for the Kokoro helper."""
    scenes: list[dict] = []
    for chunk in chunks:
        scene_entry = {
            "slug": chunk.slug,
            "text": chunk.text,
            "scene_output": str((output_dir / f"{chunk.slug}.wav").resolve()),
            "beats": [],
        }
        if chunk.beats:
            for beat in chunk.beats:
                scene_entry["beats"].append(
                    {
                        "beat_index": beat.beat_index,
                        "text": beat.text,
                        "target_duration": beat.target_duration,
                        "output_path": str(
                            (
                                output_dir
                                / "_beats"
                                / chunk.slug
                                / f"beat_{beat.beat_index:02d}.wav"
                            ).resolve()
                        ),
                    }
                )
        scenes.append(scene_entry)

    return {
        "device": device,
        "lang_code": lang_code,
        "speaker_name": speaker_name,
        "speed": speech_speed,
        "scenes": scenes,
    }


def _generate_with_kokoro(
    kokoro_python: Path,
    chunks: list[NarrationChunk],
    output_dir: Path,
    speaker_name: str,
    lang_code: str,
    device: str,
    speech_speed: float,
) -> str:
    """Generate narration with Kokoro via the external Python 3.11 runtime."""
    output_dir.mkdir(parents=True, exist_ok=True)
    job = _build_kokoro_job(
        chunks=chunks,
        output_dir=output_dir,
        speaker_name=speaker_name,
        lang_code=lang_code,
        device=device,
        speech_speed=speech_speed,
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="kokoro_job_",
        dir=output_dir,
        delete=False,
    ) as handle:
        json.dump(job, handle, indent=2)
        job_path = Path(handle.name)

    try:
        return _run_kokoro_bridge(
            [
                str(kokoro_python),
                str(REPO_ROOT / "src" / "three_b1b" / "kokoro_bridge.py"),
                "--job",
                str(job_path),
            ]
        )
    finally:
        job_path.unlink(missing_ok=True)


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--project-dir", "-d",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project directory for matching narration blocks to scene filenames.",
)
@click.option(
    "--source-mode",
    type=click.Choice(["auto", "scene-comments", "plan"]),
    default=DEFAULT_SOURCE_MODE,
    show_default=True,
    help="Prefer scene comments or plan narration when both are available.",
)
@click.option(
    "--backend",
    type=click.Choice(["vibevoice", "kokoro"]),
    default=DEFAULT_BACKEND,
    show_default=True,
    help="Speech backend to use.",
)
@click.option(
    "--model-path",
    default=DEFAULT_MODEL_PATH,
    show_default=True,
    help="VibeVoice-Realtime model identifier or local path.",
)
@click.option(
    "--speaker-name",
    default=DEFAULT_SPEAKER,
    show_default=True,
    help="Voice preset name for the selected backend.",
)
@click.option(
    "--voice-prompt",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Explicit VibeVoice .pt voice prompt file.",
)
@click.option(
    "--voices-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing VibeVoice .pt voice prompts.",
)
@click.option(
    "--kokoro-python",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Python 3.11 runtime used to execute the Kokoro helper.",
)
@click.option(
    "--kokoro-lang",
    default=DEFAULT_KOKORO_LANG,
    show_default=True,
    help="Kokoro language code, for example 'a' for US English.",
)
@click.option(
    "--speech-speed",
    default=DEFAULT_KOKORO_SPEED,
    show_default=True,
    type=float,
    help="Speech rate for Kokoro generation.",
)
@click.option(
    "--output-dir", "-o",
    default="voiceover_audio",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Directory for generated wav files.",
)
@click.option(
    "--device",
    type=click.Choice(["auto", "cuda", "mps", "cpu"]),
    default="auto",
    show_default=True,
    help="Inference device.",
)
@click.option(
    "--cfg-scale",
    default=1.5,
    show_default=True,
    type=float,
    help="Classifier-free guidance scale.",
)
@click.option(
    "--ddpm-steps",
    default=5,
    show_default=True,
    type=int,
    help="Number of DDPM inference steps.",
)
@click.option(
    "--list-voices",
    is_flag=True,
    help="List available voices for the selected backend and exit.",
)
def voiceover(
    source: Path,
    project_dir: Optional[Path],
    source_mode: str,
    backend: str,
    model_path: str,
    speaker_name: str,
    voice_prompt: Optional[Path],
    voices_dir: Optional[Path],
    kokoro_python: Optional[Path],
    kokoro_lang: str,
    speech_speed: float,
    output_dir: Path,
    device: str,
    cfg_scale: float,
    ddpm_steps: int,
    list_voices: bool,
) -> None:
    """Generate single-speaker narration audio from a plan or project.

    Extracts narration from # NARRATION: comments in scene files (preferred),
    narration sections in markdown plans, or storyboard concept lines.

    \b
    Backends:
      kokoro     Kokoro-82M (fast, 54 voices, voice mixing, recommended)
      vibevoice  VibeVoice-Realtime-0.5B (expressive, slower)

    \b
    Examples:
      3brown1blue voiceover videos/my_project
      3brown1blue voiceover videos/my_project --backend kokoro --speaker-name af_heart
      3brown1blue voiceover plan.md --backend vibevoice --speaker-name Carter
      3brown1blue voiceover videos/my_project --list-voices
    """
    if project_dir is not None:
        project_dir = _find_project_dir(project_dir)

    chunks, project_dir = _load_narration_chunks(source, project_dir, source_mode)
    if not chunks:
        click.echo(
            "No narration blocks found.\n"
            "Supported sources:\n"
            "  - project directories with # NARRATION: comments in scene_*.py\n"
            "  - markdown plans containing a '## Narration Script' section\n"
            "  - storyboard.md files with 'Narration concept:' lines"
        )
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"\nNarration source: {source}")
    if project_dir is not None:
        click.echo(f"Project dir:      {project_dir}")
    click.echo(f"Backend:          {backend}")
    click.echo(f"Chunks:           {len(chunks)}")
    click.echo(f"Source mode:      {source_mode}")
    click.echo(f"Output dir:       {output_dir}")

    generated: list[NarrationChunk] = []

    if backend == "kokoro":
        resolved_kokoro_python = _resolve_kokoro_python(kokoro_python)
        resolved_speaker = (
            DEFAULT_KOKORO_SPEAKER if speaker_name == DEFAULT_SPEAKER else speaker_name
        )

        if list_voices:
            voices = _list_kokoro_voices(resolved_kokoro_python)
            click.echo("\nAvailable Kokoro voices:\n")
            for name in voices:
                click.echo(f"  - {name}")
            return

        click.echo(f"Kokoro runtime:   {resolved_kokoro_python}")
        click.echo(f"Speaker:          {resolved_speaker}")
        click.echo(f"Kokoro lang:      {kokoro_lang}")
        click.echo(f"Speech speed:     {speech_speed:.2f}")

        generated = list(chunks)
        click.echo("\nGenerating Kokoro narration...")
        kokoro_summary = _generate_with_kokoro(
            kokoro_python=resolved_kokoro_python,
            chunks=generated,
            output_dir=output_dir,
            speaker_name=resolved_speaker,
            lang_code=kokoro_lang,
            device=device,
            speech_speed=speech_speed,
        )
        if kokoro_summary:
            click.echo(kokoro_summary)
        for chunk in generated:
            click.echo(f"Saved: {output_dir / f'{chunk.slug}.wav'}")
    else:
        resolved_voice_prompt, voice_registry = _resolve_voice_prompt(
            voice_prompt=voice_prompt,
            voices_dir=voices_dir,
            speaker_name=speaker_name,
        )

        if list_voices:
            if not voice_registry:
                click.echo(
                    "No voice registry available. Pass --voices-dir or set "
                    f"{DEFAULT_VOICE_DIR_ENV}."
                )
                sys.exit(1)
            click.echo("\nAvailable VibeVoice prompts:\n")
            for name in sorted(voice_registry):
                click.echo(f"  - {name}")
            return

        if resolved_voice_prompt is None:
            click.echo(
                "No voice prompt could be resolved.\n"
                "Pass --voice-prompt directly, or use --voices-dir / "
                f"{DEFAULT_VOICE_DIR_ENV} with --speaker-name."
            )
            sys.exit(1)

        click.echo(f"Voice prompt:     {resolved_voice_prompt}")
        torch_module, processor, model, resolved_device = _load_vibevoice_runtime(
            model_path=model_path,
            device=device,
            ddpm_steps=ddpm_steps,
        )
        click.echo(f"Device:           {resolved_device}")

        for chunk in chunks:
            if len(chunk.text.split()) < 4:
                click.echo(f"Skipping {chunk.slug}: narration too short for stable TTS.")
                continue

            output_path = output_dir / f"{chunk.slug}.wav"

            if chunk.beats:
                beat_dir = output_dir / "_beats" / chunk.slug
                beat_dir.mkdir(parents=True, exist_ok=True)
                generated_beats: list[NarrationBeat] = []
                beat_paths: list[Path] = []
                target_durations: list[float] = []

                click.echo(
                    f"\nGenerating {output_path.name} from {chunk.source_label} "
                    f"using {len(chunk.beats)} timed beat(s)..."
                )
                for beat in chunk.beats:
                    if len(beat.text.split()) < 4:
                        click.echo(
                            f"  Skipping beat {beat.beat_index}: narration too short "
                            "for stable TTS."
                        )
                        continue

                    beat_output = beat_dir / f"beat_{beat.beat_index:02d}.wav"
                    click.echo(
                        f"  Beat {beat.beat_index}: {len(beat.text.split())} words, "
                        f"target {beat.target_duration:.2f}s"
                    )
                    _generate_audio_file(
                        torch_module=torch_module,
                        processor=processor,
                        model=model,
                        device=resolved_device,
                        voice_prompt=resolved_voice_prompt,
                        text=beat.text,
                        output_path=beat_output,
                        cfg_scale=cfg_scale,
                    )
                    beat_paths.append(beat_output)
                    target_durations.append(beat.target_duration)
                    generated_beats.append(beat)

                if not generated_beats:
                    click.echo(
                        f"Skipping {chunk.slug}: no stable narration beats generated."
                    )
                    continue

                _concat_wavs(beat_paths, output_path, target_durations)
                generated.append(
                    NarrationChunk(
                        slug=chunk.slug,
                        text=chunk.text,
                        source_label=chunk.source_label,
                        beats=generated_beats,
                    )
                )
                click.echo(f"Saved: {output_path}")
                continue

            click.echo(
                f"\nGenerating {output_path.name} "
                f"from {chunk.source_label} ({len(chunk.text.split())} words)..."
            )
            _generate_audio_file(
                torch_module=torch_module,
                processor=processor,
                model=model,
                device=resolved_device,
                voice_prompt=resolved_voice_prompt,
                text=chunk.text,
                output_path=output_path,
                cfg_scale=cfg_scale,
            )
            generated.append(chunk)
            click.echo(f"Saved: {output_path}")

    manifest_md, manifest_json = _write_manifests(output_dir, generated)
    click.echo(f"\nManifest: {manifest_md}")
    click.echo(f"JSON manifest: {manifest_json}")
    click.echo("Done!")

"""voiceover command: generate single-speaker narration audio with VibeVoice."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click

from .edit_scene import _discover_scenes, _find_project_dir

DEFAULT_MODEL_PATH = "microsoft/VibeVoice-Realtime-0.5B"
DEFAULT_SPEAKER = "Carter"
DEFAULT_VOICE_DIR_ENV = "VIBEVOICE_VOICES_DIR"

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
class NarrationChunk:
    """A single narration block destined for one output audio file."""

    slug: str
    text: str
    source_label: str


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


def _chunks_from_scene_comments(project_dir: Path) -> list[NarrationChunk]:
    """Build narration chunks from scene-level NARRATION comments."""
    chunks: list[NarrationChunk] = []
    for scene in _discover_scenes(project_dir):
        lines = _extract_scene_comment_narration(scene["file"])
        if not lines:
            continue
        text = _normalize_for_tts(" ".join(lines))
        if text:
            chunks.append(
                NarrationChunk(
                    slug=scene["file"].stem,
                    text=text,
                    source_label=scene["file"].name,
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

    if source.suffix == ".py":
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


def _write_manifest(output_dir: Path, chunks: list[NarrationChunk]) -> Path:
    """Write a simple markdown manifest of generated files."""
    manifest = output_dir / "manifest.md"
    lines = [
        "# Voiceover Manifest",
        "",
    ]
    for chunk in chunks:
        lines.append(f"- `{chunk.slug}.wav`: {chunk.source_label}")
    manifest.write_text("\n".join(lines) + "\n")
    return manifest


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--project-dir", "-d",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project directory for matching narration blocks to scene filenames.",
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
    help="Voice preset name to resolve inside --voices-dir.",
)
@click.option(
    "--voice-prompt",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Explicit .pt voice prompt file.",
)
@click.option(
    "--voices-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing VibeVoice .pt voice prompts.",
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
    help="List available voice prompts from --voices-dir and exit.",
)
def voiceover(
    source: Path,
    project_dir: Optional[Path],
    model_path: str,
    speaker_name: str,
    voice_prompt: Optional[Path],
    voices_dir: Optional[Path],
    output_dir: Path,
    device: str,
    cfg_scale: float,
    ddpm_steps: int,
    list_voices: bool,
) -> None:
    """Generate single-speaker narration audio from a plan or project."""
    if project_dir is not None:
        project_dir = _find_project_dir(project_dir)

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

    chunks, project_dir = _load_narration_chunks(source, project_dir)
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
    click.echo(f"Chunks:           {len(chunks)}")
    click.echo(f"Voice prompt:     {resolved_voice_prompt}")
    click.echo(f"Output dir:       {output_dir}")

    torch_module, processor, model, resolved_device = _load_vibevoice_runtime(
        model_path=model_path,
        device=device,
        ddpm_steps=ddpm_steps,
    )
    click.echo(f"Device:           {resolved_device}")

    generated: list[NarrationChunk] = []
    for chunk in chunks:
        if len(chunk.text.split()) < 4:
            click.echo(f"Skipping {chunk.slug}: narration too short for stable TTS.")
            continue

        output_path = output_dir / f"{chunk.slug}.wav"
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

    manifest = _write_manifest(output_dir, generated)
    click.echo(f"\nManifest: {manifest}")
    click.echo("Done!")

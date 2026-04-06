"""Standalone Kokoro helper executed by a Python 3.11 runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    np = None  # type: ignore[assignment]
    sf = None  # type: ignore[assignment]

KOKORO_VOICES = (
    "af_alloy",
    "af_aoede",
    "af_bella",
    "af_heart",
    "af_jessica",
    "af_kore",
    "af_nicole",
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",
    "am_echo",
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
    "pf_dora",
    "pm_alex",
    "pm_santa",
    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
)


def _resolve_device(device: str) -> str:
    """Resolve a Kokoro device name."""
    import torch

    if device != "auto":
        return device
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _list_voices() -> list[str]:
    """Return published Kokoro voice names, with a static fallback."""
    try:
        from huggingface_hub import list_repo_files

        files = list_repo_files("hexgrad/Kokoro-82M")
        return sorted(
            file_path.split("/")[-1][:-3]
            for file_path in files
            if file_path.startswith("voices/") and file_path.endswith(".pt")
        )
    except Exception:
        return list(KOKORO_VOICES)


def _synthesize_text(pipe, text: str, voice: str, speed: float) -> np.ndarray:
    """Run Kokoro over one narration string and return mono audio."""
    pieces: list[np.ndarray] = []
    for result in pipe(text, voice=voice, speed=speed, split_pattern=None):
        if result.audio is None:
            continue
        pieces.append(result.audio.detach().cpu().numpy())
    if not pieces:
        raise RuntimeError(f"No audio generated for text: {text[:80]!r}")
    return np.concatenate(pieces).astype(np.float32, copy=False)


def _write_audio(path: Path, audio: np.ndarray, sample_rate: int = 24000) -> None:
    """Write one mono WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sample_rate)


def _concat_scene_audio(beats: list[dict[str, Any]], sample_rate: int = 24000) -> np.ndarray:
    """Concatenate beat audio, padding short beats with silence."""
    pieces: list[np.ndarray] = []
    for beat in beats:
        beat_path = Path(beat["output_path"])
        data, sr = sf.read(beat_path)
        if sr != sample_rate:
            raise RuntimeError(
                f"Unexpected sample rate for {beat_path.name}: {sr} != {sample_rate}"
            )
        if getattr(data, "ndim", 1) > 1:
            data = data[:, 0]
        target_seconds = float(beat.get("target_duration", 0.0) or 0.0)
        target_samples = int(round(max(target_seconds, 0.0) * sample_rate))
        if target_samples > len(data):
            pad = np.zeros(target_samples - len(data), dtype=data.dtype)
            data = np.concatenate([data, pad])
        pieces.append(data.astype(np.float32, copy=False))
    if not pieces:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(pieces)


def _run_job(job: dict[str, Any]) -> dict[str, Any]:
    """Generate Kokoro narration from a serialized job description."""
    from kokoro import KPipeline

    device = _resolve_device(str(job.get("device", "auto")))
    lang_code = str(job.get("lang_code", "a"))
    speaker_name = str(job.get("speaker_name", "af_bella,af_sarah"))
    speed = float(job.get("speed", 1.15))

    pipeline = KPipeline(lang_code=lang_code, device=device)
    scenes = job.get("scenes", [])

    for scene in scenes:
        beats = scene.get("beats") or []
        scene_output = Path(scene["scene_output"])
        if beats:
            for beat in beats:
                audio = _synthesize_text(
                    pipe=pipeline,
                    text=str(beat["text"]),
                    voice=speaker_name,
                    speed=speed,
                )
                _write_audio(Path(beat["output_path"]), audio)
            _write_audio(scene_output, _concat_scene_audio(beats))
            continue

        audio = _synthesize_text(
            pipe=pipeline,
            text=str(scene["text"]),
            voice=speaker_name,
            speed=speed,
        )
        _write_audio(scene_output, audio)

    return {
        "device": device,
        "lang_code": lang_code,
        "speaker_name": speaker_name,
        "speed": speed,
        "scene_count": len(scenes),
    }


def main() -> int:
    """CLI entrypoint for Kokoro narration generation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=Path, default=None)
    parser.add_argument("--list-voices", action="store_true")
    args = parser.parse_args()

    if args.list_voices:
        print(json.dumps({"voices": _list_voices()}, indent=2))
        return 0

    if args.job is None:
        parser.error("--job is required unless --list-voices is used")

    job = json.loads(args.job.read_text())
    result = _run_job(job)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

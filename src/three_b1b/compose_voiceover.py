"""compose-voiceover command: mux scene audio onto rendered scene videos."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import click

from .edit_scene import _discover_scenes, _find_project_dir

QUALITY_DIRS = {
    "l": "480p15",
    "m": "720p30",
    "h": "1080p60",
    "k": "2160p60",
}


def _audio_fit_factor(
    audio_duration: float,
    target_duration: float,
    audio_fit: str,
    max_atempo: float,
) -> float:
    """Return an ffmpeg atempo factor for fitting narration to visuals."""
    if audio_fit == "extend":
        return 1.0
    if target_duration <= 0 or audio_duration <= target_duration:
        return 1.0
    if audio_fit not in {"atempo", "hybrid"}:
        return 1.0
    return min(audio_duration / target_duration, max(max_atempo, 1.0), 2.0)


def _resolve_relative(base: Path, value: Path) -> Path:
    """Resolve a possibly relative path against the project directory."""
    if value.is_absolute():
        return value
    return (base / value).resolve()


def _require_ffmpeg() -> None:
    """Ensure ffmpeg is available."""
    if shutil.which("ffmpeg") is None:
        raise click.ClickException("ffmpeg is required for compose-voiceover.")
    if shutil.which("ffprobe") is None:
        raise click.ClickException("ffprobe is required for compose-voiceover.")


def _find_rendered_video(project_dir: Path, scene: dict, quality_dir: str) -> Optional[Path]:
    """Return the rendered MP4 for a scene at a given quality."""
    for class_name in scene["classes"]:
        candidate = (
            project_dir
            / "media"
            / "videos"
            / scene["file"].stem
            / quality_dir
            / f"{class_name}.mp4"
        )
        if candidate.exists():
            return candidate
    return None


def _run_ffmpeg(cmd: list[str]) -> None:
    """Run ffmpeg and surface a concise error on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "unknown ffmpeg error"
        raise click.ClickException(stderr.splitlines()[-1])


def _probe_duration(path: Path) -> float:
    """Return media duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(f"ffprobe failed for {path.name}")
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise click.ClickException(f"Could not parse duration for {path.name}") from exc


def _load_manifest(audio_dir: Path) -> dict:
    """Load voiceover JSON manifest when available."""
    manifest_path = audio_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid manifest.json in {audio_dir}") from exc


def _mux_scene_video(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    audio_fit: str,
    max_atempo: float,
) -> None:
    """Attach scene-level narration WAV to a rendered scene MP4."""
    video_duration = _probe_duration(video_path)
    audio_duration = _probe_duration(audio_path)
    atempo = _audio_fit_factor(audio_duration, video_duration, audio_fit, max_atempo)
    adjusted_audio_duration = audio_duration / atempo
    final_duration = max(video_duration, adjusted_audio_duration)
    cmd = ["ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path)]
    video_filters: list[str] = []
    audio_filters: list[str] = []

    if final_duration > video_duration:
        pad_seconds = final_duration - video_duration + 0.05
        video_filters.append(f"tpad=stop_mode=clone:stop_duration={pad_seconds:.3f}")
    if atempo > 1.001:
        audio_filters.append(f"atempo={atempo:.3f}")
    if adjusted_audio_duration < final_duration:
        audio_filters.append("apad")

    if video_filters:
        cmd.extend(["-vf", ",".join(video_filters)])
    if audio_filters:
        cmd.extend(["-af", ",".join(audio_filters)])

    cmd.extend(
        [
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{final_duration:.3f}",
            str(output_path),
        ]
    )
    _run_ffmpeg(cmd)


def _mux_beat_segment(
    video_path: Path,
    audio_path: Path,
    start_time: float,
    target_duration: float,
    output_path: Path,
    audio_fit: str,
    max_atempo: float,
) -> None:
    """Mux one beat of narration onto a matching video slice."""
    audio_duration = _probe_duration(audio_path)
    atempo = _audio_fit_factor(audio_duration, target_duration, audio_fit, max_atempo)
    adjusted_audio_duration = audio_duration / atempo
    final_duration = max(target_duration, adjusted_audio_duration)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start_time:.3f}",
        "-t",
        f"{target_duration:.3f}",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
    ]
    video_filters: list[str] = []
    audio_filters: list[str] = []

    if final_duration > target_duration:
        pad_seconds = final_duration - target_duration + 0.05
        video_filters.append(f"tpad=stop_mode=clone:stop_duration={pad_seconds:.3f}")

    if atempo > 1.001:
        audio_filters.append(f"atempo={atempo:.3f}")
    if adjusted_audio_duration < final_duration:
        audio_filters.append("apad")

    if video_filters:
        cmd.extend(["-vf", ",".join(video_filters)])
    if audio_filters:
        cmd.extend(["-af", ",".join(audio_filters)])

    cmd.extend(
        [
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{final_duration:.3f}",
            str(output_path),
        ]
    )
    _run_ffmpeg(cmd)


def _concat_videos(video_paths: list[Path], output_path: Path) -> None:
    """Concatenate narrated scene MP4s into one final MP4."""
    concat_file = output_path.parent / "concat_list.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve()}'\n" for path in video_paths)
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output_path),
    ]
    _run_ffmpeg(cmd)


def _compose_scene_from_beats(
    project_dir: Path,
    audio_dir: Path,
    video_path: Path,
    scene_entry: dict,
    output_path: Path,
    audio_fit: str,
    max_atempo: float,
) -> None:
    """Compose one scene from beat-aligned narration files."""
    segment_dir = output_path.parent / "_segments" / scene_entry["slug"]
    segment_dir.mkdir(parents=True, exist_ok=True)

    start_time = 0.0
    segment_paths: list[Path] = []
    for beat in scene_entry.get("beats", []):
        audio_rel = beat.get("audio", "")
        if not audio_rel:
            continue
        audio_path = audio_dir / audio_rel
        if not audio_path.exists():
            raise click.ClickException(f"Missing beat audio: {audio_path}")

        beat_output = segment_dir / f"beat_{int(beat['beat_index']):02d}.mp4"
        _mux_beat_segment(
            video_path=video_path,
            audio_path=audio_path,
            start_time=start_time,
            target_duration=float(beat.get("target_duration", 0.0)),
            output_path=beat_output,
            audio_fit=audio_fit,
            max_atempo=max_atempo,
        )
        segment_paths.append(beat_output)
        start_time += float(beat.get("target_duration", 0.0))

    if not segment_paths:
        raise click.ClickException(f"No beat segments created for {scene_entry['slug']}")

    _concat_videos(segment_paths, output_path)


@click.command(name="compose-voiceover")
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--audio-dir",
    "-a",
    default=Path("voiceover_audio"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory containing per-scene WAV files.",
)
@click.option(
    "--quality",
    "-q",
    type=click.Choice(["l", "m", "h", "k"]),
    default="l",
    show_default=True,
    help="Rendered scene quality to use.",
)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(path_type=Path),
    help="Directory for narrated per-scene MP4 files.",
)
@click.option(
    "--final-output",
    default=None,
    type=click.Path(path_type=Path),
    help="Optional explicit path for the final narrated MP4.",
)
@click.option(
    "--audio-fit",
    type=click.Choice(["extend", "atempo", "hybrid"]),
    default="hybrid",
    show_default=True,
    help="Whether to extend visuals, speed up audio, or do both conservatively.",
)
@click.option(
    "--max-atempo",
    default=1.35,
    show_default=True,
    type=float,
    help="Maximum ffmpeg atempo factor used when fitting narration.",
)
def compose_voiceover(
    project_dir: Path,
    audio_dir: Path,
    quality: str,
    output_dir: Optional[Path],
    final_output: Optional[Path],
    audio_fit: str,
    max_atempo: float,
) -> None:
    """Mux narration audio onto rendered Manim videos.

    Reads scene WAVs from the audio directory, matches them to rendered MP4s
    by scene slug, adjusts tempo if needed, and concatenates into one video.

    \b
    Audio-fit modes:
      hybrid   Conservative tempo adjustment (default, max 1.35x)
      atempo   Speed up audio to fit video (max 2x)
      extend   Pad video with last frame to match audio length

    \b
    Examples:
      3brown1blue compose-voiceover videos/my_project
      3brown1blue compose-voiceover videos/my_project -a voiceover_audio_best -q h
      3brown1blue compose-voiceover videos/my_project --audio-fit extend
    """
    _require_ffmpeg()
    project_dir = _find_project_dir(project_dir)
    audio_dir = _resolve_relative(project_dir, audio_dir)
    if not audio_dir.exists():
        raise click.ClickException(f"Audio directory not found: {audio_dir}")
    if output_dir is None:
        output_dir = project_dir / "voiceover_video"
    else:
        output_dir = _resolve_relative(project_dir, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if final_output is None:
        final_output = project_dir / f"{project_dir.name}_narrated_{QUALITY_DIRS[quality]}.mp4"
    else:
        final_output = _resolve_relative(project_dir, final_output)
        final_output.parent.mkdir(parents=True, exist_ok=True)

    manifest = _load_manifest(audio_dir)
    manifest_by_slug = {
        scene["slug"]: scene for scene in manifest.get("scenes", [])
    }

    quality_dir = QUALITY_DIRS[quality]
    scenes = _discover_scenes(project_dir)
    if not scenes:
        raise click.ClickException(f"No scene_*.py files found in {project_dir}")

    narrated_paths: list[Path] = []
    missing: list[str] = []
    for scene in scenes:
        stem = scene["file"].stem
        audio_path = audio_dir / f"{stem}.wav"
        video_path = _find_rendered_video(project_dir, scene, quality_dir)
        if not audio_path.exists():
            missing.append(f"missing audio: {audio_path}")
            continue
        if video_path is None:
            missing.append(f"missing video: {stem} ({quality_dir})")
            continue

        output_path = output_dir / f"{stem}.mp4"
        scene_entry = manifest_by_slug.get(stem, {})
        if scene_entry.get("beats"):
            click.echo(f"Composing {stem} from {len(scene_entry['beats'])} beat(s)...")
            _compose_scene_from_beats(
                project_dir=project_dir,
                audio_dir=audio_dir,
                video_path=video_path,
                scene_entry=scene_entry,
                output_path=output_path,
                audio_fit=audio_fit,
                max_atempo=max_atempo,
            )
        else:
            click.echo(f"Muxing {stem}...")
            _mux_scene_video(
                video_path=video_path,
                audio_path=audio_path,
                output_path=output_path,
                audio_fit=audio_fit,
                max_atempo=max_atempo,
            )
        narrated_paths.append(output_path)

    if missing:
        click.echo("\nSkipped inputs:")
        for item in missing:
            click.echo(f"  - {item}")

    if not narrated_paths:
        raise click.ClickException("No narrated scene videos were created.")

    click.echo(f"\nConcatenating {len(narrated_paths)} narrated scenes...")
    _concat_videos(narrated_paths, final_output)
    click.echo(f"Final narrated video: {final_output}")

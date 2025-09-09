import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chapter:
    index: int
    start_time: float
    end_time: Optional[float]
    title: str


def ensure_tool_available(tool_name: str) -> None:
    if shutil.which(tool_name) is None:
        raise FileNotFoundError(f"Required tool not found in PATH: {tool_name}")


def sanitize_filename(name: str) -> str:
    if not name:
        return "chapter"
    name = name.strip()
    name = re.sub(r"[\s/\\:]+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]", "", name)
    return name or "chapter"


def run_command(command: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )


def probe_chapters(aax_path: str, activation_bytes: str) -> List[Chapter]:
    ensure_tool_available("ffprobe")
    if not os.path.isfile(aax_path):
        raise FileNotFoundError(f"Input file not found: {aax_path}")

    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-activation_bytes",
        activation_bytes,
        "-print_format",
        "json",
        "-show_chapters",
        "-i",
        aax_path,
    ]
    result = run_command(probe_cmd)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Failed to parse ffprobe JSON output") from exc

    chapters_raw = data.get("chapters", [])
    chapters: List[Chapter] = []
    for i, ch in enumerate(chapters_raw):
        start_time = float(ch.get("start_time", 0.0))
        end_time = float(ch.get("end_time")) if ch.get("end_time") is not None else None
        title = ch.get("tags", {}).get("title") or f"Chapter_{i+1:03d}"
        chapters.append(Chapter(index=i, start_time=start_time, end_time=end_time, title=title))

    # If no chapters, create a single pseudo-chapter covering the whole file
    if not chapters:
        chapters.append(Chapter(index=0, start_time=0.0, end_time=None, title="Chapter_001"))

    return chapters


def convert_chapter_to_mp3(
    aax_path: str,
    activation_bytes: str,
    chapter: Chapter,
    output_directory: str,
    audio_quality: str = "2",
) -> str:
    ensure_tool_available("ffmpeg")
    os.makedirs(output_directory, exist_ok=True)

    safe_title = sanitize_filename(chapter.title)
    output_filename = f"{chapter.index+1:03d}_{safe_title}.mp3"
    output_path = os.path.join(output_directory, output_filename)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-activation_bytes",
        activation_bytes,
        "-i",
        aax_path,
        "-vn",
        "-sn",
        "-dn",
        "-map",
        "a:0",
        "-ss",
        str(chapter.start_time),
    ]
    if chapter.end_time is not None:
        cmd += ["-to", str(chapter.end_time)]

    cmd += [
        "-map_metadata",
        "-1",
        "-metadata",
        f"title={chapter.title}",
        "-c:a",
        "libmp3lame",
        "-q:a",
        audio_quality,
        output_path,
    ]

    result = run_command(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for chapter {chapter.index+1}: {result.stderr.strip()}")

    return output_path


def convert_aax_to_mp3_by_chapter(
    aax_path: str,
    activation_bytes: str,
    output_directory: str,
    audio_quality: str = "2",
) -> List[str]:
    chapters = probe_chapters(aax_path, activation_bytes)
    output_files: List[str] = []
    for chapter in chapters:
        out = convert_chapter_to_mp3(
            aax_path=aax_path,
            activation_bytes=activation_bytes,
            chapter=chapter,
            output_directory=output_directory,
            audio_quality=audio_quality,
        )
        output_files.append(out)
    return output_files


def create_zip_from_directory(source_directory: str, zip_path: str) -> str:
    base_dir = os.path.abspath(source_directory)
    zip_abs = os.path.abspath(zip_path)
    if os.path.exists(zip_abs):
        os.remove(zip_abs)
    shutil.make_archive(zip_abs.replace(".zip", ""), "zip", base_dir)
    return zip_abs

#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from lib.converter import (
    convert_aax_to_mp3_by_chapter,
    create_zip_from_directory,
)

load_dotenv()


def prompt_if_missing(value: str, prompt: str, default: str = "") -> str:
    if value:
        return value
    entered = input(f"{prompt}{f' [{default}]' if default else ''} ").strip()
    return entered or default


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Audible AAX to per-chapter MP3s.")
    parser.add_argument("aax", nargs="?", help="Path to input .aax file")
    parser.add_argument("activation_bytes", nargs="?", help="16-hex activation bytes")
    parser.add_argument("--out", default=None, help="Output directory (default: $OUTPUT_DIR or ./output/<basename>_chapters)")
    parser.add_argument("--quality", default=os.environ.get("MP3_QUALITY", "2"), help="MP3 VBR quality (0=best, 9=worst; default: 2)")

    args = parser.parse_args()

    aax_path = prompt_if_missing(args.aax, "Path to .aax file:")
    env_key = os.environ.get("ACTIVATION_BYTES", "")
    activation_bytes = prompt_if_missing(args.activation_bytes, "Activation bytes (16 hex):", env_key)

    if not os.path.isfile(aax_path):
        print(f"Input file not found: {aax_path}", file=sys.stderr)
        return 1

    if not (len(activation_bytes) == 8 and all(c in "0123456789abcdefABCDEF" for c in activation_bytes)):
        print("Activation bytes must be 8 hex characters.", file=sys.stderr)
        return 1

    base_name = Path(aax_path).stem
    default_out = os.environ.get("OUTPUT_DIR") or os.path.join("output", f"{base_name}_chapters_mp3")
    output_dir = args.out or default_out
    os.makedirs(output_dir, exist_ok=True)

    print("Extracting chapters and converting to MP3...")
    files = convert_aax_to_mp3_by_chapter(
        aax_path=aax_path,
        activation_bytes=activation_bytes,
        output_directory=output_dir,
        audio_quality=args.quality,
    )
    print(f"Created {len(files)} MP3 files in: {output_dir}")

    zip_name = os.path.join("output", f"{base_name}_chapters_mp3.zip")
    os.makedirs(os.path.dirname(zip_name), exist_ok=True)
    create_zip_from_directory(output_dir, zip_name)
    print(f"ZIP created: {zip_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

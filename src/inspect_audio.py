"""Inspect the audio files of the dataset and write a data inventory.

For every audio file under <audio-root>/<genre>/<file> the script records
the technical properties (sample rate, channels, bit depth, duration, size)
and a SHA-256 hash, then checks them against the GTZAN specification
(22050 Hz, mono, 16-bit, about 30 seconds).

Usage:
    python src/inspect_audio.py --audio-root path/to/data/genres_original
"""

import argparse
import csv
import hashlib
import json
import re
import wave
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg"}
NAME_PATTERN = re.compile(r"^(?P<genre>[a-z]+)\.(?P<index>\d{5})\.wav$")

EXPECTED = {"sample_rate": 22050, "channels": 1, "bit_depth": 16, "duration_s": 30.0}
DURATION_TOLERANCE_S = 0.5

COLUMNS = [
    "file_name", "genre", "track_index", "format", "sample_rate", "channels",
    "bit_depth", "n_frames", "duration_s", "size_bytes", "sha256", "issues",
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_file(path, genre):
    row = {
        "file_name": path.name,
        "genre": genre,
        "track_index": "",
        "format": path.suffix.lower().lstrip("."),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    issues = []

    match = NAME_PATTERN.match(path.name)
    if match:
        row["track_index"] = int(match["index"])
        if match["genre"] != genre:
            issues.append("name_genre_differs_from_folder")
    else:
        issues.append("unexpected_file_name")

    if row["format"] != "wav":
        issues.append("not_wav_properties_unchecked")
        row["issues"] = ";".join(issues)
        return row

    try:
        with wave.open(str(path), "rb") as audio:
            row["sample_rate"] = audio.getframerate()
            row["channels"] = audio.getnchannels()
            row["bit_depth"] = audio.getsampwidth() * 8
            row["n_frames"] = audio.getnframes()
            row["duration_s"] = round(row["n_frames"] / row["sample_rate"], 3)
    except (wave.Error, EOFError, OSError):
        issues.append("unreadable_wav")
        row["issues"] = ";".join(issues)
        return row

    for key in ("sample_rate", "channels", "bit_depth"):
        if row[key] != EXPECTED[key]:
            issues.append(f"{key}_differs")
    if abs(row["duration_s"] - EXPECTED["duration_s"]) > DURATION_TOLERANCE_S:
        issues.append("duration_differs")

    row["issues"] = ";".join(issues)
    return row


def inspect(audio_root):
    rows = []
    for genre_dir in sorted(p for p in audio_root.iterdir() if p.is_dir()):
        for path in sorted(genre_dir.iterdir()):
            if path.suffix.lower() in AUDIO_EXTENSIONS:
                rows.append(inspect_file(path, genre_dir.name))

    hash_counts = Counter(r["sha256"] for r in rows)
    for r in rows:
        if hash_counts[r["sha256"]] > 1:
            r["issues"] = ";".join(filter(None, [r["issues"], "duplicate_content"]))
    return rows


def summarize(rows):
    def distinct(key):
        return sorted({r[key] for r in rows if r.get(key) not in (None, "")})

    durations = [r["duration_s"] for r in rows if r.get("duration_s")]
    return {
        "total_files": len(rows),
        "genres": dict(sorted(Counter(r["genre"] for r in rows).items())),
        "formats": distinct("format"),
        "sample_rates": distinct("sample_rate"),
        "channels": distinct("channels"),
        "bit_depths": distinct("bit_depth"),
        "duration_s": {
            "min": min(durations) if durations else None,
            "max": max(durations) if durations else None,
            "total": round(sum(durations), 3),
        },
        "total_size_bytes": sum(r["size_bytes"] for r in rows),
        "files_with_issues": [
            {"file_name": r["file_name"], "issues": r["issues"]} for r in rows if r["issues"]
        ],
        "expected_spec": EXPECTED,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect dataset audio files")
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data")
    args = parser.parse_args()

    if not args.audio_root.is_dir():
        parser.error(f"audio folder not found: {args.audio_root}")

    rows = inspect(args.audio_root)
    summary = summarize(rows)

    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "audio_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "audio_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Files: {summary['total_files']}  Genres: {summary['genres']}")
    print(f"Sample rates: {summary['sample_rates']}  Channels: {summary['channels']}  "
          f"Bit depths: {summary['bit_depths']}")
    print(f"Duration min/max: {summary['duration_s']['min']}/{summary['duration_s']['max']} s")
    print(f"Files with issues: {len(summary['files_with_issues'])}")
    print(f"Saved audio_inventory.csv and audio_summary.json in {args.output}")


if __name__ == "__main__":
    main()

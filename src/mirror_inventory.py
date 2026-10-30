"""List the files in the Hugging Face mirror of GTZAN used by the group.

Downloads only the file listing (not the audio) from the Hugging Face API,
then writes one row per audio file and a per-genre summary that also shows
which of the original 100 track indices (00000-00099) are missing.

Usage:
    python src/mirror_inventory.py
"""

import argparse
import csv
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET = "storylinez/gtzan-music-genre-dataset"
TREE_URL = f"https://huggingface.co/api/datasets/{DATASET}/tree/main?recursive=true"
NAME_PATTERN = re.compile(r"^(?P<genre>[a-z]+)\.(?P<index>\d{5})\.wav$")
TRACKS_PER_GENRE = 100


def fetch_tree(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.load(response)


def build_inventory(tree):
    rows = []
    for item in tree:
        if item.get("type") != "file" or not item["path"].endswith(".wav"):
            continue
        genre, name = item["path"].split("/", 1)
        match = NAME_PATTERN.match(name)
        rows.append({
            "file_name": name,
            "genre": genre,
            "track_index": int(match["index"]) if match else "",
            "size_bytes": item.get("size", ""),
            "path_in_mirror": item["path"],
        })
    rows.sort(key=lambda r: (r["genre"], r["file_name"]))
    return rows


def summarize(rows):
    by_genre = defaultdict(set)
    for r in rows:
        if r["track_index"] != "":
            by_genre[r["genre"]].add(r["track_index"])
    genres = {}
    for genre in sorted(by_genre):
        present = by_genre[genre]
        missing = [i for i in range(TRACKS_PER_GENRE) if i not in present]
        genres[genre] = {
            "present": len(present),
            "missing": len(missing),
            "missing_indices": [f"{i:05d}" for i in missing],
        }
    return {
        "dataset": DATASET,
        "total_files": len(rows),
        "expected_files": TRACKS_PER_GENRE * len(genres),
        "total_size_bytes": sum(r["size_bytes"] for r in rows if r["size_bytes"] != ""),
        "genres": genres,
    }


def main():
    parser = argparse.ArgumentParser(description="Inventory of the GTZAN mirror")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data")
    args = parser.parse_args()

    rows = build_inventory(fetch_tree(TREE_URL))
    summary = summarize(rows)

    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "mirror_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "mirror_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Mirror files: {summary['total_files']} of {summary['expected_files']}")
    for genre, info in summary["genres"].items():
        print(f"  {genre:<10} present={info['present']:3d}  missing={info['missing']:3d}")
    print(f"Saved mirror_inventory.csv and mirror_summary.json in {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import argparse
import json
import lzma
from pathlib import Path
from typing import Any

VARIANT_MAP = {
  "衆": "眾",
}


def load_json(path: Path) -> Any:
  if path.suffix == ".xz":
    with lzma.open(path, "rt", encoding="utf-8") as handle:
      return json.load(handle)

  return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)

  if path.suffix == ".xz":
    with lzma.open(path, "wt", encoding="utf-8") as handle:
      json.dump(payload, handle, ensure_ascii=False)
      handle.write("\n")
    return

  path.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )


def build_corpus(chapters: list[str]) -> str:
  corpus = "\n".join(chapter.strip() for chapter in chapters)

  for source, target in VARIANT_MAP.items():
    corpus += "\n" + corpus.replace(source, target)

  return corpus


def filter_entries(entries: list[dict[str, Any]], corpus: str) -> list[dict[str, Any]]:
  kept: list[dict[str, Any]] = []

  for entry in entries:
    title = entry.get("title")

    if not isinstance(title, str) or not title:
      continue

    if title in corpus:
      kept.append(entry)

  return kept


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Create a MoeDict subset containing only entries that appear in the Dao De Jing.",
  )
  parser.add_argument(
    "--chapters",
    default="data/laozi.json",
    help="Path to the Dao De Jing chapter array JSON.",
  )
  parser.add_argument(
    "--input",
    default="moedict-data/dict-revised_bkup.json",
    help="Path to the MoeDict JSON or JSON.XZ file.",
  )
  parser.add_argument(
    "--output",
    default="data/moedict-laozi.json",
    help="Where to write the filtered dictionary JSON or JSON.XZ file.",
  )
  return parser.parse_args()


def main() -> int:
  args = parse_args()
  chapters_path = Path(args.chapters)
  input_path = Path(args.input)
  output_path = Path(args.output)

  chapters = load_json(chapters_path)
  entries = load_json(input_path)

  if not isinstance(chapters, list) or not all(isinstance(item, str) for item in chapters):
    raise ValueError(f"{chapters_path} must be a JSON array of chapter strings.")

  if not isinstance(entries, list):
    raise ValueError(f"{input_path} must be a JSON array of dictionary entries.")

  corpus = build_corpus(chapters)
  filtered = filter_entries(entries, corpus)
  write_json(output_path, filtered)

  print(f"chapters: {len(chapters)}")
  print(f"entries_in: {len(entries)}")
  print(f"entries_out: {len(filtered)}")
  print(f"output: {output_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

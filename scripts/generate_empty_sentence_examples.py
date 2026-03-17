#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


SPLIT_RE = re.compile(r"[。！？；]")


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Generate an empty sentence-example JSON map from data/laozi.json.",
  )
  parser.add_argument(
    "--input",
    default="data/laozi.json",
    help="Path to the chapter JSON file.",
  )
  parser.add_argument(
    "--output",
    default="data/sentence-examples.json",
    help="Path to the output JSON file.",
  )
  return parser.parse_args()


def build_records(chapters: list[str]) -> list[dict[str, object]]:
  records: list[dict[str, object]] = []

  for chapter_index, chapter in enumerate(chapters, start=1):
    sentence_index = 0
    for sentence in SPLIT_RE.split(chapter.strip()):
      sentence = sentence.strip()
      if not sentence:
        continue
      sentence_index += 1
      records.append(
        {
          "chapter": chapter_index,
          "sentence_index": sentence_index,
          "sentence": sentence,
          "examples": [],
        }
      )

  return records


def main() -> int:
  args = parse_args()
  input_path = Path(args.input)
  output_path = Path(args.output)

  chapters = json.loads(input_path.read_text(encoding="utf-8"))
  if not isinstance(chapters, list) or not all(isinstance(item, str) for item in chapters):
    raise ValueError(f"{input_path} must be a JSON array of chapter strings.")

  payload = build_records(chapters)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )

  print(f"sentences: {len(payload)}")
  print(f"output: {output_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

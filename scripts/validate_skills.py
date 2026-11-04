"""Validate portable skill metadata and required instruction sections."""

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SECTIONS = (
    "When to use",
    "Prerequisites",
    "Inputs to gather",
    "Steps",
    "Verification",
    "Rollback",
    "Safety notes",
)


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return ["missing opening YAML frontmatter delimiter"], None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return ["missing closing YAML frontmatter delimiter"], None
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return ["invalid YAML frontmatter"], None
    if not isinstance(metadata, dict):
        return ["frontmatter must be a mapping"], None
    name = metadata.get("name")
    if (
        not isinstance(name, str)
        or not NAME.fullmatch(name)
        or len(name) > 64
        or name != path.parent.name
    ):
        errors.append("name must be lowercase-hyphenated, <=64 characters, and match folder")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a non-empty string")
    headings = set()
    fence = None
    for line in lines[end + 1 :]:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if (
                marker
                and marker.group(1)[0] == fence[0]
                and len(marker.group(1)) >= len(fence)
                and not marker.group(2).strip()
            ):
                fence = None
            continue
        if marker and (marker.group(1)[0] != "`" or "`" not in marker.group(2)):
            fence = marker.group(1)
        elif line.startswith("## "):
            headings.add(line[3:].strip())
    for section in SECTIONS:
        if section not in headings:
            errors.append(f"missing section: {section}")
    return errors, name if isinstance(name, str) else None


def main():
    paths = sorted((ROOT / "skills").rglob("SKILL.md"))
    if not paths:
        print("No skills found.", file=sys.stderr)
        return 1
    failed = False
    seen = set()
    for path in paths:
        try:
            errors, name = validate(path)
        except (OSError, UnicodeError):
            errors, name = ["cannot read UTF-8 skill file"], None
        if name is not None:
            if name in seen:
                errors.append("duplicate skill name")
            seen.add(name)
        for error in errors:
            print(f"{path.relative_to(ROOT)}: {error}", file=sys.stderr)
        failed = failed or bool(errors)
    if not failed:
        print(f"Validated {len(paths)} skills.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())

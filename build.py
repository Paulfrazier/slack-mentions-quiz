#!/usr/bin/env python3
"""Render dontuseathere from spec.json into the local "no-score" variant template.

This is a thin wrapper around fairpoint-kit/render.py: it reuses the kit's
validate() (the choice-sync invariant) and ISLAND regex, but injects the spec
into THIS folder's local template.html instead of the shared kit template.

Usage:  python3 build.py            # spec.json -> index.html (this dir)
Exit:   0 ok, 1 validation error, 2 IO/usage error.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent / "fairpoint-kit"
sys.path.insert(0, str(KIT))

try:
    from render import validate, ISLAND  # reuse kit validation + #site-config regex
except ImportError as e:
    print(f"error: could not import fairpoint-kit/render.py: {e}", file=sys.stderr)
    sys.exit(2)


def main():
    spec_path = HERE / "spec.json"
    template_path = HERE / "template.html"
    out_path = HERE / "index.html"

    try:
        spec = json.loads(spec_path.read_text())
        template = template_path.read_text()
    except (OSError, json.JSONDecodeError) as e:
        print(f"error reading inputs: {e}", file=sys.stderr)
        return 2

    errors = validate(spec)
    if errors:
        print(f"✗ {len(errors)} validation error(s) in {spec_path.name}:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if not ISLAND.search(template):
        print("error: could not find #site-config block in template.html", file=sys.stderr)
        return 2

    payload = json.dumps(spec, ensure_ascii=False, indent=2)
    rendered = ISLAND.sub(
        lambda m: m.group(1) + "\n" + payload + "\n  " + m.group(3),
        template,
        count=1,
    )
    out_path.write_text(rendered)
    print(f"✓ rendered {len(spec['scenarios'])} scenarios ({len(spec['choices'])} choices) → {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the CNC simulation files with LinuxCNC's rs274 interpreter."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "examples" / "cnc-simulation-test"
REPORT = ASSET_DIR / "linuxcnc-rs274-validation.txt"
MOVE_RE = re.compile(r"STRAIGHT_(FEED|TRAVERSE)\(([-0-9.]+), ([-0-9.]+), ([-0-9.]+),")


@dataclass(frozen=True)
class Expected:
    filename: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    feed_z_min: float
    retract_z_min: float


EXPECTED_FILES = [
    Expected("first-aircut-mm-safe-z5.ngc", 0.0, 120.0, 0.0, 80.0, 5.0, 15.0),
    Expected("faceted-star-air-sculpture-mm.ngc", 0.0, 122.308, 0.0, 114.496, 4.0, 26.0),
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def run_rs274(rs274: str, expected: Expected) -> tuple[str, list[tuple[str, float, float, float]]]:
    gcode = ASSET_DIR / expected.filename
    if not gcode.exists():
        fail(f"missing G-code file: {gcode}")

    completed = subprocess.run(
        [rs274, "-g", str(gcode)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        fail(completed.stderr.strip() or completed.stdout.strip() or f"rs274 failed for {expected.filename}")

    moves: list[tuple[str, float, float, float]] = []
    for match in MOVE_RE.finditer(completed.stdout):
        kind, x, y, z = match.groups()
        moves.append((kind, float(x), float(y), float(z)))

    if not moves:
        fail(f"rs274 produced no straight moves for {expected.filename}")

    return completed.stdout, moves


def summarize(expected: Expected, canonical: str, moves: list[tuple[str, float, float, float]]) -> list[str]:
    xs = [move[1] for move in moves]
    ys = [move[2] for move in moves]
    zs = [move[3] for move in moves]
    feed_zs = [move[3] for move in moves if move[0] == "FEED"]

    checks = [
        ("uses millimetres", "USE_LENGTH_UNITS(CANON_UNITS_MM)" in canonical, "G21 interpreted"),
        ("program ends", "PROGRAM_END()" in canonical, "M2 interpreted"),
        ("no spindle start", "START_SPINDLE" not in canonical, "no START_SPINDLE in canonical output"),
        ("x envelope", min(xs) >= expected.x_min and max(xs) <= expected.x_max, f"{min(xs):.3f}..{max(xs):.3f}"),
        ("y envelope", min(ys) >= expected.y_min and max(ys) <= expected.y_max, f"{min(ys):.3f}..{max(ys):.3f}"),
        ("feed z floor", min(feed_zs) >= expected.feed_z_min, f"min feed Z {min(feed_zs):.3f}"),
        ("safe retract present", max(zs) >= expected.retract_z_min, f"max Z {max(zs):.3f}"),
    ]

    lines = [
        f"File: {expected.filename}",
        f"- straight moves: {len(moves)}",
        f"- X range: {min(xs):.3f}..{max(xs):.3f}",
        f"- Y range: {min(ys):.3f}..{max(ys):.3f}",
        f"- Z range: {min(zs):.3f}..{max(zs):.3f}",
        "- checks:",
    ]
    for name, ok, detail in checks:
        marker = "PASS" if ok else "FAIL"
        lines.append(f"  - {marker}: {name} ({detail})")

    failed = [name for name, ok, _detail in checks if not ok]
    if failed:
        fail(f"{expected.filename}: {', '.join(failed)}")

    return lines


def main() -> None:
    rs274 = shutil.which("rs274")
    if not rs274:
        fail("LinuxCNC rs274 interpreter is not installed")

    report_lines = [
        "LinuxCNC rs274 validation for CNC simulation test files",
        "Status: PASS",
        "",
        "This is a parser/interpreter check, not a full GUI backplot or machine dry run.",
        "",
    ]

    for expected in EXPECTED_FILES:
        canonical, moves = run_rs274(rs274, expected)
        report_lines.extend(summarize(expected, canonical, moves))
        report_lines.append("")

    report_lines.extend(
        [
            "Next manual check:",
            "- Open each file in a LinuxCNC GUI simulator/backplot and confirm the visual path matches the SVG preview.",
            "",
        ]
    )
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(REPORT.relative_to(ROOT))
    print("Status: PASS")


if __name__ == "__main__":
    main()

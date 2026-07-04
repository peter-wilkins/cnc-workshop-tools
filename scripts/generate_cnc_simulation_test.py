#!/usr/bin/env python3
"""Generate conservative CNC simulation files and visual previews."""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples" / "cnc-simulation-test"


def format_xy(x: float, y: float) -> str:
    return f"X{x:.3f} Y{y:.3f}"


def format_xyz(x: float, y: float, z: float) -> str:
    return f"X{x:.3f} Y{y:.3f} Z{z:.3f}"


def circle_points(cx: float, cy: float, radius: float, segments: int = 72) -> list[tuple[float, float]]:
    return [
        (
            cx + math.cos((math.tau * i) / segments) * radius,
            cy + math.sin((math.tau * i) / segments) * radius,
        )
        for i in range(segments + 1)
    ]


def build_paths() -> list[list[tuple[float, float]]]:
    return [
        [(0, 0), (120, 0), (120, 80), (0, 80), (0, 0)],
        [(0, 0), (120, 80)],
        [(0, 80), (120, 0)],
        [(20, 20), (100, 20), (100, 60), (20, 60), (20, 20)],
        circle_points(60, 40, 18),
        [(44, 40), (76, 40)],
        [(60, 24), (60, 56)],
    ]


def star_points(cx: float, cy: float, outer: float, inner: float, points: int = 5) -> list[tuple[float, float]]:
    vertices: list[tuple[float, float]] = []
    for index in range(points * 2):
        radius = outer if index % 2 == 0 else inner
        angle = -math.pi / 2 + (math.tau * index) / (points * 2)
        vertices.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return vertices


def scale_from_center(
    path: list[tuple[float, float]],
    cx: float,
    cy: float,
    scale: float,
) -> list[tuple[float, float]]:
    return [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in path]


def build_star_paths() -> list[tuple[str, list[tuple[float, float, float]]]]:
    cx = 70.0
    cy = 70.0
    outline_xy = star_points(cx, cy, outer=55.0, inner=24.0)
    middle_xy = scale_from_center(outline_xy, cx, cy, 0.68)
    top_xy = scale_from_center(outline_xy, cx, cy, 0.32)

    paths: list[tuple[str, list[tuple[float, float, float]]]] = [
        ("Outer star outline at low air-cut height", [(x, y, 4.0) for x, y in outline_xy + [outline_xy[0]]]),
        ("Middle star outline at mid height", [(x, y, 10.0) for x, y in middle_xy + [middle_xy[0]]]),
        ("Top star outline at high height", [(x, y, 16.0) for x, y in top_xy + [top_xy[0]]]),
    ]

    center = (cx, cy, 22.0)
    for index, point in enumerate(outline_xy):
        next_point = outline_xy[(index + 1) % len(outline_xy)]
        z = 4.0 if index % 2 == 0 else 7.0
        next_z = 4.0 if (index + 1) % 2 == 0 else 7.0
        paths.append(
            (
                f"Faceted star triangle {index + 1}",
                [
                    center,
                    (point[0], point[1], z),
                    (next_point[0], next_point[1], next_z),
                    center,
                ],
            )
        )

    for point in outline_xy[::2]:
        paths.append(("High ridge to star point", [center, (point[0], point[1], 4.0)]))

    return paths


def write_gcode(paths: list[list[tuple[float, float]]]) -> Path:
    gcode = [
        "%",
        "(CNC workshop tools first simulation file)",
        "(Purpose: safe XY air-cut / simulator sanity check)",
        "(Units: millimetres. Coordinates fit inside 120 x 80 mm.)",
        "(No spindle command is included.)",
        "(Tool remains at Z5.000 for the drawing moves if work zero is the surface.)",
        "(For first real-machine use: verify in simulator, set Z zero safely, and run above stock.)",
        "G21 (millimetres)",
        "G90 (absolute coordinates)",
        "G17 (XY plane)",
        "G40 G49 G80 (cancel cutter comp, tool length comp, canned cycles)",
        "G54 (work coordinate system)",
        "G94 (feed per minute)",
        "F800.0",
        "G0 Z15.000",
    ]

    for path_index, path in enumerate(paths, start=1):
        start = path[0]
        gcode.extend(
            [
                f"(Path {path_index})",
                f"G0 {format_xy(*start)}",
                "G1 Z5.000 F200.0",
            ]
        )
        for x, y in path[1:]:
            gcode.append(f"G1 {format_xy(x, y)} F800.0")
        gcode.append("G0 Z15.000")

    gcode.extend(["G0 X0.000 Y0.000", "M2", "%", ""])
    path = OUT / "first-aircut-mm-safe-z5.ngc"
    path.write_text("\n".join(gcode), encoding="utf-8")
    return path


def write_star_gcode(paths: list[tuple[str, list[tuple[float, float, float]]]]) -> Path:
    gcode = [
        "%",
        "(CNC workshop tools faceted 3D star simulation file)",
        "(Purpose: identifiable no-spindle 3D air-sculpture sanity check)",
        "(Units: millimetres. Coordinates fit inside 140 x 140 mm.)",
        "(No spindle command is included.)",
        "(All moves stay above Z4.000 if work zero is the surface.)",
        "(This is not a cutting recipe.)",
        "G21 (millimetres)",
        "G90 (absolute coordinates)",
        "G17 (XY plane)",
        "G40 G49 G80 (cancel cutter comp, tool length comp, canned cycles)",
        "G54 (work coordinate system)",
        "G94 (feed per minute)",
        "F900.0",
        "G0 Z26.000",
    ]

    for path_index, (name, path) in enumerate(paths, start=1):
        sx, sy, sz = path[0]
        gcode.extend(
            [
                f"(Path {path_index}: {name})",
                f"G0 X{sx:.3f} Y{sy:.3f}",
                f"G1 Z{sz:.3f} F250.0",
            ]
        )
        for x, y, z in path[1:]:
            gcode.append(f"G1 {format_xyz(x, y, z)} F900.0")
        gcode.append("G0 Z26.000")

    gcode.extend(["G0 X0.000 Y0.000", "M2", "%", ""])
    path = OUT / "faceted-star-air-sculpture-mm.ngc"
    path.write_text("\n".join(gcode), encoding="utf-8")
    return path


def write_svg(paths: list[list[tuple[float, float]]]) -> Path:
    margin = 12
    width = 120
    height = 80

    def svg_point(point: tuple[float, float]) -> str:
        x, y = point
        return f"{x + margin:.3f},{height - y + margin:.3f}"

    polylines = []
    for path in paths:
        points = " ".join(svg_point(point) for point in path)
        polylines.append(f'<polyline points="{points}" />')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + margin * 2} {height + margin * 2}" role="img" aria-labelledby="title desc">
  <title id="title">First CNC simulation air-cut preview</title>
  <desc id="desc">A 120 by 80 millimetre rectangle, diagonals, inner rectangle, circle, and crosshair.</desc>
  <rect x="0" y="0" width="{width + margin * 2}" height="{height + margin * 2}" fill="#f4f7f6" />
  <rect x="{margin}" y="{margin}" width="{width}" height="{height}" fill="#fff" stroke="#d7e0df" stroke-width="1" />
  <g fill="none" stroke="#115e59" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    {"".join(polylines)}
  </g>
  <g fill="#be123c" font-family="system-ui, sans-serif" font-size="4">
    <text x="{margin}" y="{height + margin + 7}">0,0</text>
    <text x="{width + margin - 18}" y="{margin - 3}">120,80</text>
  </g>
</svg>
"""
    path = OUT / "first-aircut-mm-safe-z5.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def write_star_svg(paths: list[tuple[str, list[tuple[float, float, float]]]]) -> Path:
    margin = 12
    width = 140
    height = 140

    def svg_point(point: tuple[float, float, float]) -> str:
        x, y, _ = point
        return f"{x + margin:.3f},{height - y + margin:.3f}"

    polylines = []
    for _, path in paths:
        points = " ".join(svg_point(point) for point in path)
        avg_z = sum(point[2] for point in path) / len(path)
        stroke = "#b45309" if avg_z < 8 else "#0f766e" if avg_z < 15 else "#be123c"
        polylines.append(f'<polyline points="{points}" stroke="{stroke}" />')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + margin * 2} {height + margin * 2}" role="img" aria-labelledby="title desc">
  <title id="title">Faceted 3D star CNC simulation preview</title>
  <desc id="desc">A five-point star with coloured paths showing different Z heights.</desc>
  <rect x="0" y="0" width="{width + margin * 2}" height="{height + margin * 2}" fill="#f4f7f6" />
  <rect x="{margin}" y="{margin}" width="{width}" height="{height}" fill="#fff" stroke="#d7e0df" stroke-width="1" />
  <g fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    {"".join(polylines)}
  </g>
  <g font-family="system-ui, sans-serif" font-size="5" fill="#475569">
    <text x="{margin}" y="{height + margin + 8}">Top view. Amber = lower Z, teal = mid Z, red = high Z.</text>
  </g>
</svg>
"""
    path = OUT / "faceted-star-air-sculpture-mm.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def write_setup_sheet() -> Path:
    setup = """# First CNC Simulation Test

Purpose: prove the software path before any real AXYZ controller or table is available.

Files:

- `first-aircut-mm-safe-z5.ngc` - LinuxCNC-style G-code, metric, absolute, no spindle command.
- `first-aircut-mm-safe-z5.svg` - visual preview of the XY path.
- `faceted-star-air-sculpture-mm.ngc` - LinuxCNC-style 3D air-sculpture star, metric, absolute, no spindle command.
- `faceted-star-air-sculpture-mm.svg` - top-view preview of the star path, colour-coded by Z height.
- `linuxcnc-rs274-validation.txt` - LinuxCNC standalone interpreter validation report.

Machine safety assumptions:

- This is a simulation/air-cut file, not a cutting recipe.
- Toolpath envelope is 120 mm x 80 mm.
- All drawing moves are at Z5.000.
- The file contains no spindle start command.
- Before any real use, back up the Windows controller and verify the machine coordinate system, soft limits, work zero, tool length, and emergency stop.

First things to check in a simulator:

1. Units are millimetres.
2. Extents are X0..120 and Y0..80.
3. Z never goes below 5.000 during drawing moves.
4. Program returns to X0 Y0 and ends with M2.

Second star test checks:

1. The preview clearly looks like a five-point star.
2. All coordinates fit inside X15..125 and Y15..125.
3. Z varies between 4.000 and 22.000, so the AXIS view should show a faceted 3D shape when rotated.
4. There is still no spindle start command.

LinuxCNC parser validation:

```bash
python3 scripts/validate_cnc_simulation_test.py
```
"""
    path = OUT / "README.md"
    path.write_text(setup, encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = build_paths()
    star_paths = build_star_paths()
    for generated in (
        write_gcode(paths),
        write_svg(paths),
        write_star_gcode(star_paths),
        write_star_svg(star_paths),
        write_setup_sheet(),
    ):
        print(generated.relative_to(ROOT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate procedural ammonite meshes with Blender's Python API.

Examples:
  blender -b --python scripts/generate_ammonite_blender.py
  blender -b --python scripts/generate_ammonite_blender.py -- --preset bold-ribs --seed 12
  blender -b --python scripts/generate_ammonite_blender.py -- --collection --variants 8
  blender -b --python scripts/generate_ammonite_blender.py -- --size-mm 650 --slab-thickness-mm 50
  blender -b --python scripts/generate_ammonite_blender.py -- --size-mm 650 --slab-thickness-mm 50 --router-max-depth-mm 50
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "local" / "ammonite-prototype"


@dataclass(frozen=True)
class AmmoniteParams:
    preset: str
    seed: int
    turns: float = 3.55
    growth: float = 0.154
    start_radius: float = 0.34
    tube_ratio: float = 0.255
    taper: float = 0.028
    ovalness: float = 0.72
    flat_back: float = 0.42
    rib_count: int = 92
    rib_strength: float = 0.18
    rib_sharpness: float = 2.25
    rib_twist: float = 0.28
    radius_noise: float = 0.022
    rib_noise: float = 0.045
    wobble: float = 0.035
    path_segments: int = 320
    ring_segments: int = 32
    size_mm: float = 360.0


PRESETS: dict[str, AmmoniteParams] = {
    "balanced": AmmoniteParams(preset="balanced", seed=1),
    "bold-ribs": AmmoniteParams(
        preset="bold-ribs",
        seed=1,
        turns=3.35,
        growth=0.163,
        tube_ratio=0.29,
        rib_count=72,
        rib_strength=0.27,
        rib_sharpness=3.3,
        rib_twist=0.42,
        wobble=0.045,
    ),
    "tight-coil": AmmoniteParams(
        preset="tight-coil",
        seed=1,
        turns=4.35,
        growth=0.121,
        tube_ratio=0.22,
        rib_count=118,
        rib_strength=0.15,
        radius_noise=0.016,
    ),
    "smooth-giant": AmmoniteParams(
        preset="smooth-giant",
        seed=1,
        turns=3.1,
        growth=0.175,
        tube_ratio=0.31,
        rib_count=52,
        rib_strength=0.08,
        rib_sharpness=1.4,
        size_mm=650.0,
    ),
}


def blender_args() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="balanced")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--turns", type=float)
    parser.add_argument("--growth", type=float)
    parser.add_argument("--rib-count", type=int)
    parser.add_argument("--rib-strength", type=float)
    parser.add_argument("--size-mm", type=float)
    parser.add_argument("--slab-thickness-mm", type=float, default=50.0)
    parser.add_argument("--router-max-depth-mm", type=float, help="measured usable cutter depth; fails if slab thickness exceeds it")
    parser.add_argument("--stock-margin-mm", type=float, default=45.0)
    parser.add_argument("--guide-hole-diameter-mm", type=float, default=12.0)
    parser.add_argument("--no-manufacturing-guides", action="store_true")
    parser.add_argument("--variants", type=int, default=1)
    parser.add_argument("--collection", action="store_true", help="generate several preset/seed variants")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(blender_args())
    if args.router_max_depth_mm is not None and args.slab_thickness_mm > args.router_max_depth_mm:
        parser.error("--slab-thickness-mm must not exceed --router-max-depth-mm")
    return args


def params_from_args(args: argparse.Namespace, seed_offset: int = 0) -> AmmoniteParams:
    params = replace(PRESETS[args.preset], seed=args.seed + seed_offset)
    for field, value in (
        ("turns", args.turns),
        ("growth", args.growth),
        ("rib_count", args.rib_count),
        ("rib_strength", args.rib_strength),
        ("size_mm", args.size_mm),
    ):
        if value is not None:
            params = replace(params, **{field: value})
    return params


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def low_frequency_noise(rng: random.Random, count: int, amplitude: float) -> list[float]:
    anchors = [rng.uniform(-amplitude, amplitude) for _ in range(9)]
    values: list[float] = []
    for index in range(count + 1):
        u = index / count
        scaled = u * (len(anchors) - 1)
        left = int(math.floor(scaled))
        right = min(left + 1, len(anchors) - 1)
        blend = scaled - left
        # Smoothstep interpolation prevents hard changes in shell radius.
        blend = blend * blend * (3 - 2 * blend)
        values.append(anchors[left] * (1 - blend) + anchors[right] * blend)
    return values


def make_ammonite(params: AmmoniteParams) -> bpy.types.Object:
    rng = random.Random(params.seed)
    radius_noise = low_frequency_noise(rng, params.path_segments, params.radius_noise)
    wobble_noise = low_frequency_noise(rng, params.path_segments, params.wobble)

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []

    for i in range(params.path_segments + 1):
        u = i / params.path_segments
        t = u * params.turns * math.tau
        natural_radius = 1.0 + radius_noise[i]
        spiral_radius = params.start_radius * math.exp(params.growth * t) * natural_radius
        wobble_z = math.sin(t * 0.7 + wobble_noise[i] * 20.0) * wobble_noise[i]
        center = Vector((spiral_radius * math.cos(t), spiral_radius * math.sin(t), wobble_z))

        tangent = Vector(
            (
                params.growth * spiral_radius * math.cos(t) - spiral_radius * math.sin(t),
                params.growth * spiral_radius * math.sin(t) + spiral_radius * math.cos(t),
                0.0,
            )
        ).normalized()
        normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()
        binormal = Vector((0.0, 0.0, 1.0))

        taper_factor = 1.0 - params.taper * u
        tube_radius = (0.13 + params.tube_ratio * spiral_radius) * taper_factor

        rib_phase_noise = rng.uniform(-params.rib_noise, params.rib_noise)
        rib_wave = math.sin(params.rib_count * u * math.tau + rib_phase_noise)
        rib_pulse = max(0.0, rib_wave) ** params.rib_sharpness
        chamber_pulse = 1.0 + params.rib_strength * rib_pulse

        for j in range(params.ring_segments):
            theta = (j / params.ring_segments) * math.tau
            rib_angle_bias = 1.0 + params.rib_twist * math.cos(theta - u * math.tau)
            radial = math.cos(theta) * tube_radius * (1.0 + (chamber_pulse - 1.0) * rib_angle_bias)
            height = math.sin(theta) * tube_radius * params.ovalness
            if height < 0:
                height *= params.flat_back
            point = center + normal * radial + binormal * height
            vertices.append(tuple(point))

    for i in range(params.path_segments):
        for j in range(params.ring_segments):
            a = i * params.ring_segments + j
            b = i * params.ring_segments + ((j + 1) % params.ring_segments)
            c = (i + 1) * params.ring_segments + ((j + 1) % params.ring_segments)
            d = (i + 1) * params.ring_segments + j
            faces.append((a, b, c, d))

    # Close the start and end rings so boolean slicing has a solid-ish shell to intersect.
    faces.append(tuple(reversed(range(params.ring_segments))))
    last_ring_start = params.path_segments * params.ring_segments
    faces.append(tuple(last_ring_start + j for j in range(params.ring_segments)))

    mesh = bpy.data.meshes.new(f"ammonite_{params.preset}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(f"ammonite_{params.preset}_seed_{params.seed}", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()

    # Scale the largest XY dimension to the requested real-world size in millimetres.
    xs = [vertex[0] for vertex in vertices]
    ys = [vertex[1] for vertex in vertices]
    largest = max(max(xs) - min(xs), max(ys) - min(ys))
    obj.scale = (params.size_mm / largest,) * 3

    material = bpy.data.materials.new(f"warm_limestone_{params.preset}_{params.seed}")
    material.diffuse_color = (0.72, 0.58, 0.42, 1.0)
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def add_scene_helpers(obj: bpy.types.Object) -> None:
    bounds = world_bounds(obj)
    center = Vector(
        (
            (bounds["min_x"] + bounds["max_x"]) / 2,
            (bounds["min_y"] + bounds["max_y"]) / 2,
            (bounds["min_z"] + bounds["max_z"]) / 2,
        )
    )
    span = max(bounds["max_x"] - bounds["min_x"], bounds["max_y"] - bounds["min_y"], 250.0)

    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1200
    bpy.context.scene.world.color = (0.04, 0.045, 0.05)

    bpy.ops.object.light_add(type="AREA", location=(center.x - span * 0.25, center.y - span * 0.55, center.z + span * 1.2))
    light = bpy.context.object
    light.name = "softbox"
    light.data.energy = 1200
    light.data.size = span

    bpy.ops.object.camera_add(location=(center.x, center.y - span * 0.45, center.z + span * 1.25), rotation=(math.radians(58), 0, 0))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.data.lens = 42

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=center)
    target = bpy.context.object
    target.name = "view_target"
    constraint = bpy.context.scene.camera.constraints.new(type="TRACK_TO")
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    constraint.target = target


def world_bounds(obj: bpy.types.Object) -> dict[str, float]:
    bpy.context.view_layer.update()
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [corner.x for corner in corners]
    ys = [corner.y for corner in corners]
    zs = [corner.z for corner in corners]
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "min_z": min(zs),
        "max_z": max(zs),
    }


def make_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = color[3]
        bsdf.inputs["Roughness"].default_value = 0.72
    material.blend_method = "BLEND"
    return material


def add_box(name: str, location: tuple[float, float, float], dimensions: tuple[float, float, float], material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj.display_type = "WIRE"
    obj.hide_render = True
    return obj


def make_collection(name: str) -> bpy.types.Collection:
    existing = bpy.data.collections.get(name)
    if existing:
        return existing
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    for current in list(obj.users_collection):
        if current != collection:
            current.objects.unlink(obj)


def mesh_vertex_count(obj: bpy.types.Object) -> int:
    return len(obj.data.vertices) if hasattr(obj.data, "vertices") else 0


def create_slice_object(
    source: bpy.types.Object,
    *,
    index: int,
    z0: float,
    z1: float,
    stock_center: tuple[float, float],
    stock_dimensions: tuple[float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object | None:
    slice_obj = source.copy()
    slice_obj.data = source.data.copy()
    slice_obj.name = f"ammonite_slice_{index:02d}"
    bpy.context.collection.objects.link(slice_obj)
    link_to_collection(slice_obj, collection)
    slice_obj.data.materials.clear()
    slice_obj.data.materials.append(material)

    cutter_material = make_material(f"hidden_slice_cutter_{index:02d}", (1.0, 1.0, 1.0, 0.0))
    cutter = add_box(
        f"slice_cutter_{index:02d}",
        (stock_center[0], stock_center[1], (z0 + z1) / 2),
        (stock_dimensions[0], stock_dimensions[1], z1 - z0),
        cutter_material,
    )
    cutter.hide_viewport = True
    cutter.hide_render = True

    modifier = slice_obj.modifiers.new(f"intersect_slab_{index:02d}", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.object = cutter
    if hasattr(modifier, "solver"):
        modifier.solver = "EXACT"

    bpy.ops.object.select_all(action="DESELECT")
    slice_obj.select_set(True)
    bpy.context.view_layer.objects.active = slice_obj
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except RuntimeError as exc:
        print(f"Warning: boolean slice {index} failed: {exc}", file=sys.stderr)
        bpy.data.objects.remove(slice_obj, do_unlink=True)
        return None
    finally:
        bpy.data.objects.remove(cutter, do_unlink=True)

    if mesh_vertex_count(slice_obj) == 0:
        bpy.data.objects.remove(slice_obj, do_unlink=True)
        return None

    slice_obj["slice_index"] = index
    slice_obj["z_min_mm"] = z0
    slice_obj["z_max_mm"] = z1
    return slice_obj


def add_manufacturing_guides(
    obj: bpy.types.Object,
    *,
    slab_thickness_mm: float,
    router_max_depth_mm: float | None,
    stock_margin_mm: float,
    guide_hole_diameter_mm: float,
) -> dict[str, object]:
    bounds = world_bounds(obj)
    height = bounds["max_z"] - bounds["min_z"]
    slab_count = max(1, math.ceil(height / slab_thickness_mm))

    stock_min_x = bounds["min_x"] - stock_margin_mm
    stock_max_x = bounds["max_x"] + stock_margin_mm
    stock_min_y = bounds["min_y"] - stock_margin_mm
    stock_max_y = bounds["max_y"] + stock_margin_mm
    stock_width = stock_max_x - stock_min_x
    stock_depth = stock_max_y - stock_min_y
    hole_inset = stock_margin_mm * 0.5
    hole_positions = [
        (stock_min_x + hole_inset, stock_min_y + hole_inset),
        (stock_max_x - hole_inset, stock_min_y + hole_inset),
        (stock_max_x - hole_inset, stock_max_y - hole_inset),
        (stock_min_x + hole_inset, stock_max_y - hole_inset),
    ]

    slab_material = make_material("transparent_foam_slab_guides", (0.2, 0.55, 0.95, 0.18))
    dowel_material = make_material("registration_dowel_guides", (0.05, 0.2, 0.95, 0.55))
    glue_material = make_material("translucent_glue_lines", (1.0, 0.68, 0.18, 0.28))
    slice_collection = make_collection("assembled_ammonite_slices")

    slabs = []
    slice_objects = []
    for index in range(slab_count):
        z0 = bounds["min_z"] + index * slab_thickness_mm
        z1 = min(z0 + slab_thickness_mm, bounds["max_z"])
        z_mid = (z0 + z1) / 2
        add_box(
            f"foam_slab_{index + 1:02d}",
            ((stock_min_x + stock_max_x) / 2, (stock_min_y + stock_max_y) / 2, z_mid),
            (stock_width, stock_depth, z1 - z0),
            slab_material,
        )
        color_shift = (index % 4) * 0.045
        slice_material = make_material(
            f"machined_slice_material_{index + 1:02d}",
            (0.72 + color_shift, 0.58 + color_shift * 0.5, 0.42, 1.0),
        )
        slice_obj = create_slice_object(
            obj,
            index=index + 1,
            z0=z0,
            z1=z1,
            stock_center=((stock_min_x + stock_max_x) / 2, (stock_min_y + stock_max_y) / 2),
            stock_dimensions=(stock_width, stock_depth),
            material=slice_material,
            collection=slice_collection,
        )
        if slice_obj is not None:
            slice_objects.append(slice_obj)
        if index > 0:
            add_box(
                f"glue_line_{index:02d}",
                ((stock_min_x + stock_max_x) / 2, (stock_min_y + stock_max_y) / 2, z0),
                (stock_width, stock_depth, 0.8),
                glue_material,
            )
        slabs.append(
            {
                "index": index + 1,
                "z_min_mm": z0,
                "z_max_mm": z1,
                "thickness_mm": z1 - z0,
                "object_name": slice_obj.name if slice_obj is not None else None,
            }
        )

    guide_depth = height + 20.0
    guide_mid_z = (bounds["min_z"] + bounds["max_z"]) / 2
    for index, (x, y) in enumerate(hole_positions, start=1):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48,
            radius=guide_hole_diameter_mm / 2,
            depth=guide_depth,
            location=(x, y, guide_mid_z),
        )
        guide = bpy.context.object
        guide.name = f"registration_hole_guide_{index:02d}"
        guide.data.materials.append(dowel_material)
        guide.display_type = "WIRE"
        guide.hide_render = True

    obj.name = f"{obj.name}_full_reference_wire"
    obj.display_type = "WIRE"
    obj.hide_render = True

    return {
        "status": "sliced_visual_simulation_not_cam_ready",
        "warning": "Registration holes are outside the finished ammonite. If the assembled stack cannot fit under the router, these must be removable tabs/ears or part of an external glue-up jig, then removed by hand.",
        "registration_strategy": "machine each slab while it fits under the router; align during glue-up with removable tabs/ears, hidden back-side holes, or an external jig",
        "slab_thickness_mm": slab_thickness_mm,
        "router_max_depth_mm": router_max_depth_mm,
        "router_depth_status": "measured" if router_max_depth_mm is not None else "unknown_use_slab_thickness_as_conservative_simulation_value",
        "slab_count": slab_count,
        "slice_object_names": [slice_obj.name for slice_obj in slice_objects],
        "guide_hole_diameter_mm": guide_hole_diameter_mm,
        "stock_margin_mm": stock_margin_mm,
        "stock_bounds_mm": {
            "min_x": stock_min_x,
            "max_x": stock_max_x,
            "min_y": stock_min_y,
            "max_y": stock_max_y,
            "width": stock_width,
            "depth": stock_depth,
        },
        "model_bounds_mm": bounds,
        "registration_holes_mm": [
            {"index": index, "x": x, "y": y, "diameter": guide_hole_diameter_mm}
            for index, (x, y) in enumerate(hole_positions, start=1)
        ],
        "slabs": slabs,
        "process_notes": [
            "Cut matching registration holes in every foam sheet before or during roughing.",
            "Machine each slab to its final or near-final outline before glue-up; do not rely on a post-glue CNC trim unless the assembled stack fits under the machine.",
            "If holes sit outside the finished outline, leave small removable tabs/ears that keep the holes attached during glue-up.",
            "Use dowels or temporary rods through the guide holes to align the stack while the adhesive cures.",
            "After curing, remove tabs/ears manually with a saw, knife, hot wire, rasp, or sanding block.",
            "For a visible finished sculpture, prefer hidden back-side registration holes or an external jig so there is less cosmetic repair.",
            "The generated per-slab meshes are visual/planning geometry, not roughing/finishing CAM.",
            "Generate true per-slab CAM files after a small foam test proves the guide-hole workflow.",
        ],
    }


def export_mesh_object(obj: bpy.types.Object, path: Path, file_type: str) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    if file_type == "stl":
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True)
        else:
            bpy.ops.export_mesh.stl(filepath=str(path), use_selection=True)
        return

    if file_type == "obj":
        if hasattr(bpy.ops.wm, "obj_export"):
            bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True)
        else:
            bpy.ops.export_scene.obj(filepath=str(path), use_selection=True)
        return

    raise ValueError(f"Unsupported export type: {file_type}")


def export_slice_meshes(out_dir: Path, slug: str, manufacturing_plan: dict[str, object]) -> list[dict[str, object]]:
    slice_dir = out_dir / f"{slug}-slices"
    slice_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    for slab in manufacturing_plan.get("slabs", []):
        if not isinstance(slab, dict):
            continue
        object_name = slab.get("object_name")
        if not object_name:
            continue
        slice_obj = bpy.data.objects.get(str(object_name))
        if slice_obj is None:
            continue
        index = int(slab["index"])
        stem = f"{slug}-slice-{index:02d}"
        stl_path = slice_dir / f"{stem}.stl"
        obj_path = slice_dir / f"{stem}.obj"
        export_mesh_object(slice_obj, stl_path, "stl")
        export_mesh_object(slice_obj, obj_path, "obj")
        exported.append(
            {
                "index": index,
                "object_name": object_name,
                "stl": str(stl_path),
                "obj": str(obj_path),
                "z_min_mm": slab["z_min_mm"],
                "z_max_mm": slab["z_max_mm"],
                "thickness_mm": slab["thickness_mm"],
            }
        )
    return exported


def export_object(
    obj: bpy.types.Object,
    params: AmmoniteParams,
    out_dir: Path,
    manufacturing_plan: dict[str, object] | None,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"ammonite-{params.preset}-seed-{params.seed}"
    blend_path = out_dir / f"{slug}.blend"
    stl_path = out_dir / f"{slug}.stl"
    obj_path = out_dir / f"{slug}.obj"
    params_path = out_dir / f"{slug}.json"

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    export_mesh_object(obj, stl_path, "stl")
    export_mesh_object(obj, obj_path, "obj")

    manifest = {
        "slug": slug,
        "params": asdict(params),
        "files": {
            "blend": str(blend_path),
            "stl": str(stl_path),
            "obj": str(obj_path),
        },
        "notes": [
            "Procedural logarithmic spiral shell generated by Blender Python.",
            "Not yet CAM-ready; inspect normals, overhangs, wall thickness, slab plan, and intended manufacturing method.",
        ],
    }
    if manufacturing_plan is not None:
        manufacturing_plan["slice_files"] = export_slice_meshes(out_dir, slug, manufacturing_plan)
        manifest["manufacturing_plan"] = manufacturing_plan
    params_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["files"]["params"] = str(params_path)
    return manifest


def build_param_sets(args: argparse.Namespace) -> list[AmmoniteParams]:
    if not args.collection:
        return [params_from_args(args)]

    presets = list(PRESETS)
    params: list[AmmoniteParams] = []
    for index in range(args.variants):
        preset = presets[index % len(presets)]
        variant_args = argparse.Namespace(**vars(args))
        variant_args.preset = preset
        params.append(params_from_args(variant_args, seed_offset=index))
    return params


def main() -> None:
    args = parse_args()
    manifests = []
    for params in build_param_sets(args):
        clear_scene()
        ammonite = make_ammonite(params)
        add_scene_helpers(ammonite)
        manufacturing_plan = None
        if not args.no_manufacturing_guides:
            manufacturing_plan = add_manufacturing_guides(
                ammonite,
                slab_thickness_mm=args.slab_thickness_mm,
                router_max_depth_mm=args.router_max_depth_mm,
                stock_margin_mm=args.stock_margin_mm,
                guide_hole_diameter_mm=args.guide_hole_diameter_mm,
            )
        manifests.append(export_object(ammonite, params, args.out_dir, manufacturing_plan))

    index_path = args.out_dir / "manifest.json"
    index_path.write_text(json.dumps({"ammonites": manifests}, indent=2), encoding="utf-8")
    print(f"Wrote {index_path}")
    for manifest in manifests:
        print(f"Wrote {manifest['slug']}")


if __name__ == "__main__":
    main()

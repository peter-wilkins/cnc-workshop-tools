---
name: cad-geometry-validation
description: Validate generated CAD geometry against a design spec using deterministic evidence before visual judgement. Use when working with CadQuery, build123d, FreeCAD, OpenSCAD, Blender, STEP, STL, OBJ, GLB, toolpath previews, geometry reports, generated models, or when the user asks whether a CAD artifact matches the intended dimensions, features, volume, or shape.
---

# CAD Geometry Validation

## Workflow

1. Collect the design intent, source model, parameter manifest, exported geometry,
   screenshots/renders, and any generated reports.
2. Prefer deterministic checks over screenshots. Use available scripts or CAD
   tooling before making aesthetic claims.
3. Check units first. Most false CAD confidence comes from silent unit mismatch.
4. Validate the geometry against the spec:
   - execution succeeds without hidden errors
   - solid or mesh validity is appropriate for the process
   - bounding box matches expected length, width, height, and stock envelope
   - volume and mass estimate are plausible
   - named features exist and are placed correctly
   - hole centers, diameters, registration marks, and datum features match intent
   - symmetry, taper, rocker, ribs, relief, or curvature match the brief
   - minimum wall thickness and minimum feature size are plausible
   - sliced parts preserve alignment features and glue-up logic
5. Use visual review only after the measurable checks. Renders are for
   recognisability, proportion, and "does this look wrong?" judgement.

## Output Shape

Lead with findings:

- `Pass`: evidence-backed checks that match the spec.
- `Fail`: concrete mismatch, risk, or missing feature.
- `Unknown`: checks that need a tool, source file, measurement, or human input.

Then include:

- commands or tools used
- files inspected
- measurement table if useful
- recommended fix or next validation step

## Rules

- Do not claim a model is manufacturable just because it renders.
- Do not treat STL mesh validity as enough for precise parametric design.
- Keep generated heavy artifacts under `local/` unless the repo explicitly tracks
  them as examples.
- If no validation script exists yet, propose the smallest reusable script rather
  than doing one-off manual arithmetic repeatedly.

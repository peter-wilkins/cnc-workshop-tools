---
name: cad-manufacturability-review
description: Review CAD designs for real-world fabrication risk across CNC routing, foam slicing, fixtures, moulds, composites, dust, PPE, and workshop workflow. Use before cutting, printing, mould-making, layup, ordering materials, producing CAM/toolpaths, or when the user asks whether a generated CAD design can actually be made safely and cleanly.
---

# CAD Manufacturability Review

## Workflow

1. Identify the intended process: CNC foam, CNC wood, 3D print, mould, composite
   layup, fixture, finishing coupon, or other workshop process.
2. Extract the hard constraints:
   - machine travel, Z clearance, cutter reach, collet clearance, dust shoe
   - stock size, slab thickness, workholding, tabs, datum strategy
   - material behaviour, dust, chip size, fumes, heat, springback, cure needs
   - required finish and acceptable hand work
   - available extraction, PPE, neighbours, noise, and cleanup path
3. Check the design against the process:
   - can the tool physically reach every feature?
   - can the part be held down without ruining the visible surface?
   - can waste escape or be collected without clogging extraction?
   - are there brittle, thin, unsupported, or unmachinable details?
   - are registration holes, ears, dowels, flanges, or jigs needed?
   - does the design avoid unnecessary sanding, fairing, and dust creation?
   - is the first coupon small enough to learn cheaply?
4. Separate blockers from improvements. A blocker prevents safe fabrication; an
   improvement makes the job cleaner, faster, or more repeatable.
5. Recommend the next physical proof: air-cut, scrap cut, material coupon, glue-up
   coupon, finish coupon, or full-size dry run.

## Output Shape

Use this order:

1. `Blockers`
2. `Recommended CAD changes`
3. `Fixture / workholding plan`
4. `Extraction and PPE notes`
5. `First coupon`
6. `Open questions`

Keep the review grounded in evidence from the current files and known workshop
constraints. If the router capacity, material, or cutter is unknown, say so and
route the next step to measurement rather than guessing.

## Bias

- Prefer preventing dust and rework over extracting dust after the fact.
- Prefer small coupons over big heroic first cuts.
- Prefer simple registration and visible datums over clever hidden alignment.
- Prefer explicit manufacturing assumptions in manifests over chat-only memory.

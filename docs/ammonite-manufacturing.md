# Procedural Ammonite Manufacturing Notes

An ammonite is a good procedural modelling target because a logarithmic spiral plus a swept profile gets surprisingly close before hand sculpting is needed.

The generator currently does four useful things:

- builds a logarithmic spiral shell
- sweeps an oval profile along it
- adds ribbing with separate controls for plan-view outline and raised face relief
- adds low-frequency variation so each seed is slightly different
- slices the model into horizontal slab meshes for Blender inspection
- adds translucent glue-line planes so the assembled stack can be checked visually

The current white-sculpture baseline is:

```bash
blender -b --python scripts/generate_ammonite_blender.py -- --preset sculpture-target --seed 7 --size-mm 650 --slab-thickness-mm 50
```

It is a proof shape, not a final commission model. It is good enough for learning the foam-slab workflow and finish tests. It still needs hand judgement against the physical reference before a full-size cut.

## Foam Slab Workflow

A large piece may be deeper than the router can cut. In that case, do not rely on a final CNC trim after glue-up.

Safer workflow:

1. Generate the full model.
2. Decide a slab thickness that fits under the router and cutter.
3. Machine each foam slab while it is still flat and shallow enough.
4. Cut each slab to final or near-final outline before glue-up.
5. Add registration holes in removable ears, hidden back-side locations, or an external jig.
6. Align the slabs with dowels or rods while the adhesive cures.
7. Remove tabs/ears manually with saw, knife, hot wire, rasp, or sanding block.

If the glued stack does fit under the router, a final cleanup pass may be possible, but the generator does not assume that.

The generated slab meshes are planning geometry, not CAM. They are useful for checking:

- how many foam sheets are needed
- whether the stack still reads visually as one ammonite after slicing
- where registration strategy needs tabs, hidden holes, or an external jig
- whether a small proof-of-process foam test is worth cutting

See `docs/router-capacity.md` before treating any slab thickness as real machine capacity.

## Foam Waste

CNC foam work can create large clean chunks as well as fine dust.

Useful first-stage extraction idea:

- catch large foam chips/offcuts before the cyclone or fine filter
- keep clean foam separate from mixed carbon/fibreglass/general dust
- bag clean foam chunks separately if they are going to be reused, for example as insulation fill where appropriate

Fine dust still needs proper extraction and PPE.

## First Coupons

Before the large sculpture, make small coupons that answer one question each.

Shape coupon:

```bash
blender -b --python scripts/generate_ammonite_blender.py -- --preset sculpture-target --seed 7 --size-mm 120 --slab-thickness-mm 25
```

Use it to judge whether the rib softness, centre spiral, and inflated whorl feel right in the hand.

Slice coupon:

- use two or three shallow foam layers
- include removable registration ears or an external alignment jig
- glue the stack and hand-fair it
- inspect whether the glue lines become invisible enough after filler/primer

Finish coupons:

- matte white: primer, filler, sanding, satin/matte top coat
- polished fossil: brown/gold base, hand-painted mineral veining, clear coat
- dark cut-section: charcoal base, ochre chamber lines, gloss clear
- pearlescent shell: pale base plus mica or pearlescent top coat

Keep the coupon notes boring: substrate, primer, filler, paint, clear coat, sanding grit, drying time, result, and what failed.

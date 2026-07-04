# Procedural Ammonite Manufacturing Notes

An ammonite is a good procedural modelling target because a logarithmic spiral plus a swept profile gets surprisingly close before hand sculpting is needed.

The generator currently does four useful things:

- builds a logarithmic spiral shell
- sweeps an oval profile along it
- adds ribbing with sine-wave-like periodic scaling
- adds low-frequency variation so each seed is slightly different

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

## Foam Waste

CNC foam work can create large clean chunks as well as fine dust.

Useful first-stage extraction idea:

- catch large foam chips/offcuts before the cyclone or fine filter
- keep clean foam separate from mixed carbon/fibreglass/general dust
- bag clean foam chunks separately if they are going to be reused, for example as insulation fill where appropriate

Fine dust still needs proper extraction and PPE.

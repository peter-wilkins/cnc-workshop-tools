# Router Capacity Notes

The actual AXYZ machine depth is not known yet.

What we know locally:

- the workshop inventory identifies the machine as an AXYZ CNC router
- the exact model, spindle, collets, cutter reach, dust shoe, spoilboard state, and usable Z clearance still need confirming
- no reliable measured maximum cut depth exists in this repo yet

So the ammonite generator defaults to a conservative simulation value:

```text
slab_thickness_mm = 50
router_max_depth_mm = unknown
```

That is not a machine promise. It is just a safe planning number for foam-slab experiments.

## How To Measure The Real Usable Depth

Measure usable depth on the actual table before cutting:

1. Fit the intended foam cutter.
2. Set up the spoilboard and any sacrificial board exactly as it will be used.
3. Measure table/spoilboard surface to the lowest safe collet or spindle-nut position.
4. Measure usable cutter flute length and safe stick-out.
5. Subtract clearance for dust shoe, clamps, hold-down, uneven stock, and a safety margin.
6. Use the smallest of those numbers as `router_max_depth_mm`.

Useful rule:

```text
usable_depth = min(
  cutter_flute_length,
  safe_cutter_stickout,
  z_clearance_after_spoilboard_and_hold_down,
  dust_shoe_clearance
) - safety_margin
```

For foam, the cutter may physically reach deeper than it can cut cleanly or safely. Test on scrap first.

## Current Ammonite Setting

Until measured, generate slices with:

```bash
blender -b --python scripts/generate_ammonite_blender.py -- --preset sculpture-target --seed 7 --size-mm 650 --slab-thickness-mm 50
```

After measuring the real machine:

```bash
blender -b --python scripts/generate_ammonite_blender.py -- --preset sculpture-target --seed 7 --size-mm 650 --slab-thickness-mm 50 --router-max-depth-mm 50
```

If `--slab-thickness-mm` exceeds `--router-max-depth-mm`, the script fails rather than hiding a dangerous assumption.

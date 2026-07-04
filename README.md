# CNC Workshop Tools

Small public CNC and digital-fabrication scripts from a workshop bootstrap project.

The bias here is conservative:

- prove toolpaths in simulation before a real machine sees them
- keep generated test files boring and inspectable
- use official non-Snap application builds where practical
- keep manufacturing assumptions explicit in JSON/manifests

## What is in here

- `scripts/generate_cnc_simulation_test.py` generates safe LinuxCNC-style air-cut G-code plus SVG previews.
- `scripts/validate_cnc_simulation_test.py` validates the generated G-code with LinuxCNC's standalone `rs274` interpreter.
- `scripts/open_*_cnc_simulation` opens the example files in LinuxCNC AXIS simulation.
- `scripts/generate_ammonite_blender.py` generates parameterised ammonite meshes with Blender Python.
- `scripts/install_blender_official.sh` installs official Blender LTS into `~/.local/opt/blender`.
- `scripts/install_cnc_sim_tools_ubuntu.sh` installs LinuxCNC user-space simulation tools on Ubuntu.

## Quick Start

Install Blender without Snap:

```bash
scripts/install_blender_official.sh
```

Install LinuxCNC simulation support on Ubuntu:

```bash
scripts/install_cnc_sim_tools_ubuntu.sh
```

Generate and validate the conservative G-code examples:

```bash
python3 scripts/generate_cnc_simulation_test.py
python3 scripts/validate_cnc_simulation_test.py
```

Open the more visual star test in LinuxCNC AXIS:

```bash
scripts/open_star_cnc_simulation
```

Generate an ammonite mesh:

```bash
blender -b --python scripts/generate_ammonite_blender.py -- --preset bold-ribs --seed 12 --size-mm 650 --slab-thickness-mm 50
```

Outputs go under `local/` by default so large generated files do not get committed accidentally.

## Safety

The example G-code is for simulation and air-cut testing. It is not a cutting recipe.

Before any real machine use:

- verify units, coordinate system, work zero, limits, and emergency stop
- run in a simulator/backplot first
- run above stock with spindle disabled
- keep the original machine controller backed up and untouched until the workflow is proven

## License

MIT.

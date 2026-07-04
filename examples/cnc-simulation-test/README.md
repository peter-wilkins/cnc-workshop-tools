# First CNC Simulation Test

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

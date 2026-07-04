#!/usr/bin/env bash
set -euo pipefail

echo "== CNC simulation tool install for Ubuntu =="
echo "This installs linuxcnc-uspace from apt for simulation and G-code parser checks."
echo "It does not install a realtime kernel and is not a real-machine controller setup."
echo "It does not install Snap packages."
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is not installed; cannot continue." >&2
  exit 1
fi

sudo apt-get update

if apt-cache policy linuxcnc-uspace | grep -q "Candidate: (none)"; then
  echo "linuxcnc-uspace is not available from this Ubuntu apt configuration." >&2
  echo "For real CNC control, use the official LinuxCNC Live/Install image instead." >&2
  exit 1
fi

sudo apt-get install -y linuxcnc-uspace

echo
echo "Installed versions:"
linuxcnc --version || true
rs274 -g examples/cnc-simulation-test/first-aircut-mm-safe-z5.ngc >/dev/null || true
echo
echo "Try:"
echo "  python3 scripts/validate_cnc_simulation_test.py"
echo "  scripts/open_star_cnc_simulation"

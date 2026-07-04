#!/usr/bin/env bash
# title: Install official Blender LTS
# summary: Install Blender from the official Linux tarball into ~/.local/opt/blender and avoid Snap.
set -euo pipefail

version="4.5.11"
series="4.5"
base_url="https://download.blender.org/release/Blender${series}"
archive="blender-${version}-linux-x64.tar.xz"
sha_file="blender-${version}.sha256"
install_root="$HOME/.local/opt/blender"
bin_dir="$HOME/.local/bin"

mkdir -p "$install_root" "$bin_dir"
cd "$install_root"

curl -L --fail --continue-at - --output "$archive" "$base_url/$archive"
curl -L --fail --output "$sha_file" "$base_url/$sha_file"
sha256sum --ignore-missing -c "$sha_file"

rm -rf "blender-${version}-linux-x64"
tar -xf "$archive"
ln -sfn "$install_root/blender-${version}-linux-x64/blender" "$bin_dir/blender"

"$bin_dir/blender" --version | head -8
echo
echo "Installed:"
echo "  $bin_dir/blender"
echo
echo "If a Snap version exists, remove it separately with:"
echo "  sudo snap remove blender"

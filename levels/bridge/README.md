# Bridge level asset installation

The Python scene has been committed to GitHub, but the five large image files and seven parallax PNGs must be copied from the accompanying afterglow_bridge_game_patch_v08.zip.

Unzip the archive, then merge `levels/bridge/assets` into this directory.

Required paths:
- `levels/bridge/assets/sections/` (5 images, 2172x724 RGBA each)
- `levels/bridge/assets/parallax/` (7 background images)
- `levels/bridge/assets/tony_sprites.png`
- `levels/bridge/assets/roy_idle.png`

A missing-assets warning appears instead of a startup crash if assets have not yet been copied.

Run: `python3 main.py --scene bridge`

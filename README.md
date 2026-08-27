# Sol's RNG Core

Focused Linux/X11 helper containing:

- Discord biome webhook notifications for all normal, event, and rare biomes
- Rare biome role/@everyone logic
- Optional Roblox private-server link in every webhook embed
- Automatic biome thumbnail lookup from `library/biomes/` and Discord attachment thumbnails
- Anti-AFK start/stop
- Swap-to-game and restore-previous-window helpers
- PySide6 GUI with built-in themes

## Launch

```bash
cd ~/Downloads/SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo pacman -S xdotool
python main.py
```

Put biome images in:

```text
library/biomes/
```

The image filename should match the biome name, for example `NORMAL.png`, `SANDSTORM.png`, or `DREAMSPACE.png` (spaces/underscores/hyphens are normalized).

The private-server link and image directory can be changed under **Discord Webhook** in the GUI.

SolsRNGCore READ THIS NOW
A Linux-first Sol's RNG automation and Discord notification core built with Python and PySide6.

Features
Discord webhook profiles
Multiple Discord profiles running simultaneously
Independent webhook settings for every profile
Per-profile Roblox private-server links
Per-biome Discord role IDs
Per-profile biome notification filters
Automatic Sober biome detection
Biome-specific Discord embed styling
Discord webhook test broadcasting
Anti-AFK support (STILL A W.I.P)
PySide6 graphical interface
Persistent configuration through ~/.config/solsrng/core.json
Installation
SolsRNGCore is designed as a Linux-first application. The commands below cover the major Linux distribution families.

Debian / Ubuntu / Linux Mint / Pop!_OS / Zorin OS
Install Python, pip, and virtual-environment support:

sudo apt update
sudo apt install python3 python3-pip python3-venv
Then install SolsRNGCore:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Fedora
sudo dnf install python3 python3-pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Arch Linux / EndeavourOS / Manjaro
sudo pacman -Syu python python-pip
Then:

cd SolsRNGCore
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
SteamOS
SteamOS is Arch Linux-based.

sudo steamos-readonly disable
sudo pacman -Syu python python-pip
Then:

cd ~/Downloads/SolsRNGCore
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
After installing the system packages, SteamOS can be returned to its normal read-only state:

sudo steamos-readonly enable
openSUSE Tumbleweed / Leap
sudo zypper install python3 python3-pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
RHEL / Rocky Linux / AlmaLinux / CentOS Stream
sudo dnf install python3 python3-pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Gentoo
sudo emerge --ask dev-lang/python
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Alpine Linux
sudo apk add python3 py3-pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Void Linux
sudo xbps-install -S python3 python3-pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
NixOS
For a temporary development environment:

nix-shell -p python3 python3Packages.pip
Then:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Universal Python Installation
If your distribution already provides Python 3, pip, and venv, you can use:

cd SolsRNGCore
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
Running After Installation
Every time you open a new terminal:

cd SolsRNGCore
source .venv/bin/activate
python main.py
SolsRNGCore is currently developed and tested primarily on Linux, with SteamOS being one of the primary development environments.

Discord Profiles
SolsRNGCore supports multiple Discord profiles at the same time.

The selected profile is only the profile being edited. All enabled profiles run simultaneously.

Each profile has its own webhook, Roblox private-server URL, biome filters, Discord role IDs, and image settings.

Biome Notifications
Biome artwork is stored in library/biomes/.

Supported biome assets include NORMAL, WINDY, SNOWY, RAINY, SANDSTORM, HELL, STARFALL, HEAVEN, CORRUPTION, NULL, PUMPKIN MOON, GRAVEYARD, BLAZING SUN, BLOOD RAIN, AURORA, EGGLAND, GLITCHED, DREAMSPACE, CYBERSPACE, and SINGULARITY.

Discord Embed Styling
Each biome can have its own title, emoji, embed color, thumbnail artwork, and SolsRNGCore footer branding.

Webhook Testing
The Discord test button broadcasts to every enabled profile with a configured webhook URL.

Anti-AFK
Includes configurable Anti-AFK support for Sober/Roblox gameplay windows.

Running
python main.py
Installing Dependencies
pip install -r requirements.txt
Repository
https://github.com/69voidtheangel/SolsRNGCore

SolsRNGCore — Linux-first Sol's RNG automation & Discord core.

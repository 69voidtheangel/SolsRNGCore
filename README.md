# 🌙 SolsRNGCore

> A Linux-first Sol's RNG automation & Discord notification core.

SolsRNGCore is a Linux-focused companion for Sol's RNG, built around live biome monitoring, Discord notifications, per-biome roles, biome artwork, Anti-AFK support, diagnostics, and a clean PySide6 GUI.

<p align="center">
<strong>🐧 Linux First • 🎮 Steam Deck Ready • 💬 Discord Powered • 🌙 Midnight UI</strong>
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌦️ Live Biome Detection | Monitors Sober's Roblox logs and detects actual biome changes |
| 💬 Multiple Discord Profiles | Configure and run multiple webhook profiles independently |
| 🎨 Biome Embeds | Send biome notifications with biome artwork |
| 🔔 Per-Biome Roles | Assign Discord role IDs to individual biomes |
| 👥 @everyone Fallback | Optional fallback for rare biomes |
| 🔗 Private Server Links | Store a Roblox private-server link per profile |
| 💤 Anti-AFK | Built-in Anti-AFK support for Sober |
| 🖥️ PySide6 GUI | Clean midnight-themed graphical interface |
| 💾 Persistent Configuration | Settings and profiles survive restarts |
| 📜 Live Diagnostics | Bounded logs for application activity |
| 🚨 Fatal Diagnostics | Diagnostic information for unexpected failures |
| 🧠 RAM-Conscious Logging | Prevents unlimited in-memory diagnostic growth |

---

# 🌦️ Live Biome Monitoring

SolsRNGCore monitors Sober's Roblox logs for BloxstrapRPC
`SetRichPresence` events.

The monitor keeps one authoritative current-biome state.

Repeated updates such as:

NORMAL → NORMAL → NORMAL → NORMAL

are ignored.

A real transition such as:

NORMAL → SNOWY

is processed immediately.

This prevents Rich Presence refreshes from flooding Discord with duplicate
notifications.

---

# 🌦️ Supported Biomes

NORMAL
WINDY
SNOWY
RAINY
SANDSTORM
HELL
STARFALL
HEAVEN
CORRUPTION
NULL
PUMPKIN MOON
GRAVEYARD
BLAZING SUN
BLOOD RAIN
AURORA
EGGLAND
GLITCHED
DREAMSPACE
CYBERSPACE
SINGULARITY

---

# 💬 Discord Profiles

Each webhook profile can have its own configuration.

### Per-profile settings

- Webhook URL
- Enabled / disabled state
- Biomes to notify
- Individual biome role IDs
- @everyone fallback
- Roblox private-server URL
- Biome image directory

Profiles operate independently, allowing multiple servers to receive
notifications without sharing the same settings.

---

# 🔔 Discord Role Notifications

Each supported biome can have its own Discord role ID.

Example:

GLITCHED → <role ID>
DREAMSPACE → <role ID>
CYBERSPACE → <role ID>
SINGULARITY → <role ID>

When a role is configured, the notification can mention that role.

A profile can also use the optional @everyone fallback for rare biomes.

---

# 🎨 Biome Artwork

Biome images are stored in:

library/biomes/

The application selects biome artwork for Discord notifications based on
the detected biome.

---

# 💤 Anti-AFK

SolsRNGCore includes configurable Anti-AFK support for Sober.

The Anti-AFK system operates independently from biome monitoring.

### Current options

- Enable / disable Anti-AFK
- Configurable interval
- Configurable input method
- Window restoration support

---

# 📜 Diagnostics & Logging

SolsRNGCore uses bounded diagnostic logging.

The application avoids allowing diagnostic history to grow indefinitely in
RAM during long-running sessions.

### Diagnostic levels

INFO
WARN
ERROR
FATAL

Important events can include:

- Monitor startup
- Log rotation
- Current biome detection
- Biome transitions
- Discord queue activity
- Discord success / failure
- Anti-AFK activity
- Application exceptions
- Fatal diagnostics

---

# 🚨 Fatal Error Diagnostics

Fatal diagnostics are designed to provide useful debugging information when
the application encounters an unexpected failure.

Diagnostic information may include:

- Failure reason
- Basic system information
- Recent diagnostic messages
- Python traceback when available

Sensitive information such as Discord webhook credentials should never be
stored in diagnostic output.

Native crashes such as SIGSEGV are separate from ordinary Python exceptions
and may be reported by the operating system.

---

# 🧠 RAM & Performance

SolsRNGCore is intended for long-running sessions.

The diagnostic system is bounded so that:

- GUI logs do not grow forever
- Diagnostic history does not grow forever
- Discord work does not create an unlimited queue
- Old Sober log history is not repeatedly processed

The goal is to keep the application lightweight during extended sessions,
including Steam Deck AFK sessions.

---

# 🐧 Linux First

SolsRNGCore is developed primarily on Linux, with SteamOS / Steam Deck being
one of the main development environments.

The application is intended for modern Linux distributions that can provide
Python 3, Qt/PySide6, and the required input automation dependencies.

## Linux distribution compatibility

### 🟢 Primary development environment

- SteamOS
- Arch Linux

### 🟡 Intended / community environments

- Debian
- Ubuntu
- Linux Mint
- Pop!_OS
- Fedora
- openSUSE
- Manjaro
- EndeavourOS
- CachyOS
- Bazzite
- Gentoo
- Void Linux
- NixOS
- Alpine Linux
- Other modern Linux distributions

> Package names and service setup can vary by distribution and release.
> SteamOS / Steam Deck is the primary development and testing environment.

---

# 🎮 SteamOS / Steam Deck

## Install system dependencies

sudo pacman -Syu
sudo pacman -S python python-pip ydotool

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

SolsRNGCore will start ydotoold automatically when required.

---

# 🏹 Arch Linux

## Install system dependencies

sudo pacman -Syu
sudo pacman -S python python-pip ydotool

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

---

# 🌀 Debian

## Debian 13 / newer

Install:

sudo apt update
sudo apt install python3 python3-pip python3-venv ydotool

Recent Debian packaging provides both the ydotool client and ydotoold daemon
from the ydotool package.

## Debian 12 / older releases

Install:

sudo apt update
sudo apt install python3 python3-pip python3-venv ydotool ydotoold

If your release does not provide the newer ydotool package, use the upstream
build instructions described in the Manual ydotool Build section below.

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

---

# 🟠 Ubuntu / Ubuntu-based

Ubuntu provides ydotool packages through the Universe repository on supported
releases.

## Enable Universe

sudo add-apt-repository universe
sudo apt update

## Install dependencies

sudo apt install python3 python3-pip python3-venv ydotool ydotoold

If your Ubuntu release does not provide ydotoold as a separate package, install
ydotool and use the daemon/service provided by that release.

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

---

# 🌿 Linux Mint

Linux Mint is Ubuntu/Debian based, so use the package manager for the
underlying release.

sudo apt update
sudo apt install python3 python3-pip python3-venv ydotool ydotoold

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

> Package availability depends on the Ubuntu/Debian release underneath Mint.

---

# 🟣 Fedora

Fedora provides a ydotool package containing both ydotool and ydotoold.

## Install dependencies

sudo dnf install python3 python3-pip ydotool

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

Fedora may provide ydotoold through its ydotool package and system service.

---

# 🔵 openSUSE

## Install dependencies

sudo zypper refresh
sudo zypper install python3 python3-pip ydotool

If ydotool is not available in your enabled repositories, use the Manual
ydotool Build section below.

## Install SolsRNGCore

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

## Launch

python main.py

---

# 🟢 Manjaro

Manjaro uses the Arch package ecosystem.

sudo pacman -Syu
sudo pacman -S python python-pip ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

---

# 🟢 EndeavourOS

EndeavourOS is Arch-based.

sudo pacman -Syu
sudo pacman -S python python-pip ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

---

# 🟢 CachyOS

CachyOS is Arch-based.

sudo pacman -Syu
sudo pacman -S python python-pip ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

---

# 🟢 Bazzite

Bazzite is Fedora-based.

Use:

sudo dnf install python3 python3-pip ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

> Bazzite is image-based, so package-management behavior may differ from a
> conventional Fedora installation.

---

# 🔴 Gentoo

Gentoo package availability can vary by repository and profile.

First search for ydotool:

sudo emerge --sync
emerge --search ydotool

If available in your configured repositories:

sudo emerge app-misc/ydotool

Install Python:

sudo emerge dev-lang/python

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

If your Gentoo tree does not provide ydotool, use the Manual ydotool Build
section below.

---

# ⚫ Void Linux

Install Python and development tools:

sudo xbps-install -S
sudo xbps-install python3 python3-pip

Search for ydotool:

xbps-query -Rs ydotool

If a ydotool package is available:

sudo xbps-install ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

If ydotool is not available in your enabled repositories, use the Manual
ydotool Build section below.

---

# 🔷 NixOS

NixOS uses declarative package and service configuration instead of the
traditional package-manager workflow.

Add the required packages to your system or user configuration.

For a temporary shell, you can use:

nix-shell -p python3 python3Packages.pip ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

> A permanent NixOS installation should place the required packages and
> ydotool service configuration in your NixOS configuration.

---

# 🏔️ Alpine Linux

Install Python and basic build tooling:

sudo apk update
sudo apk add python3 py3-pip

Search for ydotool:

apk search ydotool

If available:

sudo apk add ydotool

Then:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py

If ydotool is not available in your repositories, use the Manual ydotool
Build section below.

---

# 🛠️ Manual ydotool Build

Some distributions or releases may not provide a sufficiently new ydotool
package.

The upstream ydotool project provides a CMake build system.

You will need:

- CMake 3.22+
- A C compiler
- A C++ compiler
- make
- scdoc for documentation builds

Clone upstream ydotool:

git clone https://github.com/ReimuNotMoe/ydotool.git
cd ydotool

Create the build:

mkdir build
cd build

cmake ..
make -j$(nproc)

Install:

sudo make install

Then verify:

ydotool --help
ydotoold --help

Recent ydotool releases require ydotoold for normal operation.

---

# 🔧 Verify ydotool

Check that the client exists:

command -v ydotool

Check that the daemon exists:

command -v ydotoold

Check the version:

ydotool --version

SolsRNGCore's main launcher can automatically start ydotoold when necessary.

---

# 🧩 Existing Installation

If you already downloaded or cloned SolsRNGCore:

cd ~/Downloads/SolsRNGCore
source .venv/bin/activate
python main.py

---

# 📁 Project Structure

SolsRNGCore/
├── main.py
├── README.md
├── requirements.txt
├── src/
│   └── solsrng_core/
│       ├── antiafk/
│       ├── diagnostics/
│       ├── discord/
│       ├── gui/
│       ├── config.py
│       └── logwatcher.py
└── library/
    └── biomes/

---

# 🛠️ Development

Compile the Python modules:

python -m py_compile main.py
python -m py_compile src/solsrng_core/logwatcher.py
python -m py_compile src/solsrng_core/gui/app.py
python -m py_compile src/solsrng_core/discord/webhook.py

The project is designed so network failures and Discord problems do not
directly freeze the GUI.

---

# 🧪 Project Status

SolsRNGCore is actively developed and tested primarily on Linux.

Current development areas include:

- Reliable live biome monitoring
- Discord notification reliability
- Anti-AFK stability
- Diagnostics
- Memory efficiency
- Steam Deck compatibility
- GUI stability
- Cross-distribution Linux support

---

# 🤝 Contributing

Bug reports, testing, ideas, and improvements are welcome.

When reporting a problem, useful information includes:

Operating system:
Distribution:
Distribution version:
SteamOS version if applicable:
Python version:
SolsRNGCore version / commit:
What happened:
Relevant logs:

Please remove Discord webhook tokens and other private information before
sharing logs.

---

# 🔐 Security

Never commit Discord webhook URLs, personal access tokens, passwords, or other
credentials to the repository.

Use local configuration for private data.

---

# 🌙 The Project

SolsRNGCore is built around a simple idea:

Keep Sol's RNG monitoring lightweight, reliable, Linux-friendly, and actually useful.

Built with ❤️ on Linux.

<p align="center">
🌙 <strong>SolsRNGCore</strong> 🌙
</p>

---

## 🔗 Links

GitHub:
https://github.com/69voidtheangel/SolsRNGCore

Project:
SolsRNGCore

Platform focus:
🐧 Linux • 🎮 SteamOS • 💻 Steam Deck

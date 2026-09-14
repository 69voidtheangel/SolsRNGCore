# 🌙 SolsRNGCore

> **A Linux-first Sol's RNG automation & Discord notification core.**

SolsRNGCore is a Linux-focused companion for **Sol's RNG**, built for long-running Roblox sessions with live biome monitoring, Discord notifications, Anti-AFK, item automation, diagnostics, and a PySide6 graphical interface.

**🐧 Linux First · 🎮 Steam Deck Ready · 💬 Discord Powered · 🌙 Midnight UI**

> ⚠️ **This project is actively developed. Expect bugs, especially on Linux configurations that haven't been tested yet.**

---

## ✨ Features

| Feature                          | Description                                                                   |
| -------------------------------- | ----------------------------------------------------------------------------- |
| 🌦️ **Live Biome Detection**     | Monitors Sober's Roblox logs for BloxstrapRPC `SetRichPresence` biome updates |
| 💬 **Multiple Discord Profiles** | Run independent webhook profiles with their own settings                      |
| 🎨 **Biome Artwork**             | Automatically uses the matching biome artwork for notifications               |
| 🔔 **Per-Biome Roles**           | Assign individual Discord role IDs to supported biomes                        |
| 👥 **@everyone Fallback**        | Optional fallback notifications for rare biomes                               |
| 🔗 **Private Server Links**      | Store a Roblox private-server URL per Discord profile                         |
| 💤 **Anti-AFK**                  | Configurable Anti-AFK support for Sober                                       |
| 🤖 **Item Automation**           | Automate Strange Controllers and Biome Randomizers                            |
| 🖥️ **PySide6 GUI**              | Configure the application through a graphical interface                       |
| 💾 **Persistent Configuration**  | Settings and profiles survive application restarts                            |
| 📜 **Diagnostics**               | Bounded logging designed for long-running sessions                            |
| 🚨 **Fatal Diagnostics**         | Useful information when unexpected application failures occur                 |
| 🧠 **RAM-Conscious Design**      | Prevents diagnostic history and queues from growing indefinitely              |

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore
```

## 2. Create a virtual environment

### Arch / SteamOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Debian / Ubuntu / Fedora and similar distributions

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Install the required input tools

SolsRNGCore uses:

* **`wdotool`** for KDE Wayland window management and mouse control
* **`ydotool`** for keyboard input

On Arch-based systems:

```bash
sudo pacman -Syu
sudo pacman -S python python-pip ydotool
cargo install wdotool
```

## 5. Launch

```bash
python main.py
```

On systems where Python is named `python3`:

```bash
python3 main.py
```

---

# 🎮 Steam Deck / SteamOS

SteamOS is one of the project's primary development and testing environments.

Install the required packages:

```bash
sudo pacman -Syu
sudo pacman -S python python-pip ydotool
```

Install `wdotool`:

```bash
cargo install wdotool
```

Then:

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python main.py
```

### KDE Wayland

KDE Wayland is supported through compositor-aware automation.

SolsRNGCore uses:

* `wdotool` — window focus, restoration, mouse movement, and clicking
* `ydotool` — keyboard input

Multi-monitor KDE Wayland setups are supported.

---

# 🌦


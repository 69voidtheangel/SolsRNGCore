# 🌙 SolsRNGCore

> **A Linux-first Sol's RNG automation & Discord notification core.**

SolsRNGCore is a Linux-focused companion for **Sol's RNG**, built for long-running Roblox sessions with live biome monitoring, Discord notifications, Anti-AFK, item automation, diagnostics, and a PySide6 graphical interface.

**🐧 Linux First · 🎮 Steam Deck Ready · 💬 Discord Powered · 🌙 Midnight UI**

> ⚠️ **This project is actively developed. Expect bugs, especially on configurations that have not been tested yet.**

---

# 🪟 Windows Port

A dedicated Windows port is now available in its own repository. The Windows repository contains the Windows installer build and is kept separate from the Linux-first source tree.

### 👉 Windows repository

**[SolsRNGCore-Windows](https://github.com/69voidtheangel/SolsRNGCore-Windows)**

The Windows repository's `main` branch is maintained as the distribution location for the Windows installer.

---

## ✨ Features

| Feature | Description |
| --- | --- |
| 🌦️ **Live Biome Detection** | Monitors Sober's Roblox logs for biome updates |
| 💬 **Multiple Discord Profiles** | Independent webhook profiles with their own settings |
| 🎨 **Biome Artwork** | Matching artwork for supported biome notifications |
| 🔔 **Per-Biome Roles** | Individual Discord role IDs for supported biomes |
| 👥 **@everyone Fallback** | Optional fallback notifications for rare biomes |
| 🔗 **Private Server Links** | Store a Roblox private-server URL per profile |
| 💤 **Anti-AFK** | Configurable Anti-AFK support |
| 🤖 **Item Automation** | Strange Controller and Biome Randomizer automation |
| 🖥️ **PySide6 GUI** | Graphical configuration and controls |
| 💾 **Persistent Configuration** | Settings survive application restarts |
| 📜 **Diagnostics** | Bounded logging for long-running sessions |
| 🚨 **Fatal Diagnostics** | Useful failure information when unexpected errors occur |
| 🧠 **RAM-Conscious Design** | Prevents diagnostic history and queues from growing indefinitely |

---

# 🐧 Linux Quick Start

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

On systems where Python is named `python3`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

For KDE Wayland automation, SolsRNGCore uses tools such as `wdotool` and `ydotool`.

---

# 🎮 Steam Deck / SteamOS

SteamOS is one of the project's primary development and testing environments.

```bash
sudo pacman -Syu
sudo pacman -S python python-pip ydotool
cargo install wdotool
```

Then launch the project normally with the Linux instructions above.

---

# 🌦️ Supported Biomes

```text
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
```

Repeated Rich Presence refreshes for the same biome are ignored so Discord does not get flooded with duplicate notifications.

---

# 💬 Discord Profiles

Each Discord webhook profile can have its own:

- Webhook URL
- Enabled / disabled state
- Biomes to notify
- Individual biome role IDs
- Optional `@everyone` fallback
- Roblox private-server URL
- Biome artwork configuration

Keep personal configuration and secrets out of the repository.

---

# 💤 Anti-AFK & Automation

SolsRNGCore includes configurable Anti-AFK support and Roblox item automation for long-running Sol's RNG sessions.

Current automation includes:

- Strange Controller
- Biome Randomizer
- Per-item cooldowns
- Shared coordinate configuration
- Inventory interaction
- Item searching and selection
- Game-window detection and restoration
- Start / Stop controls

---

# 🛠️ Development

Create a development environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

Before submitting changes, test the affected functionality on your target Linux environment.

---

# 🔐 Configuration & Privacy

Do not commit sensitive or machine-specific data, including:

- Discord webhook URLs
- Discord role IDs
- Saved profiles
- Roblox private-server URLs
- Automation coordinates
- Logs
- Cookies or session data
- Authentication tokens
- Machine-specific paths
- Virtual environments
- Python cache files

---

# 🤝 Contributing

Contributions are welcome.

Please read the repository's contribution, security, and code-of-conduct documentation before submitting changes.

---

## Project links

- **Main project:** https://github.com/69voidtheangel/SolsRNGCore
- **Windows port:** https://github.com/69voidtheangel/SolsRNGCore-Windows

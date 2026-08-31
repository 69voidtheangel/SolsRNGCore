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
| 🔔 Per-Biome Roles | Assign a Discord role ID to individual biomes |
| 👥 @everyone Fallback | Optional fallback notification for rare biomes |
| 🔗 Private Server Links | Store a Roblox private-server link per profile |
| 💤 Anti-AFK | Built-in Anti-AFK support for Sober |
| 🖥️ PySide6 GUI | Clean midnight-themed graphical interface |
| 💾 Persistent Configuration | Settings and profiles survive restarts |
| 📜 Live Diagnostics | Bounded logs for monitoring application activity |
| 🚨 Fatal Diagnostics | Unexpected failures can generate a compact diagnostic report |

---

## 🌦️ How Biome Detection Works

SolsRNGCore monitors Sober's Roblox logs and reads BloxstrapRPC SetRichPresence events.

Instead of reacting to every Rich Presence update, the monitor keeps track of the current biome and only reacts when the biome actually changes.

Example:

NORMAL → NORMAL → NORMAL

does not generate repeated Discord notifications.

But:

NORMAL → SNOWY

is a real biome transition and generates the appropriate notification.

This keeps Discord notifications tied to actual biome transitions instead of repeated Rich Presence refreshes.

---

## 🌦️ Supported Biomes

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

Profiles operate independently, allowing multiple servers to receive notifications simultaneously without sharing the same settings.

---

## 🔔 Discord Role Notifications

Every supported biome can have its own Discord role ID.

Example:

GLITCHED → <role ID>
DREAMSPACE → <role ID>
CYBERSPACE → <role ID>
SINGULARITY → <role ID>

When a role is configured, the notification can mention that role.

Profiles can also use the optional @everyone fallback for rare biomes when a specific role is not configured.

---

## 🎨 Biome Artwork

Biome images are stored in:

library/biomes/

The application uses the biome name to select the corresponding artwork for Discord notifications.

---

# 💤 Anti-AFK

SolsRNGCore includes configurable Anti-AFK support for Sober.

The Anti-AFK system operates independently from the biome monitor so biome detection and Anti-AFK activity do not need to interfere with each other.

### Current options

- Enable / disable Anti-AFK
- Configurable interval
- Configurable input method
- Window restoration support

---

# 📜 Diagnostics & Logging

SolsRNGCore includes bounded diagnostics so normal operation does not continuously consume memory.

The diagnostic system keeps only a limited number of recent messages in RAM and maintains bounded log output.

### Diagnostic levels

INFO
WARN
ERROR
FATAL

Important events can include:

- Sober biome monitor started
- Monitoring Sober log
- Sober current biome
- Sober biome changed
- Discord notification queued
- Discord notification sent
- Discord notification failed
- Anti-AFK activity
- Unexpected application errors

---

# 🚨 Fatal Error Diagnostics

SolsRNGCore includes fatal-error diagnostics for unexpected application termination.

A fatal diagnostic report can contain:

- Failure reason
- Basic system information
- Recent bounded diagnostics
- Python traceback when available

Sensitive webhook tokens are filtered from diagnostic output.

Native crashes such as SIGSEGV are handled separately from ordinary Python exceptions.

---

# 🧠 RAM & Performance

The diagnostic system is intentionally bounded.

The project avoids allowing:

- GUI logs to grow forever
- Diagnostic history to grow forever
- Discord work queues to grow without limits
- Old Sober log history to be repeatedly processed

The goal is to keep SolsRNGCore lightweight during long-running sessions, including extended AFK sessions on Steam Deck.

---

# 🐧 Linux First

SolsRNGCore is developed primarily on Linux, with SteamOS / Steam Deck being one of the main development environments.

The project is designed around Linux-first tooling and the Sober Roblox client.

---

# 🎮 Steam Deck

## Requirements

You will need:

- SteamOS / Linux
- Python 3
- pip
- ydotool / ydotoold
- Sober
- A configured Discord webhook

---

## 🚀 Installation

Clone the repository:

git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

Create the virtual environment:

python -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Launch:

python main.py

---

# 🧩 Running From an Existing Folder

If you already downloaded the repository:

cd ~/Downloads/SolsRNGCore
source .venv/bin/activate
python main.py

---

# 🛠️ Development

Compile the Python modules:

python -m py_compile main.py
python -m py_compile src/solsrng_core/logwatcher.py
python -m py_compile src/solsrng_core/gui/app.py
python -m py_compile src/solsrng_core/discord/webhook.py

The project is intended to fail safely wherever possible.

Discord/network failures should not freeze the GUI, and diagnostics should never become the reason the application crashes.

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

# 🧪 Project Status

SolsRNGCore is actively developed and tested primarily on Linux.

Current development focuses on:

- Reliable live biome monitoring
- Discord notification reliability
- Anti-AFK stability
- Diagnostics
- Memory efficiency
- Steam Deck compatibility
- GUI stability

---

# 🤝 Contributing

Bug reports, testing, ideas, and improvements are welcome.

When reporting a problem, useful information includes:

Operating system:
SteamOS version:
Python version:
SolsRNGCore version / commit:
What happened:
Relevant logs:

Please remove Discord webhook tokens or other private information before sharing logs.

---

# 🔐 Security

Never commit your Discord webhook URLs, personal access tokens, passwords, or other credentials to the repository.

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

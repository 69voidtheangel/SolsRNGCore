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

# 🌦️ Live Biome Monitoring

SolsRNGCore watches Sober's Roblox logs for BloxstrapRPC `SetRichPresence` events.

The monitor maintains one authoritative current-biome state.

Repeated Rich Presence updates such as:

```text
NORMAL → NORMAL → NORMAL → NORMAL
```

are ignored.

Actual biome transitions such as:

```text
NORMAL → SNOWY
```

are processed immediately.

This prevents repeated Rich Presence refreshes from flooding Discord with duplicate notifications.

## Supported Biomes

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

---

# 💬 Discord Profiles

Each Discord webhook profile can operate independently.

### Per-profile configuration

* Webhook URL
* Enabled / disabled state
* Biomes to notify
* Individual biome role IDs
* Optional `@everyone` fallback
* Roblox private-server URL
* Biome artwork directory

This allows different profiles to notify different Discord servers or channels without sharing notification settings.

### 🔔 Role Notifications

Supported biomes can have individual Discord role IDs.

For example:

```text
GLITCHED
DREAMSPACE
CYBERSPACE
SINGULARITY
```

can each have their own role.

An optional `@everyone` fallback can also be configured for rare biome notifications.

---

# 🎨 Biome Artwork

Biome artwork is stored in:

```text
library/biomes/
```

When a supported biome is detected, SolsRNGCore can select its corresponding artwork for the Discord notification.

---

# 💤 Anti-AFK

SolsRNGCore includes configurable Anti-AFK support for Sober.

Available configuration includes:

* Enable / disable Anti-AFK
* Configurable interval
* Configurable input method
* Window restoration

Anti-AFK operates independently from biome monitoring.

---

# 🤖 Item Automation

SolsRNGCore includes a built-in Roblox item automation system designed for long-running Sol's RNG sessions.

Currently supported automation includes:

* 🎛️ **Strange Controller**
* 🌦️ **Biome Randomizer**
* ⏱️ Per-item cooldowns
* 📍 Shared coordinate configuration
* 🎒 Inventory interaction
* 🔎 Item searching
* 🎯 First-slot selection
* 🔢 Quantity selection
* ▶️ Item usage
* ❌ Inventory closing
* 🪟 Game-window detection
* 🔄 Window restoration
* 🧪 Automation testing
* ▶️ Start / Stop controls

All automation items use the same coordinate configuration rather than requiring a separate coordinate layout for every item.

## ⚡ Automation Priority

When Anti-AFK and item automation are running together, execution priority is:

```text
1. Anti-AFK
2. Strange Controller
3. Biome Randomizer
```

Automation tasks do not interrupt one another.

A running automation cycle finishes its complete sequence before another automation task takes control.

This prevents multiple automation systems from fighting over Roblox focus and input.

---

# 🖥️ KDE Wayland & Multi-Monitor Support

SolsRNGCore was designed around real Linux desktop automation rather than assuming X11-only behavior.

For KDE Wayland:

```text
wdotool
    ↓
Window focus / restoration
Mouse movement / clicking

ydotool
    ↓
Keyboard input
```

The automation system is designed to work across multi-monitor KDE Wayland setups.

---

# 📜 Diagnostics & Logging

SolsRNGCore includes bounded diagnostic logging for long-running sessions.

Diagnostic levels include:

```text
INFO
WARN
ERROR
FATAL
```

Important events can include:

* Monitor startup
* Sober log rotation
* Biome detection
* Biome transitions
* Discord queue activity
* Discord success / failure
* Anti-AFK activity
* Automation activity
* Application exceptions
* Fatal diagnostics

The diagnostic system intentionally avoids allowing application history to grow without limits.

---

# 🚨 Fatal Diagnostics

When an unexpected application failure occurs, SolsRNGCore can provide useful diagnostic information such as:

* Failure reason
* Basic system information
* Recent diagnostic messages
* Python traceback when available

Sensitive information such as Discord webhook credentials should **never** be stored in diagnostic output.

Native crashes such as `SIGSEGV` are separate from ordinary Python exceptions and may instead be reported by the operating system.

---

# 🧠 Long-Running Session Design

SolsRNGCore is intended to stay running for extended periods.

The application is designed to prevent:

* GUI logs from growing forever
* Diagnostic history from growing forever
* Discord work from creating an unlimited queue
* Old Sober log history from being repeatedly processed

The goal is to remain lightweight during extended AFK sessions, including Steam Deck usage.

---

# 🐧 Linux Support

SolsRNGCore is **Linux-first**.

Primary development and testing currently focus on:

* 🟢 SteamOS
* 🟢 Arch Linux

The project is also intended for other modern Linux distributions, including:

* Debian
* Ubuntu
* Linux Mint
* Pop!_OS
* Fedora
* openSUSE
* Manjaro
* EndeavourOS
* CachyOS
* Bazzite
* Gentoo
* Void Linux
* NixOS
* Alpine Linux

> Package names, service configuration, and Wayland behavior can vary between distributions and releases.

---

# 📦 Distribution Notes

## Arch / SteamOS / Manjaro / EndeavourOS / CachyOS

```bash
sudo pacman -Syu
sudo pacman -S python python-pip ydotool
cargo install wdotool
```

Then install the project:

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

---

## Debian / Ubuntu / Linux Mint

Install Python, virtual-environment support, and the input tools using your distribution's package manager.

For Debian-based systems:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ydotool
```

If your release provides `ydotoold` separately:

```bash
sudo apt install ydotoold
```

Then:

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

---

## Fedora / Bazzite

```bash
sudo dnf install python3 python3-pip ydotool
```

Then:

```bash
git clone https://github.com/69voidtheangel/SolsRNGCore.git
cd SolsRNGCore

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

> Bazzite is image-based, so package-management and persistence behavior can differ from conventional Fedora installations.

---

## openSUSE

```bash
sudo zypper refresh
sudo zypper install python3 python3-pip ydotool
```

Then install SolsRNGCore using the standard Python setup above.

---

## Gentoo

Search for `ydotool` in your configured repositories:

```bash
sudo emerge --sync
emerge --search ydotool
```

If available:

```bash
sudo emerge app-misc/ydotool
sudo emerge dev-lang/python
```

Then install SolsRNGCore normally.

---

## Void Linux

```bash
sudo xbps-install -S
sudo xbps-install python3 python3-pip
```

Search for `ydotool`:

```bash
xbps-query -Rs ydotool
```

If available:

```bash
sudo xbps-install ydotool
```

Then install SolsRNGCore normally.

---

## NixOS

NixOS uses declarative configuration rather than the traditional package-manager workflow.

For a temporary environment:

```bash
nix-shell -p python3 python3Packages.pip ydotool
```

Then install SolsRNGCore normally.

A permanent setup should configure the required packages and input services through your NixOS configuration.

---

## Alpine Linux

```bash
sudo apk update
sudo apk add python3 py3-pip
```

Search for `ydotool`:

```bash
apk search ydotool
```

If available:

```bash
sudo apk add ydotool
```

Then install SolsRNGCore normally.

---

# 🛠️ Manual ydotool Build

If your distribution does not provide a usable `ydotool` package, build it from upstream.

You will generally need:

* CMake 3.22+
* C compiler
* C++ compiler
* `make`
* `scdoc`

Clone the upstream project:

```bash
git clone https://github.com/ReimuNotMoe/ydotool.git
cd ydotool
```

Build:

```bash
mkdir build
cd build

cmake ..
make -j"$(nproc)"
```

Install:

```bash
sudo make install
```

Verify:

```bash
ydotool --help
ydotoold --help
```

Recent versions of `ydotool` require `ydotoold` for normal operation.

---

# 🔍 Verify ydotool

Check the client:

```bash
command -v ydotool
```

Check the daemon:

```bash
command -v ydotoold
```

Check the version:

```bash
ydotool --version
```

SolsRNGCore's launcher can automatically start `ydotoold` when necessary.

---

# 📁 Project Structure

```text
SolsRNGCore/
├── .github/
│   └── ISSUE_TEMPLATE/
├── assets/
├── bin/
├── library/
│   └── biomes/
├── src/
│   └── solsrng_core/
│       ├── antiafk/
│       ├── diagnostics/
│       ├── discord/
│       ├── gui/
│       ├── automation/
│       ├── config.py
│       └── logwatcher.py
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

# 🛠️ Development

Create and activate a development environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Compile the main Python modules:

```bash
python -m py_compile main.py
python -m py_compile src/solsrng_core/logwatcher.py
python -m py_compile src/solsrng_core/gui/app.py
python -m py_compile src/solsrng_core/discord/webhook.py
```

Before submitting changes, make sure the application still launches and that the affected feature works on your target Linux environment.

---

# 🔐 Configuration & Privacy

Local configuration may contain sensitive or machine-specific information.

**Do not commit:**

* Discord webhook URLs
* Discord role IDs
* Server-specific configuration
* Saved profiles
* Roblox private-server URLs
* Automation coordinates
* Local runtime configuration
* Logs
* Cookies or session data
* Authentication tokens
* Machine-specific paths
* Virtual environments
* Python cache files

Keep personal configuration in your local configuration directory rather than inside the repository.

---

# 🤝 Contributing

Contributions are welcome.

Before opening an issue or pull request, please read:

* [`CONTRIBUTING.md`](CONTRIBUTING.md)
* [`SECURITY.md`](SECURITY.md)
* [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)

Bug reports, compatibility reports, documentation improvements, testing, and feature ideas are all useful.

---

# 🛡️ Security

If you discover a security issue, please follow the instructions in [`SECURITY.md`](SECURITY.md) rather than publicly posting sensitive credentials or private configuration.

**Never post Discord webhook URLs, authentication tokens, cookies, or other secrets in an issue.**

---

# 📜 License

SolsRNGCore is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

# 🌐 Project Links

* **Repository:** https://github.com/69voidtheangel/SolsRNGCore
* **Wiki:** https://sol-rng.fandom.com/wiki/Macros/SolsRNGCore
* **Issues:** https://github.com/69voidtheangel/SolsRNGCore/issues

---

## 🌙 Status

SolsRNGCore is an actively developed Linux-first Sol's RNG project.

The primary goal is simple:

> **Make Sol's RNG automation and notifications work properly on Linux—especially on the Steam Deck.**

🐧 Linux first.
🎮 Steam Deck ready.
💬 Discord powered.
🌙 Built for long sessions.

**Expect bugs. We're building it anyway.**

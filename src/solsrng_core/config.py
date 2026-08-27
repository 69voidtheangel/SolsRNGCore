from __future__ import annotations
from dataclasses import asdict, dataclass, field
from pathlib import Path
import json, os
from typing import Any

CONFIG_DIR = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'solsrng'
CONFIG_PATH = CONFIG_DIR / 'core.json'

NORMAL_BIOMES = ['NORMAL','WINDY','SNOWY','RAINY','SANDSTORM','HELL','STARFALL','HEAVEN','CORRUPTION','NULL']
EVENT_BIOMES = ['PUMPKIN MOON','GRAVEYARD','BLAZING SUN','BLOOD RAIN','AURORA','EGGLAND']
RARE_BIOMES = {'DREAMSPACE','GLITCHED','CYBERSPACE','SINGULARITY'}
RARE_LIST = ['GLITCHED','DREAMSPACE','CYBERSPACE','SINGULARITY']
BIOMES = NORMAL_BIOMES + EVENT_BIOMES + RARE_LIST

@dataclass
class WebhookProfile:
    name: str = 'Main Server'
    enabled: bool = False
    url: str = ''
    notify_biomes: list[str] = field(default_factory=lambda: list(BIOMES))
    # One Discord role per biome. Empty string means "do not ping a role".
    biome_roles: dict[str, str] = field(default_factory=lambda: {b: '' for b in BIOMES})
    # Rare fallback keeps the old @everyone behavior available without randomization.
    rare_everyone_fallback: bool = False
    roblox_private_server_url: str = ''
    biome_image_dir: str = 'library/biomes'

@dataclass
class AntiAFKConfig:
    enabled: bool = False
    interval_seconds: float = 120.0
    game_title_regex: str = ''
    anti_afk_key: str = 'space'

@dataclass
class AppConfig:
    profiles: list[WebhookProfile] = field(default_factory=lambda: [WebhookProfile()])
    active_profile: int = 0
    anti_afk: AntiAFKConfig = field(default_factory=AntiAFKConfig)
    theme: str = 'midnight'


def _coerce_roles(raw: Any) -> dict[str, str]:
    roles = {b: '' for b in BIOMES}
    if isinstance(raw, dict):
        for biome in BIOMES:
            value = raw.get(biome, '')
            roles[biome] = str(value).strip() if value is not None else ''
    return roles


def _profile_from_dict(d: dict[str, Any]) -> WebhookProfile:
    # Migrate from older builds that used a single rare-role list / random mode.
    old_rare = d.get('rare', {}) if isinstance(d.get('rare', {}), dict) else {}
    old_roles = [str(x).strip() for x in old_rare.get('role_ids', []) if str(x).strip()]
    roles = _coerce_roles(d.get('biome_roles', {}))
    for rare, role in zip(RARE_LIST, old_roles):
        if not roles.get(rare):
            roles[rare] = role

    notify = [str(x).upper() for x in d.get('notify_biomes', BIOMES) if str(x).upper() in BIOMES]
    if not notify:
        notify = list(BIOMES)

    return WebhookProfile(
        name=str(d.get('name', 'Main Server')),
        enabled=bool(d.get('enabled', True)),
        url=str(d.get('url', '')),
        notify_biomes=notify,
        biome_roles=roles,
        rare_everyone_fallback=bool(d.get('rare_everyone_fallback', False)),
        roblox_private_server_url=str(d.get('roblox_private_server_url', '')),
        biome_image_dir=str(d.get('biome_image_dir', 'library/biomes')),
    )


def _from_dict(data: dict[str, Any]) -> AppConfig:
    if 'profiles' in data:
        profiles = [_profile_from_dict(x) for x in data.get('profiles', [])]
        if not profiles:
            profiles = [WebhookProfile()]
    elif 'webhook' in data:
        old = data.get('webhook', {})
        profiles = [_profile_from_dict({'name': 'Main Server', **old})]
    else:
        profiles = [WebhookProfile()]

    a = data.get('anti_afk', {})
    return AppConfig(
        profiles=profiles,
        active_profile=max(0, min(int(data.get('active_profile', 0)), len(profiles) - 1)),
        anti_afk=AntiAFKConfig(
            enabled=bool(a.get('enabled', True)),
            interval_seconds=float(a.get('interval_seconds', 120)),
            game_title_regex=str(a.get('game_title_regex', '')),
            anti_afk_key=str(a.get('anti_afk_key', 'space')),
        ),
        theme=str(data.get('theme', 'midnight')),
    )


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return AppConfig()
    try:
        return _from_dict(json.loads(CONFIG_PATH.read_text()))
    except (OSError, ValueError, TypeError, KeyError):
        return AppConfig()


def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=2))

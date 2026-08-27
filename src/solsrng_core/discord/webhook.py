from __future__ import annotations
import json, mimetypes, re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import requests
from solsrng_core.config import BIOMES, RARE_BIOMES, WebhookProfile

@dataclass
class WebhookResult:
    ok: bool
    status: int | None = None
    error: str | None = None


def _norm(v: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', re.sub(r'\.(png|jpe?g|webp|gif)$', '', v.strip().lower()))


class DiscordWebhook:
    def __init__(self, profile: WebhookProfile):
        self.profile = profile

    def _urls(self) -> list[str]:
        return list(dict.fromkeys([
            p.strip() for p in re.split(r'[,;\n\s]+', self.profile.url or '') if p.strip()
        ]))

    def _role_mention(self, biome: str) -> tuple[str, list[str]]:
        role_id = self.profile.biome_roles.get(biome, '').strip()
        if role_id.isdigit():
            return f'<@&{role_id}>', [role_id]
        if biome in RARE_BIOMES and self.profile.rare_everyone_fallback:
            return '@everyone', []
        return '', []

    def _image(self, biome: str):
        p = Path(self.profile.biome_image_dir).expanduser()
        roots = [p] if p.is_absolute() else [Path.cwd()/p, Path(__file__).resolve().parents[3]/p]
        exts = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
        target = _norm(biome)
        for root in roots:
            if root.is_dir():
                for f in root.iterdir():
                    if f.is_file() and f.suffix.lower() in exts and _norm(f.name) == target:
                        return f
        return None

    def send_biome(self, biome: str, *, duration: str|None = None, details: str|None = None):
        biome = biome.strip().upper()
        urls = self._urls()
        if not self.profile.enabled or not urls:
            return WebhookResult(False, error='Profile disabled or no webhook URL')
        if biome not in BIOMES:
            return WebhookResult(False, error=f'Unknown biome {biome!r}')
        if biome not in self.profile.notify_biomes:
            return WebhookResult(False, error=f'Biome {biome!r} disabled')

        desc = f"Sol's RNG detected **{biome}**."
        if duration:
            desc += f'\nDuration: **{duration}**'
        if details:
            desc += f'\n{details}'
        if self.profile.roblox_private_server_url:
            desc += f'\n\n[Join Roblox Private Server]({self.profile.roblox_private_server_url})'

        mention, role_ids = self._role_mention(biome)
        image = self._image(biome)
        successes = 0
        errors = []
        last = None

        for url in urls:
            embed = {
                'title': f'Biome detected: {biome}',
                'description': desc,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'footer': {
                    'text': f"Sol's RNG Core • {self.profile.name} • github.com/69voidtheangel/SolsRNGCore",
                    'icon_url': 'https://raw.githubusercontent.com/69voidtheangel/SolsRNGCore/main/assets/solsrng_core_logo.svg'
                },
            }
            payload = {
                'content': mention,
                'allowed_mentions': {
                    'parse': ['everyone'] if mention == '@everyone' else [],
                    'roles': role_ids,
                },
                'embeds': [embed],
            }
            opened = None
            try:
                if image:
                    embed['thumbnail'] = {'url': f'attachment://{image.name}'}
                    opened = image.open('rb')
                    resp = requests.post(
                        url,
                        data={'payload_json': json.dumps(payload)},
                        files={'file': (image.name, opened, mimetypes.guess_type(image.name)[0] or 'application/octet-stream')},
                        timeout=10,
                    )
                else:
                    resp = requests.post(url, json=payload, timeout=10)
                last = resp.status_code
                if 200 <= resp.status_code < 300:
                    successes += 1
                else:
                    errors.append(f'{resp.status_code}: {resp.text[:150]}')
            except (requests.RequestException, OSError) as e:
                errors.append(str(e))
            finally:
                if opened:
                    opened.close()

        if successes == len(urls):
            return WebhookResult(True, status=last)
        if successes:
            return WebhookResult(True, status=last, error=f'Sent to {successes}/{len(urls)} webhooks: {" | ".join(errors)}')
        return WebhookResult(False, status=last, error=' | '.join(errors))

    def test(self):
        return self.send_biome('NORMAL', details=f'Test notification for profile: {self.profile.name}')

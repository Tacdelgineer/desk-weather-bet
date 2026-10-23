"""Minimal Kalshi API client. Keys live outside the repo (~/.kalshi). Never print keys or account details."""
import base64
import time
from pathlib import Path

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

HOSTS = {"prod": "https://api.elections.kalshi.com", "demo": "https://demo-api.kalshi.co"}
PREFIX = "/trade-api/v2"
KEYDIR = Path.home() / ".kalshi"


def has_keys(env="prod"):
    return (KEYDIR / f"{env}.pem").exists() and (KEYDIR / f"{env}_key_id").exists()


class Kalshi:
    def __init__(self, env="prod", auth=True):
        self.base = HOSTS[env]
        self.kid = self.key = None
        if auth:
            self.kid = (KEYDIR / f"{env}_key_id").read_text().strip()
            self.key = serialization.load_pem_private_key((KEYDIR / f"{env}.pem").read_bytes(), password=None)
        self.s = requests.Session()

    def _headers(self, method, path):
        if not self.key:
            return {}
        ts = str(int(time.time() * 1000))
        msg = (ts + method + path).encode()
        if isinstance(self.key, rsa.RSAPrivateKey):
            sig = self.key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                 salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
        else:  # Ed25519
            sig = self.key.sign(msg)
        return {"KALSHI-ACCESS-KEY": self.kid, "KALSHI-ACCESS-TIMESTAMP": ts,
                "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode()}

    def request(self, method, path, params=None, json=None, tries=5):
        full = PREFIX + path
        for i in range(tries):
            r = self.s.request(method, self.base + full, params=params, json=json, timeout=30,
                               headers=self._headers(method, full))
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(1.5 * (i + 1))
                continue
            if r.status_code >= 400:
                body = r.text.replace(self.kid, "<key-id>") if self.kid else r.text
                raise RuntimeError(f"Kalshi {method} {path} -> HTTP {r.status_code}: {body[:300]}")
            return r.json()
        raise RuntimeError(f"Kalshi {method} {path}: retries exhausted")

    def get(self, path, **params):
        return self.request("GET", path, params=params)

    def paged(self, path, key, **params):
        cursor = None
        while True:
            p = dict(params, limit=params.get("limit", 1000))
            if cursor:
                p["cursor"] = cursor
            d = self.get(path, **p)
            yield from d.get(key, [])
            cursor = d.get("cursor")
            if not cursor:
                break

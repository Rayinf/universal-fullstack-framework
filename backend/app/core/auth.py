from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class JwtTokenCodec:
  secret: str
  algorithm: str = 'HS256'

  def _b64url_encode(self, raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')

  def _b64url_decode(self, raw: str) -> bytes:
    padding = '=' * (-len(raw) % 4)
    return base64.urlsafe_b64decode(f'{raw}{padding}')

  def _sign_token_part(self, raw: str) -> str:
    signature = hmac.new(self.secret.encode('utf-8'), raw.encode('utf-8'), hashlib.sha256).digest()
    return self._b64url_encode(signature)

  def build_token(self, user_id: str, token_type: str, expire_seconds: int) -> str:
    now_ts = int(datetime.now().timestamp())
    payload = {
      'sub': str(user_id),
      'type': token_type,
      'iat': now_ts,
      'exp': now_ts + max(expire_seconds, 60),
      'jti': secrets.token_hex(8),
    }
    header = {'alg': self.algorithm, 'typ': 'JWT'}
    header_part = self._b64url_encode(json.dumps(header, separators=(',', ':'), sort_keys=True).encode('utf-8'))
    payload_part = self._b64url_encode(json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8'))
    signing_input = f'{header_part}.{payload_part}'
    signature_part = self._sign_token_part(signing_input)
    return f'{signing_input}.{signature_part}'

  def parse_token(self, token: str, expected_type: str = 'access') -> dict[str, Any] | None:
    try:
      parts = token.split('.')
      if len(parts) != 3:
        return None
      signing_input = f'{parts[0]}.{parts[1]}'
      expected_signature = self._sign_token_part(signing_input)
      if not hmac.compare_digest(parts[2], expected_signature):
        return None
      payload_bytes = self._b64url_decode(parts[1])
      payload = json.loads(payload_bytes.decode('utf-8'))
      if payload.get('type') != expected_type:
        return None
      exp = int(payload.get('exp', 0))
      if exp <= int(datetime.now().timestamp()):
        return None
      sub = str(payload.get('sub', '')).strip()
      if not sub:
        return None
      return payload
    except (ValueError, TypeError, json.JSONDecodeError):
      return None


@dataclass(frozen=True)
class PasswordManager:
  prefix: str
  iterations: int

  def is_password_hashed(self, password: str) -> bool:
    return password.startswith(f'{self.prefix}$')

  def hash_password(self, raw_password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
      'sha256',
      raw_password.encode('utf-8'),
      salt.encode('utf-8'),
      self.iterations,
    )
    return f'{self.prefix}${self.iterations}${salt}${dk.hex()}'

  def verify_password(self, raw_password: str, stored_password: str) -> bool:
    if not stored_password:
      return False
    if not self.is_password_hashed(stored_password):
      return hmac.compare_digest(raw_password, stored_password)

    try:
      _, iter_text, salt, hashed_hex = stored_password.split('$', 3)
      iterations = int(iter_text)
      candidate = hashlib.pbkdf2_hmac(
        'sha256',
        raw_password.encode('utf-8'),
        salt.encode('utf-8'),
        max(iterations, 1),
      ).hex()
      return hmac.compare_digest(candidate, hashed_hex)
    except (ValueError, TypeError):
      return False

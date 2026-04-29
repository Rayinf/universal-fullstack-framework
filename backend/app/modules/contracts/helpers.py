from __future__ import annotations

import uuid
from datetime import datetime


def generate_contract_no() -> str:
  return f'CT-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'


def generate_payment_no() -> str:
  return f'PM-{datetime.now().strftime("%Y%m%d%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'

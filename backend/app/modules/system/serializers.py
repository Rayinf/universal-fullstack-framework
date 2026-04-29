from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthDocData(BaseModel):
  status: str = Field(description='服务状态')
  dbDriver: str = Field(description='数据库驱动类型')


class HealthDocResponse(BaseModel):
  code: int = Field(description='业务状态码，0表示成功')
  msg: str = Field(description='提示信息')
  data: HealthDocData | None = Field(default=None, description='业务数据')


def build_health_payload(db_driver: str) -> dict[str, str]:
  return {'status': 'ok', 'dbDriver': db_driver}


def build_token_response(access_token: str, refresh_token: str) -> dict[str, str]:
  return {
    'token_type': 'Bearer',
    'access_token': access_token,
    'refresh_token': refresh_token,
  }


def serialize_system_config(row: Any) -> dict[str, str]:
  return {
    'companyName': row['company_name'] if row else '本地制造企业',
    'systemName': row['system_name'] if row else 'MES本地版',
    'version': row['version'] if row else '1.0.0',
  }

from __future__ import annotations

import time
from typing import Dict

# 简单的内存会话管理器，用于实现单点登录（互踢机制）
class SessionManager:
    def __init__(self):
        # 记录用户ID和其当前有效的 Token 签发时间（或Token签名）
        # 结构: { user_id: { "iat": int, "token_signature": str } }
        self._active_sessions: Dict[str, Dict[str, any]] = {}

    def register_session(self, user_id: str, iat: int, token_signature: str) -> None:
        """
        当用户成功登录并发放新Token时，注册此会话
        这会覆盖该用户之前的任何会话记录，从而实现“后登录踢掉先登录”
        """
        self._active_sessions[str(user_id)] = {
            "iat": iat,
            "token_signature": token_signature
        }

    def is_session_valid(self, user_id: str, iat: int, token_signature: str) -> bool:
        """
        检查传入的Token是否是该用户当前最新的/活跃的会话
        """
        uid = str(user_id)
        if uid not in self._active_sessions:
            # 如果没有记录，通常是系统重启，放行
            return True
        
        active_session = self._active_sessions[uid]
        # 判断：如果传入的token签名与记录的最新签名不一致，说明它是一个旧的或者在别处签发的token
        if active_session["token_signature"] != token_signature:
            return False
            
        return True

    def clear_session(self, user_id: str) -> None:
        """用户主动登出时清除会话"""
        self._active_sessions.pop(str(user_id), None)

# 单例
session_manager = SessionManager()

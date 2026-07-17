"""Environment-configured API-key authentication for the reference beta."""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from typing import Any


class AuthConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Principal:
    actor: str
    roles: frozenset[str]


class ApiKeyAuth:
    ALLOWED_ROLES = frozenset({"viewer", "operator", "approver", "auditor", "admin"})

    def __init__(self, keys: dict[str, Principal]) -> None:
        self.keys = keys

    @classmethod
    def from_mapping(cls, mapping: dict[str, dict[str, Any]]) -> "ApiKeyAuth":
        keys: dict[str, Principal] = {}
        for token, details in mapping.items():
            actor = str(details.get("actor", "")).strip()
            roles = frozenset(str(role) for role in details.get("roles", []))
            if len(token) < 16 or not actor or not roles:
                raise AuthConfigurationError("Each API key needs at least 16 characters, an actor, and roles")
            if not roles.issubset(cls.ALLOWED_ROLES):
                raise AuthConfigurationError("API key contains an unknown role")
            keys[token] = Principal(actor, roles)
        return cls(keys)

    @classmethod
    def from_environment(cls) -> "ApiKeyAuth":
        raw = os.getenv("DECISION360_API_KEYS", "")
        if not raw:
            return cls({})
        try:
            mapping = json.loads(raw)
        except json.JSONDecodeError as error:
            raise AuthConfigurationError("DECISION360_API_KEYS must be valid JSON") from error
        if not isinstance(mapping, dict):
            raise AuthConfigurationError("DECISION360_API_KEYS must be a JSON object")
        return cls.from_mapping(mapping)

    def authenticate(self, supplied: str | None) -> Principal | None:
        if not supplied:
            return None
        for token, principal in self.keys.items():
            if hmac.compare_digest(token, supplied):
                return principal
        return None

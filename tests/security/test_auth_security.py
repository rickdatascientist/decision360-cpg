import os
import unittest
from unittest.mock import patch

from decision360.auth import ApiKeyAuth, AuthConfigurationError


class AuthSecurityTests(unittest.TestCase):
    def test_short_key_and_unknown_role_are_rejected(self) -> None:
        with self.assertRaises(AuthConfigurationError):
            ApiKeyAuth.from_mapping({"short": {"actor": "x", "roles": ["operator"]}})
        with self.assertRaises(AuthConfigurationError):
            ApiKeyAuth.from_mapping({"long-enough-token-1": {"actor": "x", "roles": ["superuser"]}})

    def test_invalid_environment_json_fails_closed(self) -> None:
        with patch.dict(os.environ, {"DECISION360_API_KEYS": "not-json"}):
            with self.assertRaises(AuthConfigurationError):
                ApiKeyAuth.from_environment()

    def test_authentication_does_not_accept_prefixes(self) -> None:
        auth = ApiKeyAuth.from_mapping({"exact-token-00001": {"actor": "x", "roles": ["viewer"]}})
        self.assertIsNone(auth.authenticate("exact-token"))
        self.assertIsNotNone(auth.authenticate("exact-token-00001"))


if __name__ == "__main__":
    unittest.main()

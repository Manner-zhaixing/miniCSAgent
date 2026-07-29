from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import yaml
from pydantic import ValidationError

from mini_cs_agent.core.config import load_config


class LoadConfigTests(TestCase):
    def write_config(self, directory: str, data: dict) -> Path:
        path = Path(directory) / "config.yaml"
        path.write_text(
            yaml.safe_dump(data, sort_keys=False),
            encoding="utf-8",
        )
        return path

    def base_config(self) -> dict:
        return {
            "active_model": "deepseek",
            "models": {
                "deepseek": {
                    "provider": "deepseek",
                    "model": "deepseek-v4-pro",
                    "api_key": "test-key",
                }
            },
        }

    def test_loads_selected_model(self):
        with TemporaryDirectory() as directory:
            config = load_config(self.write_config(directory, self.base_config()))

        self.assertEqual(config.active_model, "deepseek")
        self.assertEqual(config.selected_model.model, "deepseek-v4-pro")
        self.assertEqual(
            config.selected_model.api_key.get_secret_value(),
            "test-key",
        )

    def test_rejects_unknown_active_model(self):
        data = self.base_config()
        data["active_model"] = "missing"

        with TemporaryDirectory() as directory:
            with self.assertRaises(ValidationError):
                load_config(self.write_config(directory, data))

    def test_requires_key_only_for_active_model(self):
        data = self.base_config()
        data["models"]["unused"] = {
            "provider": "openai",
            "model": "unused-model",
            "api_key": "",
        }

        with TemporaryDirectory() as directory:
            config = load_config(self.write_config(directory, data))

        self.assertEqual(config.active_model, "deepseek")

    def test_rejects_reserved_option(self):
        data = self.base_config()
        data["models"]["deepseek"]["options"] = {"api_key": "override"}

        with TemporaryDirectory() as directory:
            with self.assertRaises(ValidationError):
                load_config(self.write_config(directory, data))

"""Configuration tests."""

from __future__ import annotations

from nanoclaw.core.config import Config


def test_get_active_provider_azure_foundry() -> None:
    """Config should resolve azureFoundry as azure_openai provider."""
    config = Config.model_validate(
        {
            "providers": {
                "azureFoundry": {
                    "apiKey": "k",
                    "endpoint": "https://example.openai.azure.com",
                    "deployment": "gpt-4o-mini",
                    "apiVersion": "2024-10-21",
                }
            }
        }
    )

    provider, api_key, model, base_url, api_version = config.get_active_provider()
    assert provider == "azure_openai"
    assert api_key == "k"
    assert model == "gpt-4o-mini"
    assert base_url == "https://example.openai.azure.com"
    assert api_version == "2024-10-21"

"""Configuration management for Gaggimate MCP server."""

from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GaggimateConfig(BaseSettings):
    """Gaggimate MCP server configuration with validation."""

    model_config = SettingsConfigDict(
        env_prefix="GAGGIMATE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
        populate_by_name=True,
    )

    # Connection settings
    # Explicit aliases avoid doubling env_prefix for these historical field names.
    # Retain the old double-prefixed variables for existing installations.
    gaggimate_host: str = Field(
        default="gaggimate.local",
        validation_alias=AliasChoices("GAGGIMATE_HOST", "GAGGIMATE_GAGGIMATE_HOST"),
    )
    gaggimate_protocol: str = Field(
        default="ws",
        validation_alias=AliasChoices("GAGGIMATE_PROTOCOL", "GAGGIMATE_GAGGIMATE_PROTOCOL"),
    )
    # Per-attempt HTTP request timeout (seconds). Sized for the full .slog
    # shot-log download over a weak link, not just a quick API call.
    request_timeout: float = 12.0
    # Retries (after the first attempt) for idempotent HTTP reads on timeout /
    # transient connection errors. Total attempts = request_retries + 1.
    request_retries: int = 2

    # Safety limits
    max_temperature: float = 100.0
    min_temperature: float = 25.0
    max_pressure: float = 12.0
    min_pressure: float = 0.0

    # Storage
    profiles_dir: Path = Path("./profiles")
    storage_path: Path = Path("./data")

    # Agent settings
    ai_profile_suffix: str = " [AI]"
    ai_notes_prefix: str = "[Updated by AI]: "

    # Observability
    log_level: str = "INFO"
    enable_metrics: bool = True

    @property
    def host(self) -> str:
        """Get host (alias for gaggimate_host)."""
        return self.gaggimate_host

    @property
    def use_https(self) -> bool:
        """Check if HTTPS/WSS should be used."""
        return self.gaggimate_protocol == "wss"

    @property
    def websocket_url(self) -> str:
        """Generate WebSocket URL from configuration."""
        return f"{self.gaggimate_protocol}://{self.gaggimate_host}/ws"

    @property
    def http_base_url(self) -> str:
        """Generate HTTP base URL from configuration."""
        protocol = "https" if self.gaggimate_protocol == "wss" else "http"
        return f"{protocol}://{self.gaggimate_host}"

    def validate_temperature(self, temp: float) -> float:
        """
        Clamp temperature to safety limits.

        Args:
            temp: Temperature in Celsius

        Returns:
            Temperature clamped to [min_temperature, max_temperature]
        """
        return max(self.min_temperature, min(self.max_temperature, temp))

    def validate_pressure(self, pressure: float) -> float:
        """
        Clamp pressure to safety limits.

        Args:
            pressure: Pressure in bar

        Returns:
            Pressure clamped to [min_pressure, max_pressure]
        """
        return max(self.min_pressure, min(self.max_pressure, pressure))

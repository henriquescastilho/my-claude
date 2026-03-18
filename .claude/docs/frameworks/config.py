#!/usr/bin/env python3
"""
Configuration Management for Agent SDK Orchestrator
===================================================
Centralized configuration with environment variable support.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AnthropicConfig:
    """Anthropic API configuration"""
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    default_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")))
    temperature: float = field(default_factory=lambda: float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")))
    timeout: int = field(default_factory=lambda: int(os.getenv("ANTHROPIC_TIMEOUT", "300")))


@dataclass
class AgentConfig:
    """Agent system configuration"""
    agents_dir: Path = field(default_factory=lambda: Path(os.getenv("AGENTS_DIR", Path.home() / ".claude" / "agents")))
    skills_dir: Path = field(default_factory=lambda: Path(os.getenv("SKILLS_DIR", Path.home() / ".claude" / "skills")))
    cache_enabled: bool = field(default_factory=lambda: os.getenv("AGENT_CACHE_ENABLED", "true").lower() == "true")
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("AGENT_CACHE_TTL", "3600")))


@dataclass
class ExecutionConfig:
    """Execution and performance configuration"""
    max_concurrent_agents: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_AGENTS", "10")))
    agent_timeout: int = field(default_factory=lambda: int(os.getenv("AGENT_TIMEOUT", "300")))
    retry_attempts: int = field(default_factory=lambda: int(os.getenv("RETRY_ATTEMPTS", "3")))
    retry_backoff_base: float = field(default_factory=lambda: float(os.getenv("RETRY_BACKOFF_BASE", "2.0")))
    retry_backoff_max: float = field(default_factory=lambda: float(os.getenv("RETRY_BACKOFF_MAX", "60.0")))


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))
    file: Optional[Path] = field(default_factory=lambda: Path(os.getenv("LOG_FILE")) if os.getenv("LOG_FILE") else None)
    console_enabled: bool = field(default_factory=lambda: os.getenv("LOG_CONSOLE", "true").lower() == "true")


@dataclass
class PersistenceConfig:
    """Data persistence configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv("PERSISTENCE_ENABLED", "true").lower() == "true")
    db_path: Path = field(default_factory=lambda: Path(os.getenv("DB_PATH", ".orchestrator/data/orchestrator.db")))
    history_retention_days: int = field(default_factory=lambda: int(os.getenv("HISTORY_RETENTION_DAYS", "30")))


@dataclass
class OrchestratorConfig:
    """Main orchestrator configuration"""
    anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self) -> None:
        """Validate configuration values"""
        if not self.anthropic.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or .env file")

        if self.execution.max_concurrent_agents < 1:
            raise ValueError("MAX_CONCURRENT_AGENTS must be at least 1")

        if self.execution.retry_attempts < 0:
            raise ValueError("RETRY_ATTEMPTS must be non-negative")

        if self.persistence.enabled:
            self.persistence.db_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        """Create configuration from environment variables"""
        return cls()

    @classmethod
    def from_file(cls, config_file: Path) -> "OrchestratorConfig":
        """Load configuration from YAML file"""
        import yaml

        with open(config_file) as f:
            data = yaml.safe_load(f)

        return cls(
            anthropic=AnthropicConfig(**data.get("anthropic", {})),
            agents=AgentConfig(**data.get("agents", {})),
            execution=ExecutionConfig(**data.get("execution", {})),
            logging=LoggingConfig(**data.get("logging", {})),
            persistence=PersistenceConfig(**data.get("persistence", {})),
        )


# Global configuration instance
_config: Optional[OrchestratorConfig] = None


def get_config() -> OrchestratorConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = OrchestratorConfig.from_env()
    return _config


def set_config(config: OrchestratorConfig) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration instance"""
    global _config
    _config = None

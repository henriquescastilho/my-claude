#!/usr/bin/env python3
"""Setup configuration for Agent SDK Orchestrator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="agent-sdk-orchestrator",
    version="1.0.0",
    description="Production Multi-Agent Orchestrator with PACT/BMAD/Swarm patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pedro",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "anthropic>=0.39.0",
        "rich>=13.7.0",
        "click>=8.1.7",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "structlog>=24.1.0",
        "aiofiles>=23.2.1",
        "cachetools>=5.3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "mypy>=1.8.0",
            "black>=24.1.1",
            "ruff>=0.1.14",
            "ipython>=8.20.0",
        ],
        "tui": [
            "prompt-toolkit>=3.0.43",
        ],
        "web": [
            "aiohttp>=3.9.1",
            "httpx>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "orchestrator=orchestrator:main",
            "pact=pact_framework:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai agents orchestration pact bmad swarm claude anthropic",
)

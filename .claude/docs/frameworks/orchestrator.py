#!/usr/bin/env python3
"""
Production Multi-Agent Orchestrator V2
======================================

Enterprise-grade orchestrator with Anthropic SDK, structured logging,
comprehensive error handling, and true parallel execution.

Author: Pedro
Version: 2.0.0
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from enum import Enum

# Anthropic SDK
from anthropic import AsyncAnthropic
from anthropic.types import Message, TextBlock, ToolUseBlock

# Internal modules
from config import get_config, OrchestratorConfig
from logger import get_logger, setup_logging, LogContext, log_execution_time
from error_handler import (
    with_retry,
    AgentExecutionError,
    AgentTimeoutError,
    AgentConfigurationError,
    get_error_handler
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

class AgentRole(Enum):
    """Agent role categorization"""
    PLANNING = "planning"
    ACTION = "action"
    COORDINATION = "coordination"
    TESTING = "testing"
    RESEARCH = "research"
    REVIEW = "review"


@dataclass
class AgentConfig:
    """Agent configuration loaded from .md file"""
    name: str
    description: str
    prompt: str
    tools: List[str]
    model: str = "claude-sonnet-4-20250514"
    role: AgentRole = AgentRole.ACTION
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class AgentResult:
    """Result from agent execution"""
    agent_name: str
    role: AgentRole
    output: str
    success: bool = True
    duration_seconds: float = 0.0
    tokens_used: int = 0
    model: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmResult:
    """Result from swarm execution"""
    name: str
    agents: List[str]
    results: List[AgentResult]
    duration: float
    success: bool
    parallel: bool
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "agents": self.agents,
            "duration": self.duration,
            "success": self.success,
            "parallel": self.parallel,
            "total_tokens": self.total_tokens,
            "results": [
                {
                    "agent": r.agent_name,
                    "role": r.role.value,
                    "success": r.success,
                    "duration": r.duration_seconds,
                    "tokens": r.tokens_used,
                    "error": r.error
                }
                for r in self.results
            ],
            "metadata": self.metadata
        }


# =============================================================================
# AGENT LOADER
# =============================================================================

class AgentLoader:
    """Loads and manages agent definitions from markdown files"""

    def __init__(self, agents_dir: Optional[Path] = None):
        self.config = get_config()
        self.agents_dir = agents_dir or self.config.agents.agents_dir
        self.agents: Dict[str, AgentConfig] = {}
        self._load_all()

    @log_execution_time()
    def _load_all(self) -> None:
        """Load all agent .md files from the agents directory"""
        if not self.agents_dir.exists():
            logger.warning(
                "Agents directory not found",
                path=str(self.agents_dir)
            )
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            return

        count = 0
        for md_file in self.agents_dir.glob("*.md"):
            try:
                agent = self._parse_agent(md_file)
                if agent:
                    self.agents[agent.name] = agent
                    count += 1
            except Exception as e:
                logger.error(
                    "Failed to load agent",
                    file=str(md_file),
                    error=str(e)
                )

        logger.info(
            "Agent loading complete",
            total_agents=count,
            directory=str(self.agents_dir)
        )

    def _parse_agent(self, filepath: Path) -> Optional[AgentConfig]:
        """
        Parse markdown agent file with YAML frontmatter

        Expected format:
        ---
        name: agent-name
        description: Agent description
        model: claude-sonnet-4-20250514
        tools: [Read, Write, Bash]
        ---

        Agent prompt goes here...
        """
        try:
            content = filepath.read_text(encoding='utf-8')

            if not content.startswith("---"):
                logger.debug("Invalid frontmatter", file=str(filepath))
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                logger.debug("Incomplete frontmatter", file=str(filepath))
                return None

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            config_dict = {}
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    config_dict[key.strip()] = value.strip()

            # Parse tools list
            tools_str = config_dict.get("tools", "[]")
            tools = self._parse_tools(tools_str)

            agent = AgentConfig(
                name=config_dict.get("name", filepath.stem),
                description=config_dict.get("description", ""),
                prompt=body,
                tools=tools,
                model=config_dict.get("model", "claude-sonnet-4-20250514"),
                role=self._infer_role(config_dict.get("name", ""))
            )

            logger.debug(
                "Agent loaded",
                name=agent.name,
                role=agent.role.value,
                tools_count=len(tools)
            )

            return agent

        except Exception as e:
            logger.error(
                "Agent parsing failed",
                file=str(filepath),
                error=str(e),
                error_type=type(e).__name__
            )
            return None

    def _parse_tools(self, tools_str: str) -> List[str]:
        """Parse tools from [Tool1, Tool2] format"""
        tools_str = tools_str.strip("[]")
        if not tools_str:
            return []
        return [t.strip() for t in tools_str.split(",") if t.strip()]

    def _infer_role(self, name: str) -> AgentRole:
        """Infer agent role from name"""
        name_lower = name.lower()

        if any(x in name_lower for x in ["plan", "architect", "design"]):
            return AgentRole.PLANNING
        elif any(x in name_lower for x in ["test", "qa", "quality"]):
            return AgentRole.TESTING
        elif any(x in name_lower for x in ["review", "audit", "check"]):
            return AgentRole.REVIEW
        elif any(x in name_lower for x in ["explore", "research", "search"]):
            return AgentRole.RESEARCH
        elif any(x in name_lower for x in ["coord", "manage"]):
            return AgentRole.COORDINATION

        return AgentRole.ACTION

    def get(self, name: str) -> Optional[AgentConfig]:
        """Get agent by name"""
        return self.agents.get(name)

    def get_by_role(self, role: AgentRole) -> List[AgentConfig]:
        """Get all agents with a specific role"""
        return [a for a in self.agents.values() if a.role == role]

    def search(self, pattern: str) -> List[AgentConfig]:
        """Search agents by name or description"""
        pattern_lower = pattern.lower()
        return [
            a for a in self.agents.values()
            if pattern_lower in a.name.lower() or pattern_lower in a.description.lower()
        ]

    def list_all(self) -> List[str]:
        """List all agent names"""
        return sorted(self.agents.keys())


# =============================================================================
# SWARM PATTERNS
# =============================================================================

SWARM_PATTERNS = {
    # Analysis Swarms
    "code-analysis": {
        "description": "Parallel code quality, security, and performance analysis",
        "agents": ["code-reviewer", "security-auditor", "performance-engineer"],
        "parallel": True
    },
    "security-deep": {
        "description": "Deep security analysis",
        "agents": ["security-auditor", "security-sast", "backend-security-coder"],
        "parallel": True
    },

    # Development Swarms
    "full-stack": {
        "description": "Full-stack feature implementation",
        "agents": ["frontend-developer", "backend-architect", "test-automator"],
        "parallel": True
    },
    "frontend-swarm": {
        "description": "Frontend development and UI/UX",
        "agents": ["frontend-developer", "ui-ux-designer", "frontend-security-coder"],
        "parallel": True
    },
    "backend-swarm": {
        "description": "Backend API and service development",
        "agents": ["backend-architect", "database-architect", "backend-security-coder"],
        "parallel": True
    },

    # Testing Swarms
    "test-swarm": {
        "description": "Comprehensive testing automation",
        "agents": ["test-automator", "test-generate", "tdd-orchestrator"],
        "parallel": True
    },

    # DevOps Swarms
    "devops-swarm": {
        "description": "DevOps and infrastructure",
        "agents": ["kubernetes-architect", "terraform-specialist", "deployment-engineer"],
        "parallel": True
    },
}


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class Orchestrator:
    """
    Production Multi-Agent Orchestrator

    Features:
    - True parallel execution with AsyncAnthropic
    - Comprehensive error handling with retry
    - Structured logging and observability
    - Swarm patterns and workflows
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or get_config()
        self.client = AsyncAnthropic(
            api_key=self.config.anthropic.api_key,
            timeout=self.config.anthropic.timeout
        )
        self.loader = AgentLoader()
        self.error_handler = get_error_handler()
        self.history: List[SwarmResult] = []

        logger.info(
            "Orchestrator initialized",
            agents_loaded=len(self.loader.agents),
            model=self.config.anthropic.default_model
        )

    @log_execution_time()
    @with_retry(max_attempts=3)
    async def execute_single(
        self,
        agent_name: str,
        task: str,
        **kwargs
    ) -> AgentResult:
        """
        Execute a single agent with retry logic

        Args:
            agent_name: Name of the agent to execute
            task: Task description
            **kwargs: Additional arguments for the agent

        Returns:
            AgentResult with execution details
        """
        with LogContext(agent=agent_name, task_preview=task[:50]):
            agent = self.loader.get(agent_name)

            if not agent:
                error_msg = f"Agent '{agent_name}' not found"
                logger.error("Agent not found", agent=agent_name)
                raise AgentConfigurationError(error_msg)

            logger.info(
                "Executing agent",
                agent=agent_name,
                role=agent.role.value,
                model=agent.model
            )

            start_time = datetime.now()

            try:
                # Build system prompt
                system_prompt = f"""You are {agent.name}: {agent.description}

{agent.prompt}

Focus on the task. Be thorough but concise."""

                # Call Anthropic API
                response = await self.client.messages.create(
                    model=agent.model,
                    max_tokens=agent.max_tokens,
                    temperature=agent.temperature,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": task
                    }]
                )

                # Extract text from response
                output_text = ""
                for block in response.content:
                    if isinstance(block, TextBlock):
                        output_text += block.text

                duration = (datetime.now() - start_time).total_seconds()

                result = AgentResult(
                    agent_name=agent_name,
                    role=agent.role,
                    output=output_text,
                    success=True,
                    duration_seconds=duration,
                    tokens_used=response.usage.total_tokens,
                    model=response.model,
                    metadata={
                        "stop_reason": response.stop_reason,
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                )

                logger.info(
                    "Agent execution complete",
                    agent=agent_name,
                    duration=duration,
                    tokens=response.usage.total_tokens,
                    success=True
                )

                return result

            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()

                logger.error(
                    "Agent execution failed",
                    agent=agent_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration=duration
                )

                self.error_handler.record_error(
                    e,
                    context={"agent": agent_name, "task": task[:100]}
                )

                return AgentResult(
                    agent_name=agent_name,
                    role=agent.role,
                    output="",
                    success=False,
                    duration_seconds=duration,
                    error=str(e)
                )

    @log_execution_time()
    async def execute_parallel_swarm(
        self,
        agent_names: List[str],
        task: str,
        **kwargs
    ) -> SwarmResult:
        """
        Execute multiple agents in TRUE parallel

        Args:
            agent_names: List of agent names to execute
            task: Task description for all agents
            **kwargs: Additional arguments

        Returns:
            SwarmResult with all agent results
        """
        start = datetime.now()
        swarm_name = f"swarm_{start.strftime('%Y%m%d_%H%M%S')}"

        with LogContext(swarm=swarm_name, agents_count=len(agent_names)):
            logger.info(
                "Starting parallel swarm",
                swarm=swarm_name,
                agents=agent_names,
                task_preview=task[:80]
            )

            # Create async tasks for ALL agents
            tasks = [
                self.execute_single(name, task, **kwargs)
                for name in agent_names
            ]

            # Execute ALL simultaneously with gather
            results = await asyncio.gather(*tasks, return_exceptions=False)

            duration = (datetime.now() - start).total_seconds()
            success = all(r.success for r in results)
            total_tokens = sum(r.tokens_used for r in results)

            swarm_result = SwarmResult(
                name=swarm_name,
                agents=agent_names,
                results=results,
                duration=duration,
                success=success,
                parallel=True,
                total_tokens=total_tokens
            )

            self.history.append(swarm_result)

            logger.info(
                "Swarm execution complete",
                swarm=swarm_name,
                duration=duration,
                success=success,
                total_tokens=total_tokens,
                successful_agents=sum(1 for r in results if r.success),
                total_agents=len(results)
            )

            return swarm_result

    @log_execution_time()
    async def execute_swarm_pattern(
        self,
        pattern_name: str,
        task: str,
        **kwargs
    ) -> SwarmResult:
        """
        Execute a predefined swarm pattern

        Args:
            pattern_name: Name of the swarm pattern
            task: Task description
            **kwargs: Additional arguments

        Returns:
            SwarmResult from pattern execution
        """
        if pattern_name not in SWARM_PATTERNS:
            raise ValueError(f"Unknown swarm pattern: {pattern_name}")

        pattern = SWARM_PATTERNS[pattern_name]

        logger.info(
            "Executing swarm pattern",
            pattern=pattern_name,
            description=pattern["description"],
            agents=pattern["agents"]
        )

        return await self.execute_parallel_swarm(
            pattern["agents"],
            task,
            **kwargs
        )

    def list_patterns(self) -> Dict[str, str]:
        """List all available swarm patterns"""
        return {
            name: pattern["description"]
            for name, pattern in SWARM_PATTERNS.items()
        }

    def get_history(self) -> List[SwarmResult]:
        """Get execution history"""
        return self.history

    def get_stats(self) -> dict:
        """Get orchestrator statistics"""
        return {
            "agents_loaded": len(self.loader.agents),
            "executions": len(self.history),
            "total_tokens_used": sum(s.total_tokens for s in self.history),
            "successful_executions": sum(1 for s in self.history if s.success),
            "patterns_available": len(SWARM_PATTERNS)
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """CLI entry point"""
    import argparse
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    parser = argparse.ArgumentParser(
        description="Production Multi-Agent Orchestrator V2"
    )
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("--swarm", "-s", help="Execute a swarm pattern")
    parser.add_argument("--agents", "-a", nargs="+", help="Specific agents to run")
    parser.add_argument("--list", "-l", action="store_true", help="List available agents")
    parser.add_argument("--patterns", action="store_true", help="List swarm patterns")
    parser.add_argument("--stats", action="store_true", help="Show orchestrator stats")

    args = parser.parse_args()

    try:
        orchestrator = Orchestrator()
    except Exception as e:
        console.print(f"[red]Failed to initialize orchestrator: {e}[/red]")
        sys.exit(1)

    # List mode
    if args.list:
        agents = orchestrator.loader.list_all()

        table = Table(title="Available Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Role", style="magenta")

        for name in agents[:50]:
            agent = orchestrator.loader.get(name)
            if agent:
                table.add_row(name, agent.role.value)

        console.print(table)
        if len(agents) > 50:
            console.print(f"\n[dim]... and {len(agents) - 50} more agents[/dim]")
        return

    if args.patterns:
        table = Table(title="Swarm Patterns")
        table.add_column("Pattern", style="cyan")
        table.add_column("Description", style="white")

        for name, desc in orchestrator.list_patterns().items():
            table.add_row(name, desc)

        console.print(table)
        return

    if args.stats:
        stats = orchestrator.get_stats()

        console.print(Panel.fit(
            f"""[cyan]Orchestrator Statistics[/cyan]

Agents Loaded:     {stats['agents_loaded']}
Executions:        {stats['executions']}
Total Tokens:      {stats['total_tokens_used']:,}
Success Rate:      {stats['successful_executions']}/{stats['executions']}
Patterns:          {stats['patterns_available']}
""",
            title="Stats",
            border_style="green"
        ))
        return

    # Execution mode
    if not args.task and not args.swarm:
        parser.print_help()
        return

    task = args.task or "Analyze the codebase"

    try:
        if args.swarm:
            result = await orchestrator.execute_swarm_pattern(args.swarm, task)
        elif args.agents:
            result = await orchestrator.execute_parallel_swarm(args.agents, task)
        else:
            # Default: single agent or code-analysis swarm
            result = await orchestrator.execute_swarm_pattern("code-analysis", task)

        # Display results
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            f"""[green]Execution Complete[/green]

Duration:    {result.duration:.2f}s
Success:     {result.success}
Tokens:      {result.total_tokens:,}
Agents:      {len(result.results)}
""",
            title=result.name,
            border_style="green" if result.success else "red"
        ))

        # Show agent results
        for agent_result in result.results:
            status = "✅" if agent_result.success else "❌"
            console.print(f"\n{status} [cyan]{agent_result.agent_name}[/cyan] ({agent_result.duration_seconds:.2f}s)")
            if agent_result.success:
                console.print(f"[dim]{agent_result.output[:200]}...[/dim]")
            else:
                console.print(f"[red]Error: {agent_result.error}[/red]")

    except Exception as e:
        console.print(f"\n[red]Execution failed: {e}[/red]")
        logger.exception("Execution failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

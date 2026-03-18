#!/usr/bin/env python3
"""
Production Multi-Agent Orchestrator
====================================

Integrates Claude Agent SDK with your existing 241 agents for
true parallel execution with PACT/BMAD/Swarm patterns.

Usage:
    python orchestrator.py "Your task description"
    python orchestrator.py --swarm code-analysis
    python orchestrator.py --pact "Build user authentication"
"""

import asyncio
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

# Claude Agent SDK imports
from claude_agent_sdk import query, ClaudeAgentOptions


# =============================================================================
# CONFIGURATION
# =============================================================================

AGENTS_DIR = Path.home() / ".claude" / "agents"
SKILLS_DIR = Path.home() / ".claude" / "skills"


class AgentRole(Enum):
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
    tools: list[str]
    model: str = "sonnet"
    role: AgentRole = AgentRole.ACTION


@dataclass
class SwarmResult:
    """Result from swarm execution"""
    name: str
    agents: list[str]
    results: list[dict]
    duration: float
    success: bool
    parallel: bool


# =============================================================================
# AGENT LOADER - Loads your 241 agents
# =============================================================================

class AgentLoader:
    """Loads agent definitions from ~/.claude/agents/"""

    def __init__(self):
        self.agents: dict[str, AgentConfig] = {}
        self._load_all()

    def _load_all(self):
        """Load all agent .md files"""
        if not AGENTS_DIR.exists():
            print(f"⚠️ Agents dir not found: {AGENTS_DIR}")
            return

        count = 0
        for md_file in AGENTS_DIR.glob("*.md"):
            agent = self._parse_agent(md_file)
            if agent:
                self.agents[agent.name] = agent
                count += 1

        print(f"✅ Loaded {count} agents from {AGENTS_DIR}")

    def _parse_agent(self, filepath: Path) -> AgentConfig | None:
        """Parse markdown agent file with YAML frontmatter"""
        try:
            content = filepath.read_text()
            if not content.startswith("---"):
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML-like frontmatter
            config = {}
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    config[key.strip()] = value.strip()

            # Parse tools list
            tools_str = config.get("tools", "[]")
            tools = self._parse_tools(tools_str)

            return AgentConfig(
                name=config.get("name", filepath.stem),
                description=config.get("description", ""),
                prompt=body[:2000],  # Truncate for context
                tools=tools,
                model=config.get("model", "sonnet"),
                role=self._infer_role(config.get("name", ""))
            )
        except Exception as e:
            return None

    def _parse_tools(self, tools_str: str) -> list[str]:
        """Parse tools from [Tool1, Tool2] format"""
        tools_str = tools_str.strip("[]")
        return [t.strip() for t in tools_str.split(",") if t.strip()]

    def _infer_role(self, name: str) -> AgentRole:
        """Infer agent role from name"""
        name = name.lower()
        if any(x in name for x in ["plan", "architect", "design"]):
            return AgentRole.PLANNING
        elif any(x in name for x in ["test", "qa", "quality"]):
            return AgentRole.TESTING
        elif any(x in name for x in ["review", "audit", "check"]):
            return AgentRole.REVIEW
        elif any(x in name for x in ["explore", "research", "search"]):
            return AgentRole.RESEARCH
        return AgentRole.ACTION

    def get(self, name: str) -> AgentConfig | None:
        return self.agents.get(name)

    def get_by_role(self, role: AgentRole) -> list[AgentConfig]:
        return [a for a in self.agents.values() if a.role == role]

    def search(self, pattern: str) -> list[AgentConfig]:
        """Find agents matching pattern"""
        pattern = pattern.lower()
        return [
            a for a in self.agents.values()
            if pattern in a.name.lower() or pattern in a.description.lower()
        ]


# =============================================================================
# SWARM PATTERNS - Pre-defined parallel configurations
# =============================================================================

SWARM_PATTERNS = {
    # === ANALYSIS SWARMS ===
    "code-analysis": {
        "description": "Parallel code quality, security, and performance analysis",
        "agents": ["code-reviewer", "security-auditor", "performance-engineer"],
        "parallel": True
    },
    "security-deep": {
        "description": "Deep security analysis (OWASP, SAST, backend)",
        "agents": ["security-auditor", "security-sast", "backend-security-coder"],
        "parallel": True
    },
    "review-chain": {
        "description": "Multi-perspective code review",
        "agents": ["code-reviewer", "architect-review", "security-auditor"],
        "parallel": True
    },

    # === DEBUGGING SWARMS ===
    "debug-swarm": {
        "description": "Parallel debugging and error analysis",
        "agents": ["debugger", "error-detective", "smart-debug"],
        "parallel": True
    },
    "error-hunt": {
        "description": "Deep error tracing and root cause analysis",
        "agents": ["error-detective", "error-trace", "devops-troubleshooter"],
        "parallel": True
    },

    # === DEVELOPMENT SWARMS ===
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
    "api-swarm": {
        "description": "API design and documentation",
        "agents": ["backend-architect", "api-documenter", "graphql-architect"],
        "parallel": True
    },

    # === DATABASE SWARMS ===
    "database-swarm": {
        "description": "Database design and optimization",
        "agents": ["database-architect", "database-optimizer", "database-admin"],
        "parallel": True
    },
    "data-swarm": {
        "description": "Data engineering and pipelines",
        "agents": ["data-engineer", "data-scientist", "database-optimizer"],
        "parallel": True
    },

    # === TESTING SWARMS ===
    "test-swarm": {
        "description": "Comprehensive testing automation",
        "agents": ["test-automator", "test-generate", "tdd-orchestrator"],
        "parallel": True
    },
    "quality-swarm": {
        "description": "Quality assurance and validation",
        "agents": ["code-reviewer", "test-automator", "accessibility-audit"],
        "parallel": True
    },

    # === INFRASTRUCTURE SWARMS ===
    "devops-swarm": {
        "description": "DevOps and infrastructure",
        "agents": ["kubernetes-architect", "terraform-specialist", "deployment-engineer"],
        "parallel": True
    },
    "cloud-swarm": {
        "description": "Cloud architecture and multi-cloud",
        "agents": ["cloud-architect", "hybrid-cloud-architect", "network-engineer"],
        "parallel": True
    },
    "observability-swarm": {
        "description": "Monitoring, logging, and tracing",
        "agents": ["observability-engineer", "performance-engineer", "incident-responder"],
        "parallel": True
    },

    # === AI/ML SWARMS ===
    "ai-swarm": {
        "description": "AI/ML development",
        "agents": ["ai-engineer", "ml-engineer", "prompt-engineer"],
        "parallel": True
    },
    "mlops-swarm": {
        "description": "ML operations and pipelines",
        "agents": ["mlops-engineer", "ml-engineer", "data-engineer"],
        "parallel": True
    },

    # === DOCUMENTATION SWARMS ===
    "docs-swarm": {
        "description": "Documentation generation",
        "agents": ["docs-architect", "api-documenter", "tutorial-engineer"],
        "parallel": True
    },
    "reference-swarm": {
        "description": "Technical reference and API docs",
        "agents": ["reference-builder", "api-documenter", "code-explain"],
        "parallel": True
    },

    # === LANGUAGE-SPECIFIC SWARMS ===
    "python-swarm": {
        "description": "Python development expertise",
        "agents": ["python-pro", "fastapi-pro", "django-pro"],
        "parallel": True
    },
    "typescript-swarm": {
        "description": "TypeScript/JavaScript development",
        "agents": ["typescript-pro", "javascript-pro", "frontend-developer"],
        "parallel": True
    },
    "golang-swarm": {
        "description": "Go development and optimization",
        "agents": ["golang-pro", "backend-architect", "performance-engineer"],
        "parallel": True
    },
    "rust-swarm": {
        "description": "Rust systems programming",
        "agents": ["rust-pro", "performance-engineer", "security-auditor"],
        "parallel": True
    },

    # === SPECIALIZED SWARMS ===
    "mobile-swarm": {
        "description": "Mobile app development",
        "agents": ["mobile-developer", "ios-developer", "flutter-expert"],
        "parallel": True
    },
    "blockchain-swarm": {
        "description": "Web3 and blockchain development",
        "agents": ["blockchain-developer", "security-auditor", "backend-architect"],
        "parallel": True
    },
    "fintech-swarm": {
        "description": "Financial technology and trading",
        "agents": ["quant-analyst", "risk-manager", "backend-security-coder"],
        "parallel": True
    },

    # === TASKMASTER SWARMS ===
    "tm-init": {
        "description": "TaskMaster project initialization",
        "agents": ["taskmaster-pm", "docs-architect", "architect-review"],
        "parallel": True
    },
    "tm-implement": {
        "description": "TaskMaster implementation workflow",
        "agents": ["taskmaster-pm", "frontend-developer", "backend-architect", "test-automator"],
        "parallel": True
    },
    "tm-research": {
        "description": "TaskMaster research workflow",
        "agents": ["taskmaster-pm", "search-specialist", "docs-architect"],
        "parallel": True
    },
    "tm-quality": {
        "description": "TaskMaster quality review workflow",
        "agents": ["taskmaster-pm", "code-reviewer", "security-auditor", "test-automator"],
        "parallel": True
    }
}


# =============================================================================
# ORCHESTRATOR - Main execution engine
# =============================================================================

class Orchestrator:
    """
    Multi-Agent Orchestrator with Claude Agent SDK

    Executes agents in parallel using true async execution.
    """

    def __init__(self):
        self.loader = AgentLoader()
        self.history: list[SwarmResult] = []

    async def execute_single(self, agent_name: str, task: str) -> str:
        """Execute a single agent"""
        agent = self.loader.get(agent_name)

        if not agent:
            print(f"⚠️ Agent '{agent_name}' not found")
            return f"Agent {agent_name} not found"

        print(f"  → Executing: {agent_name}")

        result_text = ""
        try:
            async for message in query(
                prompt=f"{agent.prompt}\n\n---\n\nTASK: {task}",
                options=ClaudeAgentOptions(
                    allowed_tools=agent.tools + ["Task"],
                    permission_mode="acceptEdits"
                )
            ):
                if hasattr(message, "result"):
                    result_text = message.result
                elif hasattr(message, "content"):
                    # Streaming content
                    pass

        except Exception as e:
            result_text = f"Error: {str(e)}"

        return result_text

    async def execute_parallel_swarm(
        self,
        agent_names: list[str],
        task: str
    ) -> SwarmResult:
        """Execute multiple agents in TRUE parallel"""
        start = datetime.now()
        swarm_name = f"swarm_{start.strftime('%H%M%S')}"

        print(f"\n🐝 PARALLEL SWARM: {swarm_name}")
        print(f"📝 Task: {task[:80]}...")
        print(f"👥 Agents: {', '.join(agent_names)}")
        print("-" * 60)

        # Create async tasks for ALL agents
        tasks = [
            self._execute_with_sdk(name, task)
            for name in agent_names
        ]

        # Execute ALL simultaneously
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        results = []
        for i, result in enumerate(raw_results):
            name = agent_names[i]
            if isinstance(result, Exception):
                results.append({"agent": name, "success": False, "error": str(result)})
            else:
                results.append({"agent": name, "success": True, "output": result})

        duration = (datetime.now() - start).total_seconds()
        success = all(r["success"] for r in results)

        swarm_result = SwarmResult(
            name=swarm_name,
            agents=agent_names,
            results=results,
            duration=duration,
            success=success,
            parallel=True
        )

        self.history.append(swarm_result)

        print(f"\n✅ Swarm complete in {duration:.2f}s")
        print(f"   {sum(1 for r in results if r['success'])}/{len(results)} succeeded")

        return swarm_result

    async def _execute_with_sdk(self, agent_name: str, task: str) -> str:
        """Execute single agent with SDK"""
        agent = self.loader.get(agent_name)

        if not agent:
            return f"[{agent_name}] Agent not found in registry"

        system_prompt = f"""You are {agent_name}: {agent.description}

{agent.prompt[:1500]}

Focus on the task. Be thorough but concise. Limit response to key findings."""

        result_text = ""
        try:
            async for message in query(
                prompt=task,
                options=ClaudeAgentOptions(
                    system_prompt=system_prompt,
                    allowed_tools=agent.tools if agent.tools else ["Read", "Grep", "Glob"],
                    max_turns=3
                )
            ):
                if hasattr(message, "result"):
                    result_text = message.result
                    break
                elif hasattr(message, "content") and message.content:
                    # Capture streaming content
                    if isinstance(message.content, str):
                        result_text = message.content

        except GeneratorExit:
            pass  # Normal cleanup
        except Exception as e:
            if "cancel scope" not in str(e):
                result_text = f"Error executing {agent_name}: {str(e)}"

        return result_text if result_text else f"[{agent_name}] Completed"

    async def execute_swarm_pattern(self, pattern_name: str, task: str) -> SwarmResult:
        """Execute a predefined swarm pattern"""
        if pattern_name not in SWARM_PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        pattern = SWARM_PATTERNS[pattern_name]
        print(f"\n🎯 Swarm Pattern: {pattern_name}")
        print(f"📋 {pattern['description']}")

        return await self.execute_parallel_swarm(pattern["agents"], task)

    async def execute_pact(self, task: str) -> dict:
        """
        Execute full PACT workflow:
        Planning → Action (parallel) → Coordination → Testing
        """
        print("\n" + "=" * 60)
        print("🎯 PACT WORKFLOW")
        print("=" * 60)
        print(f"📝 Task: {task}")

        results = {}

        # Phase 1: Planning
        print("\n📋 PHASE 1: PLANNING")
        planning = await self.execute_single("architect-review",
            f"Break down this task into subtasks with dependencies:\n{task}")
        results["planning"] = planning

        # Phase 2: Action (Parallel)
        print("\n⚡ PHASE 2: ACTION (Parallel)")
        action_swarm = await self.execute_parallel_swarm(
            ["frontend-developer", "backend-architect", "test-automator"],
            f"Based on this plan, implement your part:\n{planning}\n\nOriginal task: {task}"
        )
        results["action"] = action_swarm

        # Phase 3: Coordination
        print("\n🔗 PHASE 3: COORDINATION")
        action_summary = "\n".join([
            f"[{r['agent']}]: {r.get('output', r.get('error', ''))[:500]}"
            for r in action_swarm.results
        ])
        coordination = await self.execute_single("code-reviewer",
            f"Review and coordinate these outputs for consistency:\n{action_summary}")
        results["coordination"] = coordination

        # Phase 4: Testing
        print("\n🧪 PHASE 4: TESTING")
        testing = await self.execute_single("test-automator",
            f"Validate all changes made for this task:\n{task}")
        results["testing"] = testing

        print("\n" + "=" * 60)
        print("✅ PACT WORKFLOW COMPLETE")
        print("=" * 60)

        return results

    async def execute_bmad(self, project: str) -> dict:
        """
        Execute full BMAD lifecycle:
        Research → Design → Implementation → Deployment
        """
        print("\n" + "=" * 60)
        print("🔄 BMAD LIFECYCLE")
        print("=" * 60)
        print(f"📝 Project: {project}")

        results = {}

        phases = [
            ("RESEARCH", "code-analysis",
             f"Research and analyze requirements for: {project}"),
            ("DESIGN", "review-chain",
             f"Design architecture and approach for: {project}"),
            ("IMPLEMENTATION", "full-stack",
             f"Implement the designed solution for: {project}"),
            ("DEPLOYMENT", "devops-swarm",
             f"Prepare deployment and infrastructure for: {project}")
        ]

        for phase_name, pattern, prompt in phases:
            print(f"\n📍 PHASE: {phase_name}")
            print("-" * 40)

            try:
                result = await self.execute_swarm_pattern(pattern, prompt)
                results[phase_name.lower()] = result

                # Quality gate check
                if not result.success:
                    print(f"❌ Phase {phase_name} failed. Stopping.")
                    break

                print(f"✅ Phase {phase_name} complete")

            except Exception as e:
                print(f"❌ Phase {phase_name} error: {e}")
                break

        return results

    async def execute_taskmaster(self, task: str, project_dir: str = ".") -> dict:
        """
        Execute TaskMaster workflow with full PM orchestration:

        1. Check project state (tasks.json exists?)
        2. If new: Initialize → PRD → Parse → Analyze
        3. If active: Status → Classify → Dispatch → Execute → Update
        """
        print("\n" + "=" * 60)
        print("📋 TASKMASTER ORCHESTRATION")
        print("=" * 60)
        print(f"📝 Task: {task}")
        print(f"📁 Project: {project_dir}")

        results = {}
        tasks_file = Path(project_dir) / ".taskmaster" / "tasks" / "tasks.json"

        # Phase 1: Check State
        print("\n🔍 PHASE 1: STATE CHECK")
        if tasks_file.exists():
            print("   ✅ Active project detected (tasks.json exists)")
            workflow = "active"
            try:
                import json
                tasks_data = json.loads(tasks_file.read_text())
                task_count = len(tasks_data.get("tasks", []))
                print(f"   📊 {task_count} tasks in project")
            except:
                task_count = 0
        else:
            print("   🆕 New project (no tasks.json)")
            workflow = "init"

        results["state"] = {"workflow": workflow, "tasks_file": str(tasks_file)}

        if workflow == "init":
            # === INITIALIZATION WORKFLOW ===
            print("\n📦 PHASE 2: INITIALIZATION (Parallel)")

            # Parallel: Explore + Memory + Docs
            init_swarm = await self.execute_parallel_swarm(
                ["taskmaster-pm", "docs-architect"],
                f"""Initialize TaskMaster for this project:

Task: {task}
Directory: {project_dir}

Steps:
1. Run /tm/init/init-project-quick to create .taskmaster/
2. Create a PRD at .taskmaster/docs/prd.md based on the task
3. Run /tm/parse-prd/parse-prd to generate tasks
4. Run /tm/analyze-complexity/analyze-complexity
5. Expand any tasks with complexity >= 7
6. Return the task list and first recommendation"""
            )
            results["init"] = init_swarm

            print("\n📋 PHASE 3: TASK GENERATION")
            generation = await self.execute_single("taskmaster-pm",
                f"After initialization, show the generated tasks and recommend the first one to work on")
            results["generation"] = generation

        else:
            # === ACTIVE PROJECT WORKFLOW ===
            print("\n📊 PHASE 2: STATUS & CLASSIFICATION")

            # Get current status
            status = await self.execute_single("taskmaster-pm",
                f"""Read {tasks_file} and:
1. Show compact status: ✅ Done | 🔄 Active | ⏳ Pending
2. Identify current/next task
3. Classify this request: {task}
   - Implementation (build/create/implement)
   - Research (how/what/explain/find)
   - Quality (review/fix/debug/test)
   - Task Management (status/next/done/list)""")
            results["status"] = status

            # Phase 3: Dispatch based on classification
            print("\n⚡ PHASE 3: INTELLIGENT DISPATCH")

            # Determine task type from the request
            task_lower = task.lower()
            if any(w in task_lower for w in ["build", "create", "implement", "add", "code", "feature"]):
                dispatch_type = "implementation"
                agents = ["frontend-developer", "backend-architect", "test-automator"]
            elif any(w in task_lower for w in ["how", "what", "explain", "find", "understand", "research"]):
                dispatch_type = "research"
                agents = ["search-specialist", "docs-architect"]
            elif any(w in task_lower for w in ["review", "fix", "debug", "test", "check", "security"]):
                dispatch_type = "quality"
                agents = ["code-reviewer", "security-auditor", "debugger"]
            else:
                dispatch_type = "general"
                agents = ["taskmaster-pm"]

            print(f"   🎯 Detected: {dispatch_type.upper()}")
            print(f"   👥 Dispatching: {', '.join(agents)}")

            action_swarm = await self.execute_parallel_swarm(
                agents,
                f"TaskMaster Task: {task}\nProject: {project_dir}\n\nExecute this task and report results."
            )
            results["action"] = action_swarm

            # Phase 4: Update & Suggest
            print("\n📝 PHASE 4: UPDATE & SUGGEST")
            update = await self.execute_single("taskmaster-pm",
                f"""Based on the completed work for "{task}":
1. Determine if any task was completed → run /tm/set-status/to-done [id]
2. Update any in-progress tasks
3. Suggest next task with /tm/next/next-task
4. Format response as:
   ✅ [What was accomplished]
   👉 Next: Task #N - [title] | Complexity: X/10""")
            results["update"] = update

        print("\n" + "=" * 60)
        print("✅ TASKMASTER WORKFLOW COMPLETE")
        print("=" * 60)

        return results

    def list_agents(self, pattern: str = None) -> list[str]:
        """List available agents"""
        if pattern:
            agents = self.loader.search(pattern)
        else:
            agents = list(self.loader.agents.values())

        return [a.name for a in agents]

    def list_patterns(self) -> dict:
        """List available swarm patterns"""
        return {
            name: pattern["description"]
            for name, pattern in SWARM_PATTERNS.items()
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """CLI entry point"""
    import argparse
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    parser = argparse.ArgumentParser(
        description="Multi-Agent Orchestrator with Claude Agent SDK"
    )
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("--swarm", "-s", help="Execute a swarm pattern")
    parser.add_argument("--pact", "-p", action="store_true", help="Run PACT workflow")
    parser.add_argument("--bmad", "-b", action="store_true", help="Run BMAD lifecycle")
    parser.add_argument("--tm", "-t", action="store_true", help="Run TaskMaster orchestration")
    parser.add_argument("--project", default=".", help="Project directory for TaskMaster")
    parser.add_argument("--agents", "-a", nargs="+", help="Specific agents to run in parallel")
    parser.add_argument("--list", "-l", action="store_true", help="List available agents")
    parser.add_argument("--patterns", action="store_true", help="List swarm patterns")

    args = parser.parse_args()

    orchestrator = Orchestrator()

    # List mode
    if args.list:
        print("\n📦 Available Agents:")
        for name in sorted(orchestrator.list_agents())[:50]:
            print(f"  • {name}")
        print(f"\n  ... and {len(orchestrator.list_agents()) - 50} more")
        return

    if args.patterns:
        print("\n🐝 Swarm Patterns:")
        for name, desc in orchestrator.list_patterns().items():
            print(f"  • {name}: {desc}")
        return

    # Execution mode
    if not args.task and not args.swarm:
        parser.print_help()
        return

    task = args.task or "Analyze the codebase"

    if args.tm:
        result = await orchestrator.execute_taskmaster(task, args.project)
    elif args.pact:
        result = await orchestrator.execute_pact(task)
    elif args.bmad:
        result = await orchestrator.execute_bmad(task)
    elif args.swarm:
        result = await orchestrator.execute_swarm_pattern(args.swarm, task)
    elif args.agents:
        result = await orchestrator.execute_parallel_swarm(args.agents, task)
    else:
        # Default: code analysis swarm
        result = await orchestrator.execute_swarm_pattern("code-analysis", task)

    print("\n📊 FINAL RESULT:")
    if isinstance(result, dict):
        output = result
    else:
        output = {
            "swarm": result.name,
            "success": result.success,
            "duration": f"{result.duration:.2f}s",
            "agents": result.agents,
            "outputs": {}
        }
        # Include actual agent outputs
        for r in result.results:
            agent = r.get("agent", "unknown")
            if r.get("success"):
                out = r.get("output", "")
                # Truncate long outputs for readability
                output["outputs"][agent] = out[:500] + "..." if len(out) > 500 else out
            else:
                output["outputs"][agent] = f"❌ {r.get('error', 'Unknown error')}"

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())

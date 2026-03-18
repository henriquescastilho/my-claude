#!/usr/bin/env python3
"""
PACT Framework V2 - Production Implementation
=============================================
Planning → Action → Coordination → Testing

With Quality Gates, Structured Logging, and Error Handling

Author: Pedro
Version: 2.0.0
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

from orchestrator_v2 import Orchestrator, AgentResult, SwarmResult
from logger import get_logger, LogContext, log_execution_time
from error_handler import QualityGateFailure, get_error_handler

logger = get_logger(__name__)


# =============================================================================
# ENUMS AND DATA MODELS
# =============================================================================

class Phase(Enum):
    """BMAD/PACT Phases"""
    RESEARCH = "research"
    DESIGN = "design"
    PLANNING = "planning"
    ACTION = "action"
    COORDINATION = "coordination"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class GateCriticality(Enum):
    """Quality gate criticality levels"""
    BLOCKER = "blocker"      # Must pass to continue
    CRITICAL = "critical"    # Should pass, warn if not
    WARNING = "warning"      # Nice to pass, log if not
    INFO = "info"           # Informational only


@dataclass
class QualityGate:
    """Quality gate checkpoint with validation"""
    name: str
    phase: Phase
    criteria: List[str]
    criticality: GateCriticality = GateCriticality.CRITICAL
    passed: bool = False
    timestamp: Optional[datetime] = None
    notes: str = ""
    validation_result: Dict[str, Any] = field(default_factory=dict)

    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate gate criteria against context

        Args:
            context: Context data for validation

        Returns:
            True if all criteria are met
        """
        self.timestamp = datetime.now()
        self.validation_result = {}

        # Default validation: check if all criteria keys exist in context
        all_passed = True
        for criterion in self.criteria:
            criterion_met = criterion in context and context[criterion]
            self.validation_result[criterion] = criterion_met

            if not criterion_met:
                all_passed = False
                logger.warning(
                    "Quality gate criterion not met",
                    gate=self.name,
                    criterion=criterion
                )

        self.passed = all_passed

        logger.info(
            "Quality gate validated",
            gate=self.name,
            phase=self.phase.value,
            passed=self.passed,
            criticality=self.criticality.value
        )

        return self.passed

    def should_block(self) -> bool:
        """Check if this gate should block progression"""
        return self.criticality == GateCriticality.BLOCKER and not self.passed


@dataclass
class PACTContext:
    """Shared context for PACT workflow"""
    task_description: str
    phase: Phase
    results: List[AgentResult] = field(default_factory=list)
    quality_gates: List[QualityGate] = field(default_factory=list)
    shared_artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: AgentResult) -> None:
        """Add an agent result to context"""
        self.results.append(result)
        logger.debug(
            "Result added to PACT context",
            agent=result.agent_name,
            success=result.success
        )

    def add_gate(self, gate: QualityGate) -> None:
        """Add a quality gate to context"""
        self.quality_gates.append(gate)
        logger.debug(
            "Quality gate added",
            gate=gate.name,
            criticality=gate.criticality.value
        )

    def get_summary(self) -> dict:
        """Get context summary"""
        return {
            "task": self.task_description[:100],
            "phase": self.phase.value,
            "results_count": len(self.results),
            "successful_results": sum(1 for r in self.results if r.success),
            "gates_count": len(self.quality_gates),
            "gates_passed": sum(1 for g in self.quality_gates if g.passed),
            "gates_blocking": sum(1 for g in self.quality_gates if g.should_block())
        }


# =============================================================================
# QUALITY GATES DEFINITIONS
# =============================================================================

DEFAULT_QUALITY_GATES = {
    Phase.PLANNING: [
        QualityGate(
            name="planning_complete",
            phase=Phase.PLANNING,
            criteria=["task_breakdown", "dependencies_identified", "success_criteria"],
            criticality=GateCriticality.BLOCKER
        ),
        QualityGate(
            name="planning_validated",
            phase=Phase.PLANNING,
            criteria=["complexity_assessed", "agents_assigned"],
            criticality=GateCriticality.CRITICAL
        ),
    ],

    Phase.ACTION: [
        QualityGate(
            name="action_complete",
            phase=Phase.ACTION,
            criteria=["all_agents_executed", "no_critical_errors"],
            criticality=GateCriticality.BLOCKER
        ),
        QualityGate(
            name="action_quality",
            phase=Phase.ACTION,
            criteria=["code_written", "changes_documented"],
            criticality=GateCriticality.CRITICAL
        ),
    ],

    Phase.COORDINATION: [
        QualityGate(
            name="coordination_complete",
            phase=Phase.COORDINATION,
            criteria=["conflicts_resolved", "outputs_integrated"],
            criticality=GateCriticality.BLOCKER
        ),
    ],

    Phase.TESTING: [
        QualityGate(
            name="tests_passing",
            phase=Phase.TESTING,
            criteria=["unit_tests_pass", "integration_tests_pass"],
            criticality=GateCriticality.BLOCKER
        ),
        QualityGate(
            name="code_quality",
            phase=Phase.TESTING,
            criteria=["linting_pass", "security_scan_pass"],
            criticality=GateCriticality.CRITICAL
        ),
    ],
}


# =============================================================================
# PACT ORCHESTRATOR
# =============================================================================

class PACTOrchestrator:
    """
    PACT Framework Orchestrator V2

    Implements Planning → Action → Coordination → Testing workflow
    with quality gates, structured logging, and comprehensive error handling.
    """

    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        self.orchestrator = orchestrator or Orchestrator()
        self.context: Optional[PACTContext] = None
        self.error_handler = get_error_handler()

        logger.info("PACT Orchestrator initialized")

    @log_execution_time()
    async def execute_pact_workflow(
        self,
        task: str,
        custom_gates: Optional[Dict[Phase, List[QualityGate]]] = None,
        **kwargs
    ) -> PACTContext:
        """
        Execute full PACT workflow with quality gates

        Args:
            task: Task description
            custom_gates: Custom quality gates (uses defaults if None)
            **kwargs: Additional arguments

        Returns:
            PACTContext with all results and gates

        Raises:
            QualityGateFailure: If a blocking gate fails
        """
        self.context = PACTContext(
            task_description=task,
            phase=Phase.PLANNING
        )

        quality_gates = custom_gates or DEFAULT_QUALITY_GATES

        with LogContext(workflow="PACT", task_preview=task[:50]):
            logger.info(
                "Starting PACT workflow",
                task=task[:100]
            )

            try:
                # Phase 1: Planning
                await self._execute_planning_phase(quality_gates)

                # Phase 2: Action (Parallel)
                await self._execute_action_phase(quality_gates)

                # Phase 3: Coordination
                await self._execute_coordination_phase(quality_gates)

                # Phase 4: Testing
                await self._execute_testing_phase(quality_gates)

                logger.info(
                    "PACT workflow complete",
                    **self.context.get_summary()
                )

                return self.context

            except QualityGateFailure as e:
                logger.error(
                    "PACT workflow failed at quality gate",
                    error=str(e),
                    phase=self.context.phase.value
                )
                raise

            except Exception as e:
                logger.exception(
                    "PACT workflow failed with exception",
                    error=str(e),
                    phase=self.context.phase.value
                )
                self.error_handler.record_error(
                    e,
                    context={"workflow": "PACT", "task": task}
                )
                raise

    async def _execute_planning_phase(
        self,
        quality_gates: Dict[Phase, List[QualityGate]]
    ) -> None:
        """Execute Planning phase"""
        self.context.phase = Phase.PLANNING

        logger.info("Starting PACT Planning phase")

        # Execute planning agent
        result = await self.orchestrator.execute_single(
            "architect-review",
            f"""Break down this task into subtasks with dependencies:

{self.context.task_description}

Provide:
1. Task breakdown with IDs
2. Dependencies between tasks
3. Complexity assessment (1-10)
4. Recommended agents for each task
5. Success criteria"""
        )

        self.context.add_result(result)

        # Validate planning gates
        gates = quality_gates.get(Phase.PLANNING, [])
        for gate in gates:
            self.context.add_gate(gate)

            # Simple validation: check if result was successful
            gate_context = {
                "task_breakdown": result.success,
                "dependencies_identified": result.success,
                "success_criteria": result.success,
                "complexity_assessed": result.success,
                "agents_assigned": result.success,
            }

            gate.validate(gate_context)

            if gate.should_block():
                raise QualityGateFailure(
                    f"Planning gate '{gate.name}' failed and is blocking"
                )

        logger.info("Planning phase complete")

    async def _execute_action_phase(
        self,
        quality_gates: Dict[Phase, List[QualityGate]]
    ) -> None:
        """Execute Action phase (parallel)"""
        self.context.phase = Phase.ACTION

        logger.info("Starting PACT Action phase (parallel execution)")

        # Get planning result
        planning_output = self.context.results[0].output if self.context.results else ""

        # Execute action agents in parallel
        swarm_result = await self.orchestrator.execute_parallel_swarm(
            ["frontend-developer", "backend-architect", "test-automator"],
            f"""Based on this plan, implement your part:

{planning_output}

Original task: {self.context.task_description}"""
        )

        # Add all results to context
        for result in swarm_result.results:
            self.context.add_result(result)

        # Validate action gates
        gates = quality_gates.get(Phase.ACTION, [])
        for gate in gates:
            self.context.add_gate(gate)

            gate_context = {
                "all_agents_executed": len(swarm_result.results) > 0,
                "no_critical_errors": all(r.success for r in swarm_result.results),
                "code_written": swarm_result.success,
                "changes_documented": swarm_result.success,
            }

            gate.validate(gate_context)

            if gate.should_block():
                raise QualityGateFailure(
                    f"Action gate '{gate.name}' failed and is blocking"
                )

        logger.info("Action phase complete")

    async def _execute_coordination_phase(
        self,
        quality_gates: Dict[Phase, List[QualityGate]]
    ) -> None:
        """Execute Coordination phase"""
        self.context.phase = Phase.COORDINATION

        logger.info("Starting PACT Coordination phase")

        # Summarize action results
        action_results = self.context.results[1:]  # Skip planning result
        summary = "\n\n".join([
            f"[{r.agent_name}]: {r.output[:500]}..."
            for r in action_results
        ])

        # Execute coordination
        result = await self.orchestrator.execute_single(
            "code-reviewer",
            f"""Review and coordinate these agent outputs for consistency:

{summary}

Check for:
1. Conflicts between outputs
2. Integration points
3. Missing pieces
4. Overall coherence"""
        )

        self.context.add_result(result)

        # Validate coordination gates
        gates = quality_gates.get(Phase.COORDINATION, [])
        for gate in gates:
            self.context.add_gate(gate)

            gate_context = {
                "conflicts_resolved": result.success,
                "outputs_integrated": result.success,
            }

            gate.validate(gate_context)

            if gate.should_block():
                raise QualityGateFailure(
                    f"Coordination gate '{gate.name}' failed and is blocking"
                )

        logger.info("Coordination phase complete")

    async def _execute_testing_phase(
        self,
        quality_gates: Dict[Phase, List[QualityGate]]
    ) -> None:
        """Execute Testing phase"""
        self.context.phase = Phase.TESTING

        logger.info("Starting PACT Testing phase")

        # Execute testing
        result = await self.orchestrator.execute_single(
            "test-automator",
            f"""Validate all changes made for this task:

{self.context.task_description}

Run:
1. Unit tests
2. Integration tests
3. Linting
4. Security scan

Report any failures with clear remediation steps."""
        )

        self.context.add_result(result)

        # Validate testing gates
        gates = quality_gates.get(Phase.TESTING, [])
        for gate in gates:
            self.context.add_gate(gate)

            gate_context = {
                "unit_tests_pass": result.success,
                "integration_tests_pass": result.success,
                "linting_pass": result.success,
                "security_scan_pass": result.success,
            }

            gate.validate(gate_context)

            if gate.should_block():
                raise QualityGateFailure(
                    f"Testing gate '{gate.name}' failed and is blocking"
                )

        logger.info("Testing phase complete")


# =============================================================================
# BMAD LIFECYCLE MANAGER
# =============================================================================

class BMADLifecycleManager:
    """
    BMAD Lifecycle Implementation
    Research → Design → Implementation → Deployment
    """

    def __init__(self, orchestrator: Optional[Orchestrator] = None):
        self.orchestrator = orchestrator or Orchestrator()
        self.pact = PACTOrchestrator(self.orchestrator)
        self.current_phase: Optional[Phase] = None
        self.phase_results: Dict[Phase, Any] = {}

        logger.info("BMAD Lifecycle Manager initialized")

    @log_execution_time()
    async def execute_full_bmad(
        self,
        project_description: str,
        **kwargs
    ) -> Dict[Phase, Any]:
        """
        Execute full BMAD lifecycle

        Args:
            project_description: Project description
            **kwargs: Additional arguments

        Returns:
            Dictionary of phase results
        """
        with LogContext(lifecycle="BMAD", project=project_description[:50]):
            logger.info(
                "Starting BMAD lifecycle",
                project=project_description[:100]
            )

            phases = [
                (Phase.RESEARCH, self._research_phase),
                (Phase.DESIGN, self._design_phase),
                (Phase.PLANNING, self._implementation_phase),
                (Phase.DEPLOYMENT, self._deployment_phase),
            ]

            for phase, executor in phases:
                self.current_phase = phase

                logger.info(
                    "Starting BMAD phase",
                    phase=phase.value
                )

                try:
                    result = await executor(project_description)
                    self.phase_results[phase] = result

                    logger.info(
                        "BMAD phase complete",
                        phase=phase.value
                    )

                except Exception as e:
                    logger.error(
                        "BMAD phase failed",
                        phase=phase.value,
                        error=str(e)
                    )
                    break

            logger.info(
                "BMAD lifecycle complete",
                phases_completed=len(self.phase_results)
            )

            return self.phase_results

    async def _research_phase(self, description: str) -> SwarmResult:
        """Research phase"""
        return await self.orchestrator.execute_swarm_pattern(
            "code-analysis",
            f"Research and analyze requirements for: {description}"
        )

    async def _design_phase(self, description: str) -> PACTContext:
        """Design phase"""
        return await self.pact.execute_pact_workflow(
            f"Design architecture for: {description}"
        )

    async def _implementation_phase(self, description: str) -> SwarmResult:
        """Implementation phase"""
        return await self.orchestrator.execute_swarm_pattern(
            "full-stack",
            f"Implement: {description}"
        )

    async def _deployment_phase(self, description: str) -> SwarmResult:
        """Deployment phase"""
        return await self.orchestrator.execute_swarm_pattern(
            "devops-swarm",
            f"Deploy: {description}"
        )


# =============================================================================
# CLI
# =============================================================================

async def main():
    """CLI entry point for PACT/BMAD workflows"""
    import argparse
    from rich.console import Console

    console = Console()

    parser = argparse.ArgumentParser(description="PACT/BMAD Workflow Orchestrator")
    parser.add_argument("task", help="Task or project description")
    parser.add_argument("--pact", action="store_true", help="Run PACT workflow")
    parser.add_argument("--bmad", action="store_true", help="Run BMAD lifecycle")

    args = parser.parse_args()

    try:
        if args.pact:
            pact = PACTOrchestrator()
            result = await pact.execute_pact_workflow(args.task)

            console.print(f"\n[green]PACT Workflow Complete![/green]")
            console.print(f"Results: {len(result.results)}")
            console.print(f"Gates: {sum(1 for g in result.quality_gates if g.passed)}/{len(result.quality_gates)} passed")

        elif args.bmad:
            bmad = BMADLifecycleManager()
            results = await bmad.execute_full_bmad(args.task)

            console.print(f"\n[green]BMAD Lifecycle Complete![/green]")
            console.print(f"Phases completed: {len(results)}")

        else:
            console.print("[yellow]Please specify --pact or --bmad[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())

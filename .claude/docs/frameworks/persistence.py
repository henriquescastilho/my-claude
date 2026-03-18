#!/usr/bin/env python3
"""
Persistence Layer for Agent SDK Orchestrator
============================================
SQLite-based execution history and result storage

Author: Pedro
Version: 2.0.0
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from config import get_config
from logger import get_logger, log_execution_time
from orchestrator_v2 import SwarmResult, AgentResult

logger = get_logger(__name__)


# =============================================================================
# DATABASE SCHEMA
# =============================================================================

SCHEMA = """
-- Executions table
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE NOT NULL,
    execution_type TEXT NOT NULL, -- 'swarm', 'pact', 'bmad'
    task_description TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    success BOOLEAN,
    total_tokens INTEGER DEFAULT 0,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent results table
CREATE TABLE IF NOT EXISTS agent_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_role TEXT NOT NULL,
    output TEXT,
    success BOOLEAN,
    duration_seconds REAL,
    tokens_used INTEGER DEFAULT 0,
    model TEXT,
    error TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
);

-- Quality gates table
CREATE TABLE IF NOT EXISTS quality_gates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    gate_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    criticality TEXT NOT NULL,
    passed BOOLEAN,
    criteria JSON,
    validation_result JSON,
    notes TEXT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at);
CREATE INDEX IF NOT EXISTS idx_executions_type ON executions(execution_type);
CREATE INDEX IF NOT EXISTS idx_executions_success ON executions(success);
CREATE INDEX IF NOT EXISTS idx_agent_results_execution_id ON agent_results(execution_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_agent_name ON agent_results(agent_name);
CREATE INDEX IF NOT EXISTS idx_quality_gates_execution_id ON quality_gates(execution_id);
"""


# =============================================================================
# PERSISTENCE MANAGER
# =============================================================================

class PersistenceManager:
    """Manages execution history and results in SQLite"""

    def __init__(self, db_path: Optional[Path] = None):
        self.config = get_config()
        self.db_path = db_path or self.config.persistence.db_path

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(
            "Persistence manager initialized",
            db_path=str(self.db_path)
        )

    def _init_database(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)
            logger.debug("Database schema initialized")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    @log_execution_time()
    def save_swarm_execution(
        self,
        swarm_result: SwarmResult,
        execution_type: str = "swarm"
    ) -> str:
        """
        Save swarm execution to database

        Args:
            swarm_result: SwarmResult to save
            execution_type: Type of execution ('swarm', 'pact', 'bmad')

        Returns:
            Execution ID
        """
        execution_id = swarm_result.name

        with self._get_connection() as conn:
            # Save execution
            conn.execute("""
                INSERT INTO executions (
                    execution_id, execution_type, task_description,
                    started_at, completed_at, duration_seconds,
                    success, total_tokens, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                execution_type,
                swarm_result.metadata.get("task", "")[:500],
                datetime.now() - timedelta(seconds=swarm_result.duration),
                datetime.now(),
                swarm_result.duration,
                swarm_result.success,
                swarm_result.total_tokens,
                json.dumps(swarm_result.metadata)
            ))

            # Save agent results
            for result in swarm_result.results:
                conn.execute("""
                    INSERT INTO agent_results (
                        execution_id, agent_name, agent_role,
                        output, success, duration_seconds,
                        tokens_used, model, error, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution_id,
                    result.agent_name,
                    result.role.value,
                    result.output[:5000] if result.output else None,  # Limit size
                    result.success,
                    result.duration_seconds,
                    result.tokens_used,
                    result.model,
                    result.error,
                    json.dumps(result.metadata)
                ))

            conn.commit()

        logger.info(
            "Swarm execution saved",
            execution_id=execution_id,
            agents=len(swarm_result.results)
        )

        return execution_id

    def save_quality_gate(
        self,
        execution_id: str,
        gate: Any  # QualityGate from pact_framework_v2
    ) -> None:
        """Save quality gate result"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO quality_gates (
                    execution_id, gate_name, phase, criticality,
                    passed, criteria, validation_result, notes, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                gate.name,
                gate.phase.value,
                gate.criticality.value,
                gate.passed,
                json.dumps(gate.criteria),
                json.dumps(gate.validation_result),
                gate.notes,
                gate.timestamp.isoformat() if gate.timestamp else None
            ))

            conn.commit()

        logger.debug(
            "Quality gate saved",
            execution_id=execution_id,
            gate=gate.name,
            passed=gate.passed
        )

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID"""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM executions WHERE execution_id = ?
            """, (execution_id,)).fetchone()

            if not row:
                return None

            # Get agent results
            agent_rows = conn.execute("""
                SELECT * FROM agent_results WHERE execution_id = ?
                ORDER BY created_at
            """, (execution_id,)).fetchall()

            # Get quality gates
            gate_rows = conn.execute("""
                SELECT * FROM quality_gates WHERE execution_id = ?
                ORDER BY timestamp
            """, (execution_id,)).fetchall()

            return {
                "execution": dict(row),
                "agents": [dict(r) for r in agent_rows],
                "gates": [dict(r) for r in gate_rows]
            }

    def list_executions(
        self,
        limit: int = 100,
        offset: int = 0,
        execution_type: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List executions with filtering

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            execution_type: Filter by type
            success_only: Only successful executions

        Returns:
            List of execution dictionaries
        """
        query = "SELECT * FROM executions WHERE 1=1"
        params = []

        if execution_type:
            query += " AND execution_type = ?"
            params.append(execution_type)

        if success_only:
            query += " AND success = 1"

        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self._get_connection() as conn:
            stats = {}

            # Total executions
            stats["total_executions"] = conn.execute(
                "SELECT COUNT(*) FROM executions"
            ).fetchone()[0]

            # Successful executions
            stats["successful_executions"] = conn.execute(
                "SELECT COUNT(*) FROM executions WHERE success = 1"
            ).fetchone()[0]

            # Total tokens used
            stats["total_tokens"] = conn.execute(
                "SELECT SUM(total_tokens) FROM executions"
            ).fetchone()[0] or 0

            # Average duration
            stats["avg_duration"] = conn.execute(
                "SELECT AVG(duration_seconds) FROM executions"
            ).fetchone()[0] or 0.0

            # Executions by type
            type_counts = conn.execute("""
                SELECT execution_type, COUNT(*) as count
                FROM executions
                GROUP BY execution_type
            """).fetchall()
            stats["by_type"] = {row[0]: row[1] for row in type_counts}

            # Most used agents
            agent_counts = conn.execute("""
                SELECT agent_name, COUNT(*) as count
                FROM agent_results
                GROUP BY agent_name
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            stats["top_agents"] = {row[0]: row[1] for row in agent_counts}

            # Quality gate stats
            stats["quality_gates_total"] = conn.execute(
                "SELECT COUNT(*) FROM quality_gates"
            ).fetchone()[0]

            stats["quality_gates_passed"] = conn.execute(
                "SELECT COUNT(*) FROM quality_gates WHERE passed = 1"
            ).fetchone()[0]

            return stats

    @log_execution_time()
    def cleanup_old_executions(
        self,
        days: Optional[int] = None
    ) -> int:
        """
        Delete executions older than specified days

        Args:
            days: Number of days to keep (from config if None)

        Returns:
            Number of executions deleted
        """
        days = days or self.config.persistence.history_retention_days
        cutoff_date = datetime.now() - timedelta(days=days)

        with self._get_connection() as conn:
            # Get IDs to delete
            rows = conn.execute("""
                SELECT execution_id FROM executions
                WHERE started_at < ?
            """, (cutoff_date.isoformat(),)).fetchall()

            execution_ids = [row[0] for row in rows]

            if not execution_ids:
                logger.info("No old executions to clean up")
                return 0

            # Delete from all tables
            placeholders = ','.join('?' * len(execution_ids))

            conn.execute(f"""
                DELETE FROM agent_results
                WHERE execution_id IN ({placeholders})
            """, execution_ids)

            conn.execute(f"""
                DELETE FROM quality_gates
                WHERE execution_id IN ({placeholders})
            """, execution_ids)

            conn.execute(f"""
                DELETE FROM executions
                WHERE execution_id IN ({placeholders})
            """, execution_ids)

            conn.commit()

        logger.info(
            "Cleaned up old executions",
            deleted_count=len(execution_ids),
            cutoff_date=cutoff_date.isoformat()
        )

        return len(execution_ids)

    def export_to_json(
        self,
        output_file: Path,
        execution_id: Optional[str] = None
    ) -> None:
        """
        Export execution(s) to JSON file

        Args:
            output_file: Output file path
            execution_id: Specific execution ID (all if None)
        """
        if execution_id:
            data = self.get_execution(execution_id)
        else:
            executions = self.list_executions(limit=1000)
            data = {
                "executions": executions,
                "statistics": self.get_statistics()
            }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(
            "Exported to JSON",
            file=str(output_file)
        )


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_persistence_manager: Optional[PersistenceManager] = None


def get_persistence_manager() -> PersistenceManager:
    """Get global persistence manager instance"""
    global _persistence_manager

    if _persistence_manager is None:
        _persistence_manager = PersistenceManager()

    return _persistence_manager


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI for persistence management"""
    import argparse
    from rich.console import Console
    from rich.table import Table

    console = Console()

    parser = argparse.ArgumentParser(description="Persistence Manager CLI")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--list", action="store_true", help="List executions")
    parser.add_argument("--limit", type=int, default=20, help="Limit results")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old executions")
    parser.add_argument("--export", type=str, help="Export to JSON file")
    parser.add_argument("--execution-id", type=str, help="Specific execution ID")

    args = parser.parse_args()

    pm = get_persistence_manager()

    if args.stats:
        stats = pm.get_statistics()

        console.print("\n[cyan]Execution Statistics[/cyan]\n")
        console.print(f"Total Executions: {stats['total_executions']}")
        console.print(f"Successful: {stats['successful_executions']}")
        console.print(f"Total Tokens: {stats['total_tokens']:,}")
        console.print(f"Avg Duration: {stats['avg_duration']:.2f}s")

        console.print(f"\n[cyan]By Type:[/cyan]")
        for exec_type, count in stats['by_type'].items():
            console.print(f"  {exec_type}: {count}")

        console.print(f"\n[cyan]Top Agents:[/cyan]")
        for agent, count in list(stats['top_agents'].items())[:5]:
            console.print(f"  {agent}: {count}")

    elif args.list:
        executions = pm.list_executions(limit=args.limit)

        table = Table(title="Recent Executions")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Duration", style="green")
        table.add_column("Success", style="yellow")
        table.add_column("Started", style="white")

        for exec in executions:
            table.add_row(
                exec['execution_id'][:20],
                exec['execution_type'],
                f"{exec['duration_seconds']:.2f}s",
                "✓" if exec['success'] else "✗",
                str(exec['started_at'])[:19]
            )

        console.print(table)

    elif args.cleanup:
        deleted = pm.cleanup_old_executions()
        console.print(f"[green]Deleted {deleted} old executions[/green]")

    elif args.export:
        pm.export_to_json(
            Path(args.export),
            execution_id=args.execution_id
        )
        console.print(f"[green]Exported to {args.export}[/green]")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

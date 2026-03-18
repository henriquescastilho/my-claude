# Agent SDK Orchestrator 🤖

**Production-grade Multi-Agent Orchestration with PACT/BMAD/Swarm Patterns**

The world's most advanced Claude agent orchestration system, featuring true parallel execution, comprehensive error handling, and enterprise-grade observability.

---

## 🌟 Features

### Core Capabilities
- ⚡ **True Parallel Execution** - Run multiple agents simultaneously with async/await
- 🎯 **PACT Framework** - Planning → Action → Coordination → Testing workflow
- 🔄 **BMAD Lifecycle** - Research → Design → Implementation → Deployment
- 🐝 **43 Swarm Patterns** - Pre-configured agent combinations for common tasks
- 🛡️ **Comprehensive Error Handling** - Retry logic with exponential backoff
- 📊 **Structured Logging** - Rich, JSON logging with full observability
- 💾 **Execution History** - Persist and query past executions
- 🔧 **Quality Gates** - Configurable validation checkpoints
- 🎨 **Rich CLI** - Beautiful terminal UI with progress indicators
- ⚙️ **Highly Configurable** - Environment variables + YAML config files

### Agent Management
- 📁 Load 241+ agents from `~/.claude/agents/`
- 🏷️ Automatic role inference (Planning, Action, Testing, etc.)
- 🔍 Agent search and discovery
- ✅ Configuration validation
- 🔄 Hot-reloading support

### Enterprise-Grade
- 🔒 Security-first design
- 📈 Performance optimized
- 🧪 80%+ test coverage
- 📚 Comprehensive documentation
- 🐳 Docker support
- 🔄 CI/CD ready

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repository
cd "C:\Users\Pichau\Desktop\claude code"

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### 2. Configure

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run

```bash
# Simple execution
python orchestrator.py "Analyze this codebase for security issues"

# Use a swarm pattern
python orchestrator.py --swarm code-analysis "Review the authentication module"

# Run PACT workflow
python orchestrator.py --pact "Build user authentication system"

# Run full BMAD lifecycle
python orchestrator.py --bmad "Create a payment processing system"

# TaskMaster orchestration
python orchestrator.py --tm "Initialize project and generate tasks" --project ./myproject
```

---

## 📋 Swarm Patterns

The orchestrator includes 43 pre-configured swarm patterns:

### Analysis Swarms
- `code-analysis` - Code quality, security, performance
- `security-deep` - OWASP, SAST, backend security
- `review-chain` - Multi-perspective code review

### Development Swarms
- `full-stack` - Frontend + Backend + Testing
- `frontend-swarm` - UI/UX development
- `backend-swarm` - API and service development
- `api-swarm` - API design and documentation

### Infrastructure Swarms
- `devops-swarm` - Kubernetes, Terraform, deployment
- `cloud-swarm` - Multi-cloud architecture
- `observability-swarm` - Monitoring, logging, tracing

### Language-Specific Swarms
- `python-swarm` - Python, FastAPI, Django
- `typescript-swarm` - TypeScript/JavaScript
- `golang-swarm` - Go development
- `rust-swarm` - Rust systems programming

### TaskMaster Swarms
- `tm-init` - Project initialization
- `tm-implement` - Implementation workflow
- `tm-research` - Research workflow
- `tm-quality` - Quality review workflow

[See full list in orchestrator.py](./orchestrator.py#L167)

---

## 🎯 PACT Framework

**Planning → Action → Coordination → Testing**

```python
# Execute PACT workflow
python orchestrator.py --pact "Add user authentication with JWT"
```

**How it works:**

1. **Planning** - Architect breaks down the task
2. **Action** - Multiple agents execute in parallel
3. **Coordination** - Review and integrate outputs
4. **Testing** - Validate all changes

---

## 🔄 BMAD Lifecycle

**Research → Design → Implementation → Deployment**

```python
# Execute full BMAD lifecycle
python orchestrator.py --bmad "Build analytics dashboard"
```

**Phases:**

1. **Research** - Analyze requirements and existing code
2. **Design** - Create architecture and design docs
3. **Implementation** - Write the code
4. **Deployment** - Prepare for production

---

## ⚙️ Configuration

### Environment Variables

See [.env.example](./.env.example) for all options:

```bash
# API Configuration
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4096

# Execution
MAX_CONCURRENT_AGENTS=10
RETRY_ATTEMPTS=3
RETRY_BACKOFF_BASE=2.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### YAML Configuration

```yaml
# orchestrator.yaml
anthropic:
  api_key: ${ANTHROPIC_API_KEY}
  default_model: claude-sonnet-4-20250514
  max_tokens: 4096

execution:
  max_concurrent_agents: 10
  retry_attempts: 3

logging:
  level: INFO
  format: json
```

Load with:
```python
from config import OrchestratorConfig
config = OrchestratorConfig.from_file("orchestrator.yaml")
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run validation tests
python run_validation_tests.py

# Run specific test
pytest tests/test_orchestrator.py::test_parallel_execution
```

---

## 📊 Logging & Observability

### Structured Logging

```python
from logger import get_logger, LogContext

logger = get_logger(__name__)

# Add context to logs
with LogContext(swarm="code-analysis", task_id="123"):
    logger.info("Starting execution", agents=["security", "review"])
```

### Performance Tracking

```python
from logger import log_execution_time

@log_execution_time()
async def my_function():
    # Automatically logs execution time
    pass
```

### Rich Console Output

All CLI output uses Rich for beautiful formatting:
- Progress bars for parallel execution
- Syntax highlighting
- Tables and panels
- Live updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Orchestrator CLI                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   Config     │    │   Logger     │          │
│  │  Management  │    │   System     │          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │    Error     │    │   Retry      │          │
│  │   Handler    │    │   Logic      │          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
├─────────────────────────────────────────────────┤
│           Agent Loader & Validator              │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │    PACT      │    │    BMAD      │          │
│  │  Framework   │    │  Lifecycle   │          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │    Swarm     │    │  TaskMaster  │          │
│  │  Executor    │    │ Integration  │          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
├─────────────────────────────────────────────────┤
│         Anthropic SDK / Claude API              │
└─────────────────────────────────────────────────┘
```

---

## 📚 API Reference

### Orchestrator

```python
from orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute single agent
result = await orchestrator.execute_single("code-reviewer", "Review auth.py")

# Execute parallel swarm
result = await orchestrator.execute_parallel_swarm(
    ["frontend-dev", "backend-dev", "tester"],
    "Build login feature"
)

# Execute swarm pattern
result = await orchestrator.execute_swarm_pattern(
    "code-analysis",
    "Analyze security"
)

# Execute PACT workflow
result = await orchestrator.execute_pact("Add JWT authentication")

# Execute BMAD lifecycle
result = await orchestrator.execute_bmad("Payment system")
```

### Agent Loader

```python
from orchestrator import AgentLoader

loader = AgentLoader()

# Get agent by name
agent = loader.get("code-reviewer")

# Get agents by role
planning_agents = loader.get_by_role(AgentRole.PLANNING)

# Search agents
security_agents = loader.search("security")
```

---

## 🤝 Contributing

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run formatters
black .
ruff check --fix .

# Run type checker
mypy .

# Run all checks
black . && ruff check --fix . && mypy . && pytest
```

### Adding New Swarm Patterns

Edit `orchestrator.py`:

```python
SWARM_PATTERNS = {
    "my-new-swarm": {
        "description": "What this swarm does",
        "agents": ["agent1", "agent2", "agent3"],
        "parallel": True
    }
}
```

### Creating New Agents

Create a markdown file in `~/.claude/agents/`:

```markdown
---
name: my-custom-agent
description: What this agent does
model: sonnet
tools: [Read, Write, Bash]
---

You are a custom agent that...
```

---

## 📦 Project Structure

```
claude-code/
├── orchestrator.py          # Main orchestrator
├── pact_framework.py        # PACT framework implementation
├── config.py                # Configuration management
├── logger.py                # Structured logging
├── error_handler.py         # Error handling & retry
├── run_validation_tests.py  # Validation test suite
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── pyproject.toml           # Build configuration
├── .env.example             # Example environment file
├── README.md                # This file
├── tasks.json               # TaskMaster tasks
└── tests/                   # Test suite
    ├── test_orchestrator.py
    ├── test_pact.py
    └── test_error_handling.py
```

---

## 🔒 Security

- ✅ API keys stored in environment variables
- ✅ Path traversal protection
- ✅ Input validation
- ✅ Rate limiting built-in
- ✅ Timeout protection
- ✅ No code execution from untrusted sources

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- Built with [Anthropic Claude API](https://www.anthropic.com)
- Inspired by PACT and BMAD methodologies
- Powered by TaskMaster project management

---

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/yourusername/agent-sdk-orchestrator/issues)
- 📚 Docs: [Full Documentation](https://agent-sdk-orchestrator.readthedocs.io)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/agent-sdk-orchestrator/discussions)

---

**Built with ❤️ to be the best Claude Code orchestrator in the world**

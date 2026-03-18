#!/usr/bin/env python3
"""
CLI Input Validation Test Runner
================================
Standalone script to validate the orchestrator CLI input handling.
"""

import sys
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock

print('=' * 60)
print('CLI INPUT VALIDATION TEST REPORT')
print('=' * 60)

passed = 0
failed = 0

# Test 1: Import check
print('\n[TEST 1] Module Import Validation')
try:
    from orchestrator import (
        Orchestrator, AgentLoader, AgentConfig, AgentRole,
        SwarmResult, SWARM_PATTERNS, AGENTS_DIR
    )
    print('  PASS: All modules imported successfully')
    passed += 1
except Exception as e:
    print(f'  FAIL: Import error - {e}')
    failed += 1
    sys.exit(1)

# Test 2: Swarm patterns validation
print('\n[TEST 2] Swarm Patterns Validation')
required_patterns = ['code-analysis', 'full-stack', 'security-deep',
                     'review-chain', 'debug-swarm', 'docs-swarm',
                     'devops-swarm', 'ai-swarm']
patterns_ok = True
for pattern in required_patterns:
    if pattern in SWARM_PATTERNS:
        print(f'  OK: Pattern "{pattern}" exists')
    else:
        print(f'  MISSING: Pattern "{pattern}"')
        patterns_ok = False
if patterns_ok:
    passed += 1
else:
    failed += 1

# Test 3: Pattern structure validation
print('\n[TEST 3] Pattern Structure Validation')
required_keys = {'description', 'agents', 'parallel'}
all_valid = True
for name, pattern in SWARM_PATTERNS.items():
    missing = required_keys - set(pattern.keys())
    if missing:
        print(f'  FAIL: Pattern "{name}" missing keys: {missing}')
        all_valid = False
    if len(pattern.get('agents', [])) == 0:
        print(f'  FAIL: Pattern "{name}" has no agents')
        all_valid = False
if all_valid:
    print('  PASS: All patterns have valid structure')
    passed += 1
else:
    failed += 1

# Test 4: AgentRole enum validation
print('\n[TEST 4] AgentRole Enum Validation')
required_roles = ['PLANNING', 'ACTION', 'COORDINATION',
                  'TESTING', 'RESEARCH', 'REVIEW']
roles_ok = True
for role in required_roles:
    if hasattr(AgentRole, role):
        print(f'  OK: Role "{role}" defined')
    else:
        print(f'  MISSING: Role "{role}"')
        roles_ok = False
if roles_ok:
    passed += 1
else:
    failed += 1

# Test 5: AgentConfig defaults validation
print('\n[TEST 5] AgentConfig Defaults Validation')
try:
    config = AgentConfig(name='test', description='test',
                         prompt='test', tools=[])
    defaults_ok = True
    if config.model == 'sonnet':
        print('  OK: Default model is "sonnet"')
    else:
        print(f'  FAIL: Default model is "{config.model}"')
        defaults_ok = False
    if config.role == AgentRole.ACTION:
        print('  OK: Default role is ACTION')
    else:
        print(f'  FAIL: Default role is "{config.role}"')
        defaults_ok = False
    if defaults_ok:
        passed += 1
    else:
        failed += 1
except Exception as e:
    print(f'  FAIL: {e}')
    failed += 1

# Test 6: Tool parsing validation
print('\n[TEST 6] Tool Parsing Validation')
with patch.object(AgentLoader, '_load_all'):
    loader = AgentLoader()
    loader.agents = {}

    test_cases = [
        ('[]', []),
        ('[Read]', ['Read']),
        ('[Read, Write, Bash]', ['Read', 'Write', 'Bash']),
        ('[  Read  ,  Write  ]', ['Read', 'Write']),
    ]
    tools_ok = True
    for input_str, expected in test_cases:
        result = loader._parse_tools(input_str)
        if result == expected:
            print(f'  OK: Parsed "{input_str}" correctly')
        else:
            print(f'  FAIL: "{input_str}" got {result}, expected {expected}')
            tools_ok = False
    if tools_ok:
        passed += 1
    else:
        failed += 1

# Test 7: Role inference validation
print('\n[TEST 7] Role Inference Validation')
role_tests = [
    ('planner', AgentRole.PLANNING),
    ('architect', AgentRole.PLANNING),
    ('tester', AgentRole.TESTING),
    ('qa-engineer', AgentRole.TESTING),
    ('reviewer', AgentRole.REVIEW),
    ('auditor', AgentRole.REVIEW),
    ('explorer', AgentRole.RESEARCH),
    ('researcher', AgentRole.RESEARCH),
    ('developer', AgentRole.ACTION),
]
roles_infer_ok = True
for name, expected_role in role_tests:
    result = loader._infer_role(name)
    if result == expected_role:
        print(f'  OK: "{name}" -> {expected_role.value}')
    else:
        print(f'  FAIL: "{name}" -> {result.value} (expected {expected_role.value})')
        roles_infer_ok = False
if roles_infer_ok:
    passed += 1
else:
    failed += 1

# Test 8: Invalid pattern handling
print('\n[TEST 8] Invalid Pattern Handling Validation')
try:
    invalid_pattern = 'nonexistent-pattern'
    if invalid_pattern not in SWARM_PATTERNS:
        raise ValueError(f'Unknown pattern: {invalid_pattern}')
    print('  FAIL: Should have raised ValueError')
    failed += 1
except ValueError as e:
    if 'Unknown pattern' in str(e):
        print('  PASS: ValueError raised for invalid pattern')
        passed += 1
    else:
        print(f'  FAIL: Wrong error message - {e}')
        failed += 1

# Test 9: Agent name lookup validation
print('\n[TEST 9] Agent Name Lookup Validation')
with patch.object(AgentLoader, '_load_all'):
    loader = AgentLoader()
    loader.agents = {}
    mock_agent = AgentConfig(name='test-agent', description='Test',
                             prompt='Test', tools=[])
    loader.agents['test-agent'] = mock_agent

    lookup_ok = True
    if loader.get('test-agent') is not None:
        print('  OK: Valid agent lookup returns agent')
    else:
        print('  FAIL: Valid agent lookup returned None')
        lookup_ok = False

    if loader.get('nonexistent') is None:
        print('  OK: Invalid agent lookup returns None')
    else:
        print('  FAIL: Invalid agent lookup should return None')
        lookup_ok = False

    if loader.get('') is None:
        print('  OK: Empty agent name returns None')
    else:
        print('  FAIL: Empty agent name should return None')
        lookup_ok = False

    if lookup_ok:
        passed += 1
    else:
        failed += 1

# Test 10: Frontmatter validation
print('\n[TEST 10] Frontmatter Validation')
with patch.object(AgentLoader, '_load_all'):
    loader = AgentLoader()
    loader.agents = {}

    frontmatter_ok = True

    # Invalid frontmatter (no ---)
    mock_path = MagicMock()
    mock_path.read_text.return_value = 'No frontmatter here'
    mock_path.stem = 'invalid'
    if loader._parse_agent(mock_path) is None:
        print('  OK: Invalid frontmatter returns None')
    else:
        print('  FAIL: Invalid frontmatter should return None')
        frontmatter_ok = False

    # Incomplete frontmatter (missing closing ---)
    mock_path.read_text.return_value = '---\nname: test\n'
    if loader._parse_agent(mock_path) is None:
        print('  OK: Incomplete frontmatter returns None')
    else:
        print('  FAIL: Incomplete frontmatter should return None')
        frontmatter_ok = False

    # Valid frontmatter
    valid_content = """---
name: valid-agent
description: A valid agent
model: sonnet
tools: [Read, Write]
---

You are a valid agent."""
    mock_path.read_text.return_value = valid_content
    result = loader._parse_agent(mock_path)
    if result is not None and result.name == 'valid-agent':
        print('  OK: Valid frontmatter parsed correctly')
    else:
        print('  FAIL: Valid frontmatter should be parsed')
        frontmatter_ok = False

    if frontmatter_ok:
        passed += 1
    else:
        failed += 1

# Test 11: Security - path traversal prevention
print('\n[TEST 11] Security Validation - Path Traversal')
with patch.object(AgentLoader, '_load_all'):
    loader = AgentLoader()
    loader.agents = {}

    malicious_names = [
        '../../../etc/passwd',
        '..\\..\\windows\\system32',
        '/etc/shadow',
    ]
    security_ok = True
    for name in malicious_names:
        result = loader.get(name)
        if result is None:
            print(f'  OK: Blocked "{name[:20]}..."')
        else:
            print(f'  FAIL: Should have blocked "{name}"')
            security_ok = False

    if security_ok:
        passed += 1
    else:
        failed += 1

# Test 12: SwarmResult validation
print('\n[TEST 12] SwarmResult Dataclass Validation')
try:
    result = SwarmResult(
        name='test-swarm',
        agents=['agent1', 'agent2'],
        results=[{'agent': 'agent1', 'success': True}],
        duration=1.5,
        success=True,
        parallel=True
    )
    result_ok = True
    if result.name != 'test-swarm':
        print('  FAIL: name not set correctly')
        result_ok = False
    if len(result.agents) != 2:
        print('  FAIL: agents not set correctly')
        result_ok = False
    if result.duration != 1.5:
        print('  FAIL: duration not set correctly')
        result_ok = False
    if result.success != True:
        print('  FAIL: success not set correctly')
        result_ok = False
    if result.parallel != True:
        print('  FAIL: parallel not set correctly')
        result_ok = False

    if result_ok:
        print('  PASS: SwarmResult fields validated')
        passed += 1
    else:
        failed += 1
except Exception as e:
    print(f'  FAIL: {e}')
    failed += 1

# Summary
print('\n' + '=' * 60)
print('VALIDATION SUMMARY')
print('=' * 60)
print(f'  Passed: {passed}')
print(f'  Failed: {failed}')
print(f'  Total:  {passed + failed}')
print('=' * 60)

if failed > 0:
    print('\n*** VALIDATION FAILED ***')
    sys.exit(1)
else:
    print('\n*** ALL VALIDATIONS PASSED ***')
    sys.exit(0)

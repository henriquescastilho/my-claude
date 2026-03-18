# Profiles

## Global Settings

- model: `opus[1m]`
- enabled plugins: 11
- extra marketplaces: 8

## Profiles

### hackathon

- model: `sonnet`
- env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = `1`
- env `CLAUDE_PROFILE_MODE` = `hackathon`
- enabled plugins: 16

### mvp

- model: `sonnet`
- env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = `1`
- env `CLAUDE_PROFILE_MODE` = `mvp`
- enabled plugins: 10

### team

- model: `opus`
- env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = `1`
- env `CLAUDE_PROFILE_MODE` = `team`
- enabled plugins: 13

### xquads

- model: `opus`
- env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = `1`
- env `CLAUDE_PROFILE_MODE` = `xquads`
- enabled plugins: 17

### yolo

- model: `opus`
- env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` = `1`
- env `CLAUDE_PROFILE_MODE` = `yolo`
- enabled plugins: 25

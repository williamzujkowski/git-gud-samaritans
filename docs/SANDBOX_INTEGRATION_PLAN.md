# Sandbox Integration Plan

> Integrating moltdown VMs for isolated open source contributions

**Status**: Approved
**Version**: 1.2
**Date**: 2026-02-02

## Executive Summary

git-gud-samaritans needs isolated environments to safely clone, test, and contribute to external repositories. This plan integrates [moltdown](https://github.com/williamzujkowski/moltdown) - a libvirt/KVM VM toolkit - to provide sandboxed contribution environments.

## Business Value

| Benefit | Description |
|---------|-------------|
| **Risk Mitigation** | Running untrusted repo code in isolated VMs prevents host compromise |
| **Parallel Productivity** | 2-3 simultaneous contributions = 2-3x throughput |
| **Clean Contributions** | Each PR from pristine environment = no cross-contamination |
| **Reusable Infrastructure** | moltdown already battle-tested, minimal new code needed |

## Resource Configuration

**Host System**: 64GB RAM, 16 cores

| Allocation | RAM | Cores | Notes |
|------------|-----|-------|-------|
| Host Reserved | 16GB | 4 | OS + services + headroom |
| Available for VMs | 48GB | 12 | Sandbox pool |
| Per Sandbox (default) | 12GB | 4 | Standard profile |
| Max Concurrent | 3 | - | 36GB total |
| Warm Pool | 2 | - | Pre-created idle clones |

## Architecture

```
git-gud-samaritans/
├── tools/
│   └── moltdown/                    # Git submodule
├── src/git_gud_samaritans/
│   └── sandbox/
│       ├── __init__.py
│       ├── manager.py               # SandboxManager class (~200 LOC)
│       ├── cli.py                   # Click commands (~100 LOC)
│       ├── profiles.py              # Resource profiles
│       └── network.py               # Network isolation config
├── config/
│   └── sandbox.yaml                 # Profiles + security rules
└── docs/
    └── SANDBOX_INTEGRATION_PLAN.md  # This file
```

## CLI Design

### Core Commands

```bash
# Create sandbox for a specific issue
ggs sandbox create https://github.com/owner/repo/issues/123
# → Creates linked clone: ggs-owner-repo-123
# → Clones target repo inside VM
# → Returns sandbox ID

# List active sandboxes
ggs sandbox list
# ID                    REPO              STATUS    MEMORY    UPTIME
# ggs-owner-repo-123    owner/repo        running   12GB      2h 15m
# ggs-other-lib-456     other/lib         stopped   12GB      -

# Enter sandbox (SSH)
ggs sandbox enter ggs-owner-repo-123
# → SSH into sandbox, cd to ~/work/repo

# Execute command in sandbox
ggs sandbox exec ggs-owner-repo-123 "pytest tests/"

# Cleanup sandbox
ggs sandbox cleanup ggs-owner-repo-123
# → Destroys VM, removes clone

# Cleanup all sandboxes
ggs sandbox cleanup --all
```

### Advanced Commands (Phase 2+)

```bash
# Create with specific profile
ggs sandbox create <url> --profile heavy

# Pre-warm the pool
ggs sandbox warmup --count 2

# Quarantine suspicious sandbox
ggs sandbox quarantine ggs-owner-repo-123

# Emergency kill all
ggs sandbox kill-all --emergency
```

## Resource Profiles

```yaml
# config/sandbox.yaml
profiles:
  light:
    description: "Documentation fixes, typo corrections"
    memory_mb: 8192
    vcpus: 2
    use_cases:
      - README updates
      - Docstring fixes
      - Simple config changes

  standard:
    description: "Typical code changes"
    memory_mb: 12288
    vcpus: 4
    default: true
    use_cases:
      - Bug fixes
      - Feature additions
      - Test additions

  heavy:
    description: "Build-heavy projects, Docker workloads"
    memory_mb: 16384
    vcpus: 6
    use_cases:
      - Projects with Docker
      - Large test suites
      - Compilation required
```

## Security Model

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│ Host System (64GB, 16 cores)                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ libvirt/KVM Hypervisor                                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │ Sandbox 1       │  │ Sandbox 2       │            │  │
│  │  │ ┌─────────────┐ │  │ ┌─────────────┐ │            │  │
│  │  │ │ UFW Rules   │ │  │ │ UFW Rules   │ │            │  │
│  │  │ │ └─────────┘ │ │  │ │ └─────────┘ │ │            │  │
│  │  │ │ Scoped Token│ │  │ │ Scoped Token│ │            │  │
│  │  │ └─────────────┘ │  │ └─────────────┘ │            │  │
│  │  │ Isolated Network│  │ Isolated Network│            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Token Security

**Problem**: Golden image has pre-baked auth tokens. Don't expose full access to untrusted code.

**Solution**: Scoped tokens per sandbox

```python
# manager.py
def create_sandbox(self, issue_url: str) -> Sandbox:
    owner, repo, issue_num = parse_issue_url(issue_url)

    # Generate scoped token (24h expiry, single repo)
    token = self._create_scoped_token(
        repo=f"{owner}/{repo}",
        permissions=["contents:write", "pull_requests:write"],
        expiry_hours=24
    )

    # Create VM clone
    sandbox = self._create_clone(profile="standard")

    # Inject token (not in golden image!)
    sandbox.inject_env("GITHUB_TOKEN", token)

    return sandbox
```

### Network Isolation

```yaml
# config/sandbox.yaml
network:
  mode: isolated  # libvirt isolated network

  egress_allowlist:
    - github.com
    - api.github.com
    - raw.githubusercontent.com
    - pypi.org
    - files.pythonhosted.org
    - npmjs.org
    - registry.npmjs.org

  egress_denylist:
    - "*"  # Deny all not in allowlist
```

### Incident Response

| Trigger | Action |
|---------|--------|
| Blocked egress attempt | Log + alert |
| Excessive resource usage | Throttle or kill |
| Suspicious process activity | Quarantine sandbox |
| User reports issue | `ggs sandbox quarantine <id>` |

## Implementation Phases

### Phase 1: MVP (This PR)

**Deliverables**:
- [ ] Add moltdown as git submodule
- [ ] Create `src/git_gud_samaritans/sandbox/` module
- [ ] Implement basic `ggs sandbox create|enter|list|cleanup`
- [ ] Standard profile only (12GB/4vCPU)
- [ ] Basic documentation

**Files to Create/Modify**:
```
.gitmodules                           # NEW
tools/moltdown/                       # SUBMODULE
src/git_gud_samaritans/sandbox/       # NEW
├── __init__.py
├── manager.py
└── cli.py
src/git_gud_samaritans/cli.py         # MODIFY (add sandbox group)
config/sandbox.yaml                   # NEW
tests/test_sandbox/                   # NEW
├── __init__.py
├── test_manager.py
└── test_cli.py
```

### Phase 2: Security Hardening

**Deliverables**:
- [ ] Network isolation configuration
- [ ] Scoped token generation
- [ ] Audit logging
- [ ] Quarantine command

### Phase 3: Production Features

**Deliverables**:
- [ ] Multiple profiles (light/standard/heavy)
- [ ] Warm pool management
- [ ] Auto profile detection based on repo

### Phase 4: Scale & Automation

**Deliverables**:
- [ ] Parallel contribution support
- [ ] CI self-hosted runner integration
- [ ] Auto-cleanup after PR merge

## Creative Ideas (Future)

### 1. Snapshot Checkpoints
Take VM snapshots at key points for easy rollback:
```bash
ggs sandbox checkpoint ggs-owner-repo-123 "pre-refactor"
# ... make changes ...
ggs sandbox rollback ggs-owner-repo-123 "pre-refactor"
```

### 2. Contribution Swarm
Work on multiple issues simultaneously:
```bash
ggs contribute --parallel issue1,issue2,issue3
# Creates 3 sandboxes, runs nexus-agents orchestration in each
```

### 3. Artifact Bridge
Export PRs from sandbox without SSH:
```bash
ggs sandbox export ggs-owner-repo-123 --format patch > fix.patch
ggs sandbox export ggs-owner-repo-123 --push-branch feature/fix
```

### 4. Cost-Aware Scheduling
Auto-select profile based on repo analysis:
```python
def auto_profile(repo_url: str) -> str:
    if has_dockerfile(repo_url):
        return "heavy"
    if is_documentation_only(issue):
        return "light"
    return "standard"
```

## Dependencies

- **moltdown**: v1.0+ (submodule)
- **libvirt/KVM**: Host must have virtualization enabled
- **Golden image**: Pre-created `ubuntu2404-agent` VM with dev-ready snapshot

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| moltdown breaking changes | Low | Medium | Pin submodule to specific commit |
| Resource exhaustion | Medium | High | Strict limits, warm pool max 2 |
| Token leakage | Low | High | Scoped tokens, 24h expiry, audit log |
| Network exfiltration | Low | High | Allowlist-only egress |

## Success Metrics

- [ ] Sandbox creation time < 30s (with warm pool)
- [ ] Zero host compromises from untrusted code
- [ ] Support 2-3 parallel contributions
- [ ] Clean PR submissions (no env leakage)

---

*Plan created: 2026-02-02*
*Approved via nexus-agents consensus voting*

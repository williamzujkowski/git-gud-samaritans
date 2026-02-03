# git-gud-samaritans

```
       _ _                       _                                _ _
  __ _(_) |_       __ _ _   _  __| |      ___  __ _ _ __ ___   __ _ _ __(_) |_ __ _ _ __  ___
 / _` | | __|____ / _` | | | |/ _` |_____/ __|/ _` | '_ ` _ \ / _` | '__| | __/ _` | '_ \/ __|
| (_| | | ||_____| (_| | |_| | (_| |_____\__ \ (_| | | | | | | (_| | |  | | || (_| | | | \__ \
 \__, |_|\__|     \__, |\__,_|\__,_|     |___/\__,_|_| |_| |_|\__,_|_|  |_|\__\__,_|_| |_|___/
 |___/            |___/
```

```bash
$ git gud --help-others
```

> *"With great elevated privileges comes great responsibility to make pipelines green."*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Pipelines Healed](https://img.shields.io/badge/pipelines-healed-00ff00.svg)](#metrics)

---

## 🎮 WTF is this?

**git-gud-samaritans** is an AI-powered open source contribution engine that identifies struggling repositories and helps fix them using [nexus-agents](https://github.com/williamzujkowski/nexus-agents) orchestration.

We find repos that need help. We send in the swarm. We make pipelines green.

### The Name

The name is a mass of nerdy references:

- **"git gud"** — The immortal gamer taunt, repurposed for good
- **"Good Samaritans"** — Helping strangers in need (but for code)
- **Inspired by `sudo make it green`** — Because sometimes you just need elevated privileges to fix things
- **`sed 's/red/green/g`** — What we're literally doing to CI status badges
- **`exit 0`** — The only acceptable return code

---

## 🎯 Mission

1. **Discover** repositories that welcome contributions (good first issues, help wanted, stale PRs)
2. **Triage** which issues are good candidates for AI-assisted fixes
3. **Contribute** quality PRs using nexus-agents swarm orchestration
4. **Learn** and improve nexus-agents based on real-world contribution patterns
5. **Repeat** until all pipelines are green (they never will be, but we dream)

---

## 🏗️ How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           git-gud-samaritans                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   DISCOVER   │───▶│    TRIAGE    │───▶│  CONTRIBUTE  │                  │
│  │              │    │              │    │              │                  │
│  │ • GitHub API │    │ • Complexity │    │ • Clone repo │                  │
│  │ • Issue scan │    │ • Fit score  │    │ • Run agents │                  │
│  │ • PR review  │    │ • Priority   │    │ • Submit PR  │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                   │                          │
│         └───────────────────┴───────────────────┘                          │
│                             │                                              │
│                    ┌────────▼────────┐                                     │
│                    │  nexus-agents   │                                     │
│                    │    (via MCP)    │                                     │
│                    │                 │                                     │
│                    │ • Research loop │                                     │
│                    │ • Code analysis │                                     │
│                    │ • Fix generation│                                     │
│                    │ • Test & verify │                                     │
│                    └─────────────────┘                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Discovery

We scan for repos that explicitly welcome help:

- `good first issue` labels
- `help wanted` labels
- `hacktoberfest` participation
- Stale PRs that need review/updates
- Failing CI that's been red for too long
- CONTRIBUTING.md files that actually encourage contributions

### Phase 2: Triage

Not every issue is a good fit for AI-assisted contribution. We score based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Clarity | High | Is the issue well-defined? |
| Scope | High | Is it appropriately sized? |
| Test Coverage | Medium | Can we verify our fix? |
| Maintainer Activity | Medium | Will our PR get reviewed? |
| Complexity | Variable | Match to agent capabilities |

### Phase 3: Contribute

Using nexus-agents via MCP, we:

1. **Research** — Understand the codebase, issue context, related PRs
2. **Plan** — Generate an approach using iterative agent loops
3. **Implement** — Write the fix with proper tests
4. **Verify** — Run existing tests, linting, type checking
5. **Submit** — Create a well-documented PR with context

---

## 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/williamzujkowski/git-gud-samaritans.git
cd git-gud-samaritans

# Install dependencies
pip install -r requirements.txt

# Configure your tokens
cp .env.example .env
# Edit .env with your GitHub token and other credentials
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
NEXUS_AGENTS_PATH=/path/to/nexus-agents
LOG_LEVEL=INFO

# Optional: Filtering
TARGET_LANGUAGES=python,javascript,typescript,rust
MIN_STARS=10
MAX_OPEN_ISSUES=500
```

### MCP Configuration

The project enforces nexus-agents usage via MCP (Model Context Protocol):

```json
{
  "mcpServers": {
    "nexus-agents": {
      "command": "python",
      "args": ["-m", "nexus_agents.mcp_server"],
      "env": {
        "NEXUS_CONFIG": "./config/nexus-config.yaml"
      }
    },
    "git-gud-samaritans": {
      "command": "python",
      "args": ["-m", "git_gud_samaritans.mcp_server"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## 📁 Project Structure

```
git-gud-samaritans/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── pyproject.toml
├── requirements.txt
├── .env.example
│
├── config/
│   ├── mcp-config.json          # MCP server configuration
│   ├── nexus-config.yaml        # nexus-agents configuration
│   ├── discovery-rules.yaml     # Repo discovery criteria
│   └── triage-scoring.yaml      # Issue scoring weights
│
├── src/
│   └── git_gud_samaritans/
│       ├── __init__.py
│       ├── cli.py               # Command-line interface
│       ├── mcp_server.py        # MCP server implementation
│       │
│       ├── discovery/
│       │   ├── __init__.py
│       │   ├── github_scanner.py    # GitHub API integration
│       │   ├── issue_finder.py      # Issue discovery logic
│       │   └── pr_analyzer.py       # Stale PR detection
│       │
│       ├── triage/
│       │   ├── __init__.py
│       │   ├── scorer.py            # Issue scoring engine
│       │   ├── complexity.py        # Complexity estimation
│       │   └── fit_analyzer.py      # Agent fit analysis
│       │
│       ├── contribute/
│       │   ├── __init__.py
│       │   ├── orchestrator.py      # Contribution workflow
│       │   ├── pr_generator.py      # PR creation & formatting
│       │   └── verification.py      # Pre-submit checks
│       │
│       └── utils/
│           ├── __init__.py
│           ├── github_client.py     # GitHub API wrapper
│           ├── logging.py           # Structured logging
│           └── metrics.py           # Contribution tracking
│
├── prompts/
│   ├── discovery/
│   │   └── find_opportunities.md
│   ├── triage/
│   │   └── score_issue.md
│   └── contribute/
│       ├── research_codebase.md
│       ├── plan_fix.md
│       ├── implement_fix.md
│       └── write_pr_description.md
│
├── tests/
│   ├── __init__.py
│   ├── test_discovery.py
│   ├── test_triage.py
│   └── test_contribute.py
│
└── docs/
    ├── architecture.md
    ├── mcp-integration.md
    └── contribution-workflow.md
```

---

## 🚀 Usage

### CLI Commands

```bash
# Discover repos that need help
ggs discover --language python --min-stars 50

# Triage a specific issue
ggs triage https://github.com/owner/repo/issues/123

# Run full contribution workflow on an issue
ggs contribute https://github.com/owner/repo/issues/123

# Scan and auto-contribute (with confirmation)
ggs auto --language python --max-contributions 5

# View contribution metrics
ggs metrics --period 30d
```

### As a Library

```python
from git_gud_samaritans import Discoverer, Triager, Contributor

# Find opportunities
discoverer = Discoverer(languages=["python", "rust"])
opportunities = discoverer.find_issues(
    labels=["good first issue", "help wanted"],
    min_stars=50,
    max_complexity="medium"
)

# Score and prioritize
triager = Triager()
scored = triager.score_all(opportunities)
best_fit = scored[0]  # Highest scoring opportunity

# Contribute!
contributor = Contributor(use_nexus_agents=True)
result = contributor.submit_fix(best_fit)
print(f"PR submitted: {result.pr_url}")
```

### MCP Tools

When running as an MCP server, the following tools are exposed:

| Tool | Description |
|------|-------------|
| `discover_opportunities` | Find repos/issues that need help |
| `triage_issue` | Score an issue for contribution fit |
| `analyze_codebase` | Understand a repo's structure and conventions |
| `plan_contribution` | Generate a contribution plan |
| `submit_contribution` | Execute the full contribution workflow |
| `get_metrics` | Retrieve contribution statistics |

---

## 🎯 Contribution Criteria

We look for issues that are:

### ✅ Good Candidates

- Well-defined with clear acceptance criteria
- Appropriately scoped (not too large, not trivial)
- In actively maintained repos
- Have existing test infrastructure
- Maintainers are responsive to PRs

### ❌ Not Good Candidates

- Vague or poorly defined
- Require deep domain expertise
- In abandoned repos (no commits in 6+ months)
- Controversial or heavily debated
- Security-sensitive without clear guidance

---

## 📊 Metrics

We track our impact (and failures, because learning):

```
┌────────────────────────────────────────┐
│         git-gud-samaritans             │
│            Contribution Stats          │
├────────────────────────────────────────┤
│ PRs Submitted      │ 142               │
│ PRs Merged         │ 98                │
│ PRs Closed         │ 31                │
│ PRs Pending        │ 13                │
│ Merge Rate         │ 69%               │
│ Avg Time to Merge  │ 4.2 days          │
│ Repos Helped       │ 67                │
│ Lines Changed      │ +12,847 / -8,234  │
└────────────────────────────────────────┘
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

The irony of a project about contributing needing contributors is not lost on us.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/git-gud-samaritans.git

# Create a branch
git checkout -b feature/your-feature

# Make changes, then
git add .
git commit -m "feat: description of your changes"
git push origin feature/your-feature

# Open a PR!
```

---

## 🗺️ Roadmap

- [ ] **v0.1** — Basic discovery and triage
- [ ] **v0.2** — nexus-agents MCP integration
- [ ] **v0.3** — Automated contribution workflow
- [ ] **v0.4** — Multi-language support expansion
- [ ] **v0.5** — Contribution quality feedback loop
- [ ] **v1.0** — Production-ready release

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [nexus-agents](https://github.com/williamzujkowski/nexus-agents) — The orchestration engine that makes this possible
- Every maintainer who labels issues `good first issue` — You're the real heroes
- The `git gud` meme — For the name that writes itself

---

<p align="center">
  <i>Making open source a little greener, one PR at a time.</i>
</p>

<p align="center">
  <code>return 0;</code>
</p>

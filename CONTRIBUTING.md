# Contributing to git-gud-samaritans

First off, thanks for considering contributing to a project about contributing. The recursion is beautiful.

## 🎮 Code of Conduct

Be excellent to each other. That's it. That's the code of conduct.

(But seriously, be respectful, inclusive, and remember that everyone's here to learn and help.)

---

## 🚀 Quick Start

```bash
# 1. Fork the repo on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/git-gud-samaritans.git
cd git-gud-samaritans

# 3. Add upstream remote
git remote add upstream https://github.com/williamzujkowski/git-gud-samaritans.git

# 4. Create a virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Create a branch for your work
git checkout -b feature/your-awesome-feature

# 7. Make your changes

# 8. Run tests
pytest

# 9. Commit and push
git add .
git commit -m "feat: add awesome feature"
git push origin feature/your-awesome-feature

# 10. Open a PR!
```

---

## 📋 Types of Contributions

### 🐛 Bug Reports

Found a bug? Open an issue with:

- Clear title describing the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant logs or screenshots

### ✨ Feature Requests

Have an idea? We'd love to hear it! Open an issue with:

- Clear description of the feature
- Use case / problem it solves
- Any implementation ideas you have

### 🔧 Code Contributions

We welcome PRs for:

- Bug fixes
- New features (please open an issue first to discuss)
- Documentation improvements
- Test coverage improvements
- Performance optimizations

### 📚 Documentation

Help us improve our docs:

- Fix typos or unclear explanations
- Add examples
- Improve architecture documentation
- Write tutorials

---

## 🏗️ Development Guidelines

### Code Style

We use:

- **Black** for Python formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `style:` — Formatting, no code change
- `refactor:` — Code change that neither fixes a bug nor adds a feature
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks

Examples:

```
feat(discovery): add support for GitLab repos
fix(triage): handle rate limiting gracefully
docs: update MCP configuration examples
test(contribute): add integration tests for PR submission
```

### Testing

- Write tests for new features
- Maintain or improve test coverage
- Use pytest fixtures for common setup
- Mock external APIs (GitHub, etc.)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/git_gud_samaritans

# Run specific test file
pytest tests/test_discovery.py

# Run tests matching a pattern
pytest -k "test_score"
```

### Documentation

- Update docstrings for new/modified functions
- Update README if adding user-facing features
- Add/update docs in `docs/` for architectural changes

---

## 🔄 Pull Request Process

### Before Opening a PR

1. **Check for existing PRs** — Someone might already be working on it
2. **Open an issue first** (for significant changes) — Let's discuss the approach
3. **Write tests** — New features need tests
4. **Update documentation** — If applicable
5. **Run all checks** — Make sure CI will pass

### PR Guidelines

- **Clear title** — Describe what the PR does
- **Link related issues** — Use `Fixes #123` or `Relates to #456`
- **Describe your changes** — What and why
- **Keep it focused** — One feature/fix per PR
- **Be responsive** — Address review feedback promptly

### PR Template

```markdown
## Description

Brief description of the changes.

## Related Issues

Fixes #(issue number)

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (describe)

## Testing

- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
```

---

## 🏛️ Architecture Decisions

For significant architectural changes, we use lightweight ADRs (Architecture Decision Records). Create a new file in `docs/adr/` following this template:

```markdown
# ADR-XXX: Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

---

## 🤖 Using nexus-agents for Contributions

Meta alert: You can use nexus-agents (via this project's MCP integration) to contribute to this project!

```bash
# Discover issues in this repo that need help
ggs discover --repo williamzujkowski/git-gud-samaritans

# Let the agents help you understand the codebase
ggs analyze --repo williamzujkowski/git-gud-samaritans
```

---

## 📫 Getting Help

- **Questions?** Open a [Discussion](https://github.com/williamzujkowski/git-gud-samaritans/discussions)
- **Found a bug?** Open an [Issue](https://github.com/williamzujkowski/git-gud-samaritans/issues)
- **Security issue?** Email directly (don't open a public issue)

---

## 🙏 Recognition

All contributors will be added to our [Contributors list](README.md#contributors). We appreciate every contribution, no matter how small!

---

<p align="center">
  <i>git gud && help-others</i>
</p>

"""
Tests for the CLI module.
"""

import pytest
from click.testing import CliRunner

from git_gud_samaritans.cli import main


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for the main CLI interface."""

    def test_main_help(self, runner: CliRunner) -> None:
        """CLI should show help text."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "git-gud-samaritans" in result.output

    def test_main_version(self, runner: CliRunner) -> None:
        """CLI should show version."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_discover_help(self, runner: CliRunner) -> None:
        """Discover command should show help."""
        result = runner.invoke(main, ["discover", "--help"])
        assert result.exit_code == 0
        assert "Discover repositories" in result.output

    def test_triage_help(self, runner: CliRunner) -> None:
        """Triage command should show help."""
        result = runner.invoke(main, ["triage", "--help"])
        assert result.exit_code == 0
        assert "Score an issue" in result.output

    def test_contribute_help(self, runner: CliRunner) -> None:
        """Contribute command should show help."""
        result = runner.invoke(main, ["contribute", "--help"])
        assert result.exit_code == 0
        assert "contribution workflow" in result.output

    def test_auto_help(self, runner: CliRunner) -> None:
        """Auto command should show help."""
        result = runner.invoke(main, ["auto", "--help"])
        assert result.exit_code == 0
        assert "Automatically" in result.output

    def test_metrics_help(self, runner: CliRunner) -> None:
        """Metrics command should show help."""
        result = runner.invoke(main, ["metrics", "--help"])
        assert result.exit_code == 0
        assert "statistics" in result.output

    def test_analyze_help(self, runner: CliRunner) -> None:
        """Analyze command should show help."""
        result = runner.invoke(main, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze a repository" in result.output

    def test_verbose_flag(self, runner: CliRunner) -> None:
        """Verbose flag should work."""
        result = runner.invoke(main, ["-v", "discover", "--help"])
        assert result.exit_code == 0


class TestDiscoverCommand:
    """Tests for the discover command."""

    def test_discover_default(self, runner: CliRunner) -> None:
        """Discover with defaults should work."""
        result = runner.invoke(main, ["discover"])
        assert result.exit_code == 0
        assert "Discovering" in result.output

    def test_discover_with_language(self, runner: CliRunner) -> None:
        """Discover with language filter should work."""
        result = runner.invoke(main, ["discover", "--language", "python"])
        assert result.exit_code == 0

    def test_discover_json_output(self, runner: CliRunner) -> None:
        """Discover with JSON output should work."""
        result = runner.invoke(main, ["discover", "--output", "json"])
        assert result.exit_code == 0


class TestTriageCommand:
    """Tests for the triage command."""

    def test_triage_requires_url(self, runner: CliRunner) -> None:
        """Triage should require an issue URL."""
        result = runner.invoke(main, ["triage"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_triage_with_url(self, runner: CliRunner) -> None:
        """Triage with URL should work."""
        result = runner.invoke(
            main, ["triage", "https://github.com/owner/repo/issues/123"]
        )
        assert result.exit_code == 0
        assert "Triaging" in result.output


class TestContributeCommand:
    """Tests for the contribute command."""

    def test_contribute_requires_url(self, runner: CliRunner) -> None:
        """Contribute should require an issue URL."""
        result = runner.invoke(main, ["contribute"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_contribute_dry_run(self, runner: CliRunner) -> None:
        """Contribute with dry-run should work."""
        result = runner.invoke(
            main,
            ["contribute", "https://github.com/owner/repo/issues/123", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "dry-run" in result.output.lower()

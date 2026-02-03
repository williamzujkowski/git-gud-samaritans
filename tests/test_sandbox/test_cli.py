"""Tests for sandbox CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from git_gud_samaritans.cli import main
from git_gud_samaritans.sandbox.manager import (
    Sandbox,
    SandboxManager,
    SandboxProfile,
    SandboxStatus,
)


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_manager() -> MagicMock:
    """Create mock SandboxManager."""
    manager = MagicMock(spec=SandboxManager)
    manager.moltdown_path = Path("/mock/moltdown")
    manager.base_vm = "ubuntu2404-agent"
    manager.HOST_RESERVED_MB = 16384
    manager.MAX_CONCURRENT_SANDBOXES = 3
    return manager


class TestSandboxCLI:
    """Tests for sandbox CLI commands."""

    def test_sandbox_help(self, runner: CliRunner) -> None:
        """Sandbox help should display."""
        result = runner.invoke(main, ["sandbox", "--help"])

        assert result.exit_code == 0
        assert "Manage sandbox VMs" in result.output

    @patch("git_gud_samaritans.sandbox.cli.get_manager")
    def test_sandbox_create(
        self,
        mock_get_manager: MagicMock,
        runner: CliRunner,
        mock_manager: MagicMock,
    ) -> None:
        """Create command should create sandbox."""
        mock_get_manager.return_value = mock_manager

        sandbox = Sandbox(
            id="ggs-owner-repo-123",
            issue_url="https://github.com/owner/repo/issues/123",
            owner="owner",
            repo="repo",
            issue_num=123,
            status=SandboxStatus.RUNNING,
            profile=SandboxProfile.STANDARD,
            ip_address="192.168.122.100",
        )
        mock_manager.create.return_value = sandbox

        result = runner.invoke(
            main,
            ["sandbox", "create", "https://github.com/owner/repo/issues/123"],
        )

        assert result.exit_code == 0
        assert "Sandbox created successfully" in result.output
        assert "ggs-owner-repo-123" in result.output
        mock_manager.create.assert_called_once()

    @patch("git_gud_samaritans.sandbox.cli.get_manager")
    def test_sandbox_list_empty(
        self,
        mock_get_manager: MagicMock,
        runner: CliRunner,
        mock_manager: MagicMock,
    ) -> None:
        """List command should handle empty list."""
        mock_get_manager.return_value = mock_manager
        mock_manager.list_sandboxes.return_value = []

        result = runner.invoke(main, ["sandbox", "list"])

        assert result.exit_code == 0
        assert "No sandboxes found" in result.output

    @patch("git_gud_samaritans.sandbox.cli.get_manager")
    def test_sandbox_list_with_sandboxes(
        self,
        mock_get_manager: MagicMock,
        runner: CliRunner,
        mock_manager: MagicMock,
    ) -> None:
        """List command should display sandboxes."""
        mock_get_manager.return_value = mock_manager

        sandboxes = [
            Sandbox(
                id="ggs-owner-repo-1",
                issue_url="https://github.com/owner/repo/issues/1",
                owner="owner",
                repo="repo",
                issue_num=1,
                status=SandboxStatus.RUNNING,
                profile=SandboxProfile.STANDARD,
                ip_address="192.168.122.100",
            ),
        ]
        mock_manager.list_sandboxes.return_value = sandboxes

        result = runner.invoke(main, ["sandbox", "list"])

        assert result.exit_code == 0
        # Rich truncates long IDs, so check for partial match
        assert "ggs-owner-repo" in result.output
        assert "owner/repo" in result.output
        assert "running" in result.output

    @patch("git_gud_samaritans.sandbox.cli.get_manager")
    def test_sandbox_cleanup(
        self,
        mock_get_manager: MagicMock,
        runner: CliRunner,
        mock_manager: MagicMock,
    ) -> None:
        """Cleanup command should destroy sandbox."""
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(
            main,
            ["sandbox", "cleanup", "ggs-owner-repo-123", "--yes"],
        )

        assert result.exit_code == 0
        assert "destroyed" in result.output.lower()
        mock_manager.cleanup.assert_called_once_with("ggs-owner-repo-123", force=False)

    @patch("git_gud_samaritans.sandbox.cli.get_manager")
    def test_sandbox_status(
        self,
        mock_get_manager: MagicMock,
        runner: CliRunner,
        mock_manager: MagicMock,
    ) -> None:
        """Status command should show resource info."""
        mock_get_manager.return_value = mock_manager
        mock_manager.list_sandboxes.return_value = []

        result = runner.invoke(main, ["sandbox", "status"])

        assert result.exit_code == 0
        assert "Host Resources" in result.output

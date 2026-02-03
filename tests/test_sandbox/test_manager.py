"""Tests for SandboxManager."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_gud_samaritans.sandbox.manager import (
    ResourceError,
    Sandbox,
    SandboxManager,
    SandboxProfile,
    SandboxStatus,
)


class TestSandboxProfile:
    """Tests for SandboxProfile."""

    def test_predefined_profiles_exist(self) -> None:
        """Predefined profiles should be available."""
        assert SandboxProfile.LIGHT.memory_mb == 8192
        assert SandboxProfile.STANDARD.memory_mb == 12288
        assert SandboxProfile.HEAVY.memory_mb == 16384

    def test_profile_vcpus(self) -> None:
        """Profiles should have correct vCPU counts."""
        assert SandboxProfile.LIGHT.vcpus == 2
        assert SandboxProfile.STANDARD.vcpus == 4
        assert SandboxProfile.HEAVY.vcpus == 6


class TestSandbox:
    """Tests for Sandbox dataclass."""

    def test_sandbox_creation(self) -> None:
        """Sandbox should be created with correct attributes."""
        sandbox = Sandbox(
            id="ggs-owner-repo-123",
            issue_url="https://github.com/owner/repo/issues/123",
            owner="owner",
            repo="repo",
            issue_num=123,
            status=SandboxStatus.RUNNING,
            profile=SandboxProfile.STANDARD,
        )

        assert sandbox.id == "ggs-owner-repo-123"
        assert sandbox.owner == "owner"
        assert sandbox.repo == "repo"
        assert sandbox.issue_num == 123
        assert sandbox.vm_name == "ggs-owner-repo-123"

    def test_sandbox_to_dict(self) -> None:
        """Sandbox should serialize to dictionary."""
        sandbox = Sandbox(
            id="ggs-test-repo-1",
            issue_url="https://github.com/test/repo/issues/1",
            owner="test",
            repo="repo",
            issue_num=1,
            status=SandboxStatus.RUNNING,
            profile=SandboxProfile.LIGHT,
        )

        result = sandbox.to_dict()

        assert result["id"] == "ggs-test-repo-1"
        assert result["status"] == "running"
        assert result["profile"] == "light"


class TestSandboxManager:
    """Tests for SandboxManager."""

    @pytest.fixture
    def mock_moltdown_path(self, tmp_path: Path) -> Path:
        """Create mock moltdown directory."""
        moltdown = tmp_path / "moltdown"
        moltdown.mkdir()

        # Create mock scripts
        for script in ["clone_manager.sh", "agent.sh"]:
            (moltdown / script).write_text("#!/bin/bash\nexit 0")
            (moltdown / script).chmod(0o755)

        return moltdown

    @pytest.fixture
    def manager(self, mock_moltdown_path: Path) -> SandboxManager:
        """Create SandboxManager with mocked moltdown."""
        return SandboxManager(moltdown_path=mock_moltdown_path)

    def test_parse_issue_url_valid(self, manager: SandboxManager) -> None:
        """Valid issue URLs should be parsed correctly."""
        owner, repo, num = manager._parse_issue_url(
            "https://github.com/owner/repo/issues/123"
        )

        assert owner == "owner"
        assert repo == "repo"
        assert num == 123

    def test_parse_issue_url_invalid(self, manager: SandboxManager) -> None:
        """Invalid issue URLs should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid issue URL"):
            manager._parse_issue_url("https://gitlab.com/owner/repo/issues/123")

        with pytest.raises(ValueError, match="Invalid issue URL"):
            manager._parse_issue_url("not-a-url")

    def test_generate_sandbox_id(self, manager: SandboxManager) -> None:
        """Sandbox IDs should be generated consistently."""
        sandbox_id = manager._generate_sandbox_id("owner", "repo", 123)
        assert sandbox_id == "ggs-owner-repo-123"

    def test_check_resources_under_limit(self, manager: SandboxManager) -> None:
        """Should pass when resources are available."""
        # No sandboxes running, should not raise
        manager._check_resources(SandboxProfile.STANDARD)

    def test_check_resources_max_sandboxes(self, manager: SandboxManager) -> None:
        """Should fail when max sandboxes reached."""
        # Add 3 running sandboxes
        for i in range(3):
            sandbox = Sandbox(
                id=f"ggs-test-repo-{i}",
                issue_url=f"https://github.com/test/repo/issues/{i}",
                owner="test",
                repo="repo",
                issue_num=i,
                status=SandboxStatus.RUNNING,
                profile=SandboxProfile.STANDARD,
            )
            manager._sandboxes[sandbox.id] = sandbox

        with pytest.raises(ResourceError, match="Maximum concurrent sandboxes"):
            manager._check_resources(SandboxProfile.STANDARD)

    @patch("subprocess.run")
    def test_create_sandbox(
        self,
        mock_run: MagicMock,
        manager: SandboxManager,
    ) -> None:
        """Creating a sandbox should call moltdown scripts."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        sandbox = manager.create("https://github.com/owner/repo/issues/123")

        assert sandbox.id == "ggs-owner-repo-123"
        assert sandbox.owner == "owner"
        assert sandbox.repo == "repo"
        assert sandbox.issue_num == 123
        assert sandbox.status == SandboxStatus.RUNNING

    def test_list_sandboxes_empty(self, manager: SandboxManager) -> None:
        """Empty manager should return empty list."""
        sandboxes = manager.list_sandboxes()
        assert sandboxes == []

    def test_list_sandboxes_with_filter(self, manager: SandboxManager) -> None:
        """List should respect status filter."""
        running = Sandbox(
            id="ggs-test-repo-1",
            issue_url="https://github.com/test/repo/issues/1",
            owner="test",
            repo="repo",
            issue_num=1,
            status=SandboxStatus.RUNNING,
            profile=SandboxProfile.STANDARD,
        )
        stopped = Sandbox(
            id="ggs-test-repo-2",
            issue_url="https://github.com/test/repo/issues/2",
            owner="test",
            repo="repo",
            issue_num=2,
            status=SandboxStatus.STOPPED,
            profile=SandboxProfile.STANDARD,
        )

        manager._sandboxes["ggs-test-repo-1"] = running
        manager._sandboxes["ggs-test-repo-2"] = stopped

        all_sandboxes = manager.list_sandboxes()
        assert len(all_sandboxes) == 2

        running_only = manager.list_sandboxes(status_filter=SandboxStatus.RUNNING)
        assert len(running_only) == 1
        assert running_only[0].id == "ggs-test-repo-1"

    def test_get_sandbox_exists(self, manager: SandboxManager) -> None:
        """Get should return existing sandbox."""
        sandbox = Sandbox(
            id="ggs-test-repo-1",
            issue_url="https://github.com/test/repo/issues/1",
            owner="test",
            repo="repo",
            issue_num=1,
            status=SandboxStatus.RUNNING,
            profile=SandboxProfile.STANDARD,
        )
        manager._sandboxes["ggs-test-repo-1"] = sandbox

        result = manager.get("ggs-test-repo-1")
        assert result is not None
        assert result.id == "ggs-test-repo-1"

    def test_get_sandbox_not_found(self, manager: SandboxManager) -> None:
        """Get should return None for missing sandbox."""
        result = manager.get("nonexistent")
        assert result is None


class TestSandboxManagerNotFound:
    """Tests for moltdown not found scenarios."""

    def test_moltdown_not_found_raises(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError if moltdown not found."""
        # Point to non-existent path
        with (
            patch(
                "git_gud_samaritans.sandbox.manager.DEFAULT_MOLTDOWN_PATH",
                tmp_path / "nonexistent",
            ),
            patch(
                "git_gud_samaritans.sandbox.manager.FALLBACK_MOLTDOWN_PATH",
                tmp_path / "also-nonexistent",
            ),
            pytest.raises(FileNotFoundError, match="moltdown not found"),
        ):
            SandboxManager()

"""
Tests for the contribution orchestrator module.
"""

import pytest

from git_gud_samaritans.contribute.orchestrator import (
    ContributionOrchestrator,
    ContributionPlan,
    ContributionResult,
)


class TestContributionResult:
    """Tests for the ContributionResult dataclass."""

    def test_create_success_result(self) -> None:
        """ContributionResult should be creatable for success."""
        result = ContributionResult(
            success=True,
            issue_url="https://github.com/owner/repo/issues/123",
            pr_url="https://github.com/owner/repo/pull/456",
            branch_name="fix-123",
        )
        assert result.success is True
        assert result.pr_url is not None

    def test_create_failure_result(self) -> None:
        """ContributionResult should be creatable for failure."""
        result = ContributionResult(
            success=False,
            issue_url="https://github.com/owner/repo/issues/123",
            error="Something went wrong",
        )
        assert result.success is False
        assert result.error is not None

    def test_to_dict(self) -> None:
        """ContributionResult should convert to dict."""
        result = ContributionResult(
            success=True,
            issue_url="https://example.com",
            pr_url="https://example.com/pr",
            branch_name="fix-123",
            files_changed=["file1.py"],
            lines_added=10,
            lines_removed=5,
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["files_changed"] == ["file1.py"]
        assert data["lines_added"] == 10


class TestContributionPlan:
    """Tests for the ContributionPlan dataclass."""

    def test_create_plan(self) -> None:
        """ContributionPlan should be creatable."""
        plan = ContributionPlan(
            issue_url="https://github.com/owner/repo/issues/123",
            repo="owner/repo",
            issue_number=123,
            approach="Fix the bug",
            files_to_modify=["file.py"],
            files_to_create=[],
            tests_to_add=["test_file.py"],
            estimated_effort="Medium",
            risks=[],
        )
        assert plan.repo == "owner/repo"
        assert plan.issue_number == 123

    def test_to_dict(self) -> None:
        """ContributionPlan should convert to dict."""
        plan = ContributionPlan(
            issue_url="https://example.com",
            repo="owner/repo",
            issue_number=123,
            approach="Fix it",
            files_to_modify=[],
            files_to_create=[],
            tests_to_add=[],
            estimated_effort="Low",
            risks=["Risk 1"],
        )
        data = plan.to_dict()
        assert data["repo"] == "owner/repo"
        assert data["risks"] == ["Risk 1"]


class TestContributionOrchestrator:
    """Tests for the ContributionOrchestrator class."""

    @pytest.fixture
    def orchestrator(self) -> ContributionOrchestrator:
        """Provide an orchestrator instance."""
        return ContributionOrchestrator(
            use_nexus_agents=False,
            github_token="test_token",
        )

    def test_orchestrator_init(self, orchestrator: ContributionOrchestrator) -> None:
        """Orchestrator should initialize properly."""
        assert orchestrator.use_nexus_agents is False
        assert orchestrator.github_token == "test_token"

    def test_parse_issue_url_valid(
        self, orchestrator: ContributionOrchestrator
    ) -> None:
        """Orchestrator should parse valid issue URLs."""
        repo, number = orchestrator._parse_issue_url(
            "https://github.com/owner/repo/issues/123"
        )
        assert repo == "owner/repo"
        assert number == 123

    def test_parse_issue_url_invalid(
        self, orchestrator: ContributionOrchestrator
    ) -> None:
        """Orchestrator should reject invalid URLs."""
        with pytest.raises(ValueError, match="Invalid GitHub issue URL"):
            orchestrator._parse_issue_url("https://example.com/not-github")

    def test_parse_issue_url_not_issue(
        self, orchestrator: ContributionOrchestrator
    ) -> None:
        """Orchestrator should reject non-issue URLs."""
        with pytest.raises(ValueError, match="Invalid GitHub issue URL"):
            orchestrator._parse_issue_url("https://github.com/owner/repo/pull/123")

    def test_plan_returns_dict(self, orchestrator: ContributionOrchestrator) -> None:
        """plan() should return a dictionary."""
        result = orchestrator.plan("https://github.com/owner/repo/issues/123")
        assert isinstance(result, dict)
        assert result["repo"] == "owner/repo"
        assert result["issue_number"] == 123

    def test_contribute_dry_run(self, orchestrator: ContributionOrchestrator) -> None:
        """contribute() dry run should not submit PR."""
        result = orchestrator.contribute(
            issue_url="https://github.com/owner/repo/issues/123",
            dry_run=True,
        )
        assert isinstance(result, ContributionResult)
        assert result.dry_run is True
        assert result.pr_url is None

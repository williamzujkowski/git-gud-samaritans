"""
Tests for the PR generator module.
"""

import pytest

from git_gud_samaritans.contribute.pr_generator import PRDetails, PRGenerator


class TestPRDetails:
    """Tests for the PRDetails dataclass."""

    def test_create_pr_details(self) -> None:
        """PRDetails should be creatable."""
        details = PRDetails(
            title="Fix: Bug in authentication",
            body="This PR fixes the bug.",
            branch="fix-123",
        )
        assert details.title == "Fix: Bug in authentication"
        assert details.base == "main"

    def test_create_with_custom_base(self) -> None:
        """PRDetails should accept custom base branch."""
        details = PRDetails(
            title="Fix",
            body="Body",
            branch="fix-123",
            base="develop",
        )
        assert details.base == "develop"

    def test_to_dict(self) -> None:
        """PRDetails should convert to dict."""
        details = PRDetails(
            title="Fix",
            body="Body",
            branch="fix-123",
            labels=["bug"],
        )
        data = details.to_dict()
        assert data["title"] == "Fix"
        assert data["labels"] == ["bug"]


class TestPRGenerator:
    """Tests for the PRGenerator class."""

    @pytest.fixture
    def generator(self) -> PRGenerator:
        """Provide a PRGenerator instance."""
        return PRGenerator(github_token="test_token")

    def test_generator_init(self, generator: PRGenerator) -> None:
        """PRGenerator should initialize properly."""
        assert generator.github_token == "test_token"

    def test_generate_pr_details(self, generator: PRGenerator) -> None:
        """PRGenerator should generate PR details."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="Fix bug in login",
            issue_body="The login doesn't work properly.",
            changes=["Fixed authentication logic"],
            branch_name="fix-123",
        )
        assert isinstance(result, PRDetails)
        assert result.branch == "fix-123"
        assert len(result.title) > 0
        assert len(result.body) > 0

    def test_generate_title_cleans_prefix(self, generator: PRGenerator) -> None:
        """PRGenerator should clean common prefixes from titles."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="[Bug] Login fails",
            issue_body="Description",
            changes=[],
            branch_name="fix-123",
        )
        # Title should not start with [Bug]
        assert not result.title.startswith("[Bug]")

    def test_generate_title_adds_verb(self, generator: PRGenerator) -> None:
        """PRGenerator should add verb prefix if missing."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="Missing feature",
            issue_body="Description",
            changes=[],
            branch_name="fix-123",
        )
        # Title should start with a verb
        assert any(
            result.title.startswith(v)
            for v in ["Fix", "Add", "Update", "Remove", "Improve"]
        )

    def test_generate_body_includes_issue_number(self, generator: PRGenerator) -> None:
        """PRGenerator should include issue number in body."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="Fix bug",
            issue_body="Description",
            changes=[],
            branch_name="fix-123",
        )
        assert "#123" in result.body

    def test_generate_body_includes_changes(self, generator: PRGenerator) -> None:
        """PRGenerator should include changes in body."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="Fix bug",
            issue_body="Description",
            changes=["Updated auth.py", "Added tests"],
            branch_name="fix-123",
        )
        assert "Updated auth.py" in result.body
        assert "Added tests" in result.body

    def test_generate_with_testing_notes(self, generator: PRGenerator) -> None:
        """PRGenerator should include testing notes."""
        result = generator.generate(
            issue_url="https://github.com/owner/repo/issues/123",
            issue_title="Fix bug",
            issue_body="Description",
            changes=[],
            branch_name="fix-123",
            testing_notes="Tested manually with the demo app",
        )
        assert "Tested manually" in result.body

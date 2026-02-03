"""
Contribute module for git-gud-samaritans.

Handles the actual contribution workflow using nexus-agents.
"""

from .orchestrator import ContributionOrchestrator, ContributionResult
from .pr_generator import PRGenerator
from .verification import Verifier


class Contributor:
    """
    Main contribution interface for submitting fixes.

    Example:
        contributor = Contributor(use_nexus_agents=True)
        result = contributor.submit_fix(
            issue_url="https://github.com/owner/repo/issues/123"
        )

        if result.success:
            print(f"PR submitted: {result.pr_url}")
    """

    def __init__(
        self,
        use_nexus_agents: bool = True,
        github_token: str | None = None,
        dry_run: bool = False,
    ):
        """
        Initialize the contributor.

        Args:
            use_nexus_agents: Whether to use nexus-agents for orchestration
            github_token: GitHub personal access token
            dry_run: If True, don't actually submit PRs
        """
        self.use_nexus_agents = use_nexus_agents
        self.dry_run = dry_run

        self.orchestrator = ContributionOrchestrator(
            use_nexus_agents=use_nexus_agents, github_token=github_token
        )
        self.pr_generator = PRGenerator(github_token=github_token)
        self.verifier = Verifier()

    def submit_fix(
        self, issue_url: str, branch_name: str | None = None, skip_tests: bool = False
    ) -> ContributionResult:
        """
        Submit a fix for an issue.

        Args:
            issue_url: Full URL to the GitHub issue
            branch_name: Custom branch name (optional)
            skip_tests: Whether to skip running tests

        Returns:
            ContributionResult with details of the contribution
        """
        return self.orchestrator.contribute(
            issue_url=issue_url,
            branch_name=branch_name,
            skip_tests=skip_tests,
            dry_run=self.dry_run,
        )

    def plan_fix(self, issue_url: str) -> dict:
        """
        Plan a fix without actually implementing it.

        Args:
            issue_url: Full URL to the GitHub issue

        Returns:
            Dictionary with the contribution plan
        """
        return self.orchestrator.plan(issue_url)

    def verify_changes(
        self, repo_path: str, run_tests: bool = True, run_lint: bool = True
    ) -> dict:
        """
        Verify changes before submission.

        Args:
            repo_path: Path to the cloned repository
            run_tests: Whether to run tests
            run_lint: Whether to run linting

        Returns:
            Dictionary with verification results
        """
        return self.verifier.verify(
            repo_path=repo_path, run_tests=run_tests, run_lint=run_lint
        )


__all__ = [
    "ContributionOrchestrator",
    "ContributionResult",
    "Contributor",
    "PRGenerator",
    "Verifier",
]

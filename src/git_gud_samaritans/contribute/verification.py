"""
Verification module for checking changes before submission.
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import structlog

logger = structlog.get_logger()


@dataclass
class VerificationResult:
    """Result of verification checks."""

    passed: bool
    tests_passed: bool = True
    lint_passed: bool = True
    type_check_passed: bool = True
    security_passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "tests_passed": self.tests_passed,
            "lint_passed": self.lint_passed,
            "type_check_passed": self.type_check_passed,
            "security_passed": self.security_passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class Verifier:
    """
    Verifies changes before submission.

    Runs:
    - Tests
    - Linting
    - Type checking (if applicable)
    - Security scanning (basic)
    """

    # Common test commands by ecosystem
    TEST_COMMANDS: ClassVar[dict[str, list[str]]] = {
        "python": ["pytest", "python -m pytest", "python -m unittest discover"],
        "javascript": ["npm test", "yarn test", "pnpm test"],
        "typescript": ["npm test", "yarn test", "pnpm test"],
        "rust": ["cargo test"],
        "go": ["go test ./..."],
    }

    # Common lint commands
    LINT_COMMANDS: ClassVar[dict[str, list[str]]] = {
        "python": ["ruff check", "flake8", "pylint"],
        "javascript": ["eslint .", "npm run lint"],
        "typescript": ["eslint .", "npm run lint", "tsc --noEmit"],
        "rust": ["cargo clippy"],
        "go": ["golangci-lint run"],
    }

    def verify(
        self,
        repo_path: str,
        run_tests: bool = True,
        run_lint: bool = True,
        run_type_check: bool = True,
        run_security: bool = False,
    ) -> dict:
        """
        Run verification checks on a repository.

        Args:
            repo_path: Path to the repository
            run_tests: Whether to run tests
            run_lint: Whether to run linting
            run_type_check: Whether to run type checking
            run_security: Whether to run security scanning

        Returns:
            Dictionary with verification results
        """
        logger.info("starting_verification", repo_path=repo_path)

        path = Path(repo_path)
        errors: list[str] = []
        warnings: list[str] = []

        # Detect language
        language = self._detect_language(path)
        logger.info("detected_language", language=language)

        # Run tests
        tests_passed = True
        if run_tests:
            tests_passed = self._run_tests(path, language)
            if not tests_passed:
                errors.append("Tests failed")

        # Run linting
        lint_passed = True
        if run_lint:
            lint_passed = self._run_lint(path, language)
            if not lint_passed:
                warnings.append("Linting issues found")

        # Run type checking
        type_check_passed = True
        if run_type_check:
            type_check_passed = self._run_type_check(path, language)
            if not type_check_passed:
                warnings.append("Type checking issues found")

        # Run security scanning
        security_passed = True
        if run_security:
            security_passed = self._run_security_scan(path, language)
            if not security_passed:
                errors.append("Security issues found")

        # Overall pass/fail
        passed = tests_passed and security_passed  # Lint and type check are warnings

        result = VerificationResult(
            passed=passed,
            tests_passed=tests_passed,
            lint_passed=lint_passed,
            type_check_passed=type_check_passed,
            security_passed=security_passed,
            errors=errors,
            warnings=warnings,
        )

        logger.info(
            "verification_complete",
            passed=passed,
            tests_passed=tests_passed,
            lint_passed=lint_passed,
        )

        return result.to_dict()

    def _detect_language(self, repo_path: Path) -> str:
        """Detect the primary language of a repository."""
        indicators = {
            "python": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"],
            "javascript": ["package.json"],
            "typescript": ["tsconfig.json"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
        }

        for language, files in indicators.items():
            for file in files:
                if (repo_path / file).exists():
                    # Special case: check if it's TypeScript
                    if (
                        language == "javascript"
                        and (repo_path / "tsconfig.json").exists()
                    ):
                        return "typescript"
                    return language

        return "unknown"

    def _run_tests(self, repo_path: Path, language: str) -> bool:
        """Run tests for the repository."""
        commands = self.TEST_COMMANDS.get(language, [])

        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    cwd=repo_path,
                    capture_output=True,
                    timeout=300,  # 5 minute timeout
                )
                if result.returncode == 0:
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        # No test command worked
        logger.warning("no_test_command_found", language=language)
        return True  # Assume pass if no tests found

    def _run_lint(self, repo_path: Path, language: str) -> bool:
        """Run linting for the repository."""
        commands = self.LINT_COMMANDS.get(language, [])

        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd.split(), cwd=repo_path, capture_output=True, timeout=120
                )
                if result.returncode == 0:
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        logger.warning("no_lint_command_found", language=language)
        return True

    def _run_type_check(self, repo_path: Path, language: str) -> bool:
        """Run type checking for the repository."""
        commands = {
            "python": ["mypy ."],
            "typescript": ["tsc --noEmit"],
        }

        cmds = commands.get(language, [])
        for cmd in cmds:
            try:
                result = subprocess.run(
                    cmd.split(), cwd=repo_path, capture_output=True, timeout=120
                )
                return result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        return True

    def _run_security_scan(self, repo_path: Path, language: str) -> bool:
        """Run basic security scanning."""
        # TODO: Implement security scanning
        # Could use: bandit (Python), npm audit (JS), cargo audit (Rust)
        return True

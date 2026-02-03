"""
Tests for the verification module.
"""

from pathlib import Path

import pytest

from git_gud_samaritans.contribute.verification import VerificationResult, Verifier


class TestVerificationResult:
    """Tests for the VerificationResult dataclass."""

    def test_create_passed_result(self) -> None:
        """VerificationResult should be creatable for passed."""
        result = VerificationResult(
            passed=True,
            tests_passed=True,
            lint_passed=True,
        )
        assert result.passed is True

    def test_create_failed_result(self) -> None:
        """VerificationResult should be creatable for failed."""
        result = VerificationResult(
            passed=False,
            tests_passed=False,
            errors=["Tests failed"],
        )
        assert result.passed is False
        assert "Tests failed" in result.errors

    def test_to_dict(self) -> None:
        """VerificationResult should convert to dict."""
        result = VerificationResult(
            passed=True,
            tests_passed=True,
            lint_passed=True,
            warnings=["Minor issue"],
        )
        data = result.to_dict()
        assert data["passed"] is True
        assert data["warnings"] == ["Minor issue"]


class TestVerifier:
    """Tests for the Verifier class."""

    @pytest.fixture
    def verifier(self) -> Verifier:
        """Provide a Verifier instance."""
        return Verifier()

    def test_detect_python_language(self, verifier: Verifier, tmp_path: Path) -> None:
        """Verifier should detect Python projects."""
        # Create a pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[project]")

        language = verifier._detect_language(tmp_path)
        assert language == "python"

    def test_detect_javascript_language(
        self, verifier: Verifier, tmp_path: Path
    ) -> None:
        """Verifier should detect JavaScript projects."""
        # Create a package.json
        (tmp_path / "package.json").write_text("{}")

        language = verifier._detect_language(tmp_path)
        assert language == "javascript"

    def test_detect_typescript_language(
        self, verifier: Verifier, tmp_path: Path
    ) -> None:
        """Verifier should detect TypeScript projects."""
        # Create both package.json and tsconfig.json
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "tsconfig.json").write_text("{}")

        language = verifier._detect_language(tmp_path)
        assert language == "typescript"

    def test_detect_rust_language(self, verifier: Verifier, tmp_path: Path) -> None:
        """Verifier should detect Rust projects."""
        (tmp_path / "Cargo.toml").write_text("[package]")

        language = verifier._detect_language(tmp_path)
        assert language == "rust"

    def test_detect_go_language(self, verifier: Verifier, tmp_path: Path) -> None:
        """Verifier should detect Go projects."""
        (tmp_path / "go.mod").write_text("module example")

        language = verifier._detect_language(tmp_path)
        assert language == "go"

    def test_detect_unknown_language(self, verifier: Verifier, tmp_path: Path) -> None:
        """Verifier should return unknown for unrecognized projects."""
        language = verifier._detect_language(tmp_path)
        assert language == "unknown"

    def test_verify_returns_dict(self, verifier: Verifier, tmp_path: Path) -> None:
        """verify() should return a dictionary."""
        result = verifier.verify(str(tmp_path))
        assert isinstance(result, dict)
        assert "passed" in result
        assert "tests_passed" in result
        assert "lint_passed" in result

    def test_verify_skip_tests(self, verifier: Verifier, tmp_path: Path) -> None:
        """verify() should respect run_tests=False."""
        result = verifier.verify(str(tmp_path), run_tests=False)
        # Should still pass if tests are skipped
        assert result["tests_passed"] is True

    def test_verify_skip_lint(self, verifier: Verifier, tmp_path: Path) -> None:
        """verify() should respect run_lint=False."""
        result = verifier.verify(str(tmp_path), run_lint=False)
        # Should still pass if lint is skipped
        assert result["lint_passed"] is True

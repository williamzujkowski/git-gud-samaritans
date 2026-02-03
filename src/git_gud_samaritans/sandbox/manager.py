"""
Sandbox manager for git-gud-samaritans.

Wraps moltdown scripts to provide VM-based isolation for contributions.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

import structlog

logger = structlog.get_logger(__name__)

# Default paths - can be overridden via config
DEFAULT_MOLTDOWN_PATH = (
    Path(__file__).parent.parent.parent.parent.parent / "tools" / "moltdown"
)
FALLBACK_MOLTDOWN_PATH = Path.home() / "git" / "moltdown"


class SandboxStatus(Enum):
    """Status of a sandbox VM."""

    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


@dataclass
class SandboxProfile:
    """Resource profile for sandbox VMs."""

    name: str
    memory_mb: int
    vcpus: int
    description: str = ""

    # Predefined profiles
    LIGHT: ClassVar[SandboxProfile]
    STANDARD: ClassVar[SandboxProfile]
    HEAVY: ClassVar[SandboxProfile]


# Initialize class-level profiles after class definition
SandboxProfile.LIGHT = SandboxProfile(
    name="light",
    memory_mb=8192,
    vcpus=2,
    description="Documentation fixes, typo corrections",
)
SandboxProfile.STANDARD = SandboxProfile(
    name="standard",
    memory_mb=12288,
    vcpus=4,
    description="Typical code changes (default)",
)
SandboxProfile.HEAVY = SandboxProfile(
    name="heavy",
    memory_mb=16384,
    vcpus=6,
    description="Build-heavy projects, Docker workloads",
)


@dataclass
class Sandbox:
    """Represents a sandbox VM instance."""

    id: str
    issue_url: str
    owner: str
    repo: str
    issue_num: int
    status: SandboxStatus
    profile: SandboxProfile
    created_at: datetime = field(default_factory=datetime.now)
    vm_name: str = ""
    ip_address: str | None = None

    def __post_init__(self) -> None:
        if not self.vm_name:
            self.vm_name = f"ggs-{self.owner}-{self.repo}-{self.issue_num}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "issue_url": self.issue_url,
            "owner": self.owner,
            "repo": self.repo,
            "issue_num": self.issue_num,
            "status": self.status.value,
            "profile": self.profile.name,
            "created_at": self.created_at.isoformat(),
            "vm_name": self.vm_name,
            "ip_address": self.ip_address,
        }


class SandboxManager:
    """
    Manages sandbox VMs for contribution isolation.

    Wraps moltdown scripts (clone_manager.sh, agent.sh) to provide
    a Python interface for sandbox lifecycle management.
    """

    # Resource limits for 64GB host
    MAX_CONCURRENT_SANDBOXES: ClassVar[int] = 3
    HOST_RESERVED_MB: ClassVar[int] = 16384  # 16GB for host

    def __init__(
        self,
        moltdown_path: Path | None = None,
        base_vm: str = "ubuntu2404-agent",
        config_path: Path | None = None,
    ) -> None:
        """
        Initialize sandbox manager.

        Args:
            moltdown_path: Path to moltdown installation. Auto-detected if not provided.
            base_vm: Name of the base VM to clone from.
            config_path: Path to sandbox config file.
        """
        self.moltdown_path = self._find_moltdown(moltdown_path)
        self.base_vm = base_vm
        self.config_path = config_path
        self._sandboxes: dict[str, Sandbox] = {}

        logger.info(
            "sandbox_manager_initialized",
            moltdown_path=str(self.moltdown_path),
            base_vm=base_vm,
        )

    def _find_moltdown(self, explicit_path: Path | None = None) -> Path:
        """Find moltdown installation."""
        if explicit_path and explicit_path.exists():
            return explicit_path

        # Check submodule location first
        if DEFAULT_MOLTDOWN_PATH.exists():
            return DEFAULT_MOLTDOWN_PATH

        # Fallback to home directory
        if FALLBACK_MOLTDOWN_PATH.exists():
            return FALLBACK_MOLTDOWN_PATH

        raise FileNotFoundError(
            "moltdown not found. Please either:\n"
            "  1. Initialize submodule: git submodule update --init\n"
            "  2. Clone moltdown to ~/git/moltdown\n"
            "  3. Specify path explicitly"
        )

    def _run_moltdown_script(
        self,
        script: str,
        args: list[str],
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run a moltdown script."""
        script_path = self.moltdown_path / script
        if not script_path.exists():
            raise FileNotFoundError(f"moltdown script not found: {script_path}")

        cmd = [str(script_path), *args]
        logger.debug("running_moltdown_script", cmd=cmd)

        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            cwd=str(self.moltdown_path),
        )

        if result.returncode != 0:
            logger.error(
                "moltdown_script_failed",
                script=script,
                returncode=result.returncode,
                stderr=result.stderr,
            )

        return result

    def _parse_issue_url(self, issue_url: str) -> tuple[str, str, int]:
        """
        Parse GitHub issue URL into components.

        Args:
            issue_url: Full URL like https://github.com/owner/repo/issues/123

        Returns:
            Tuple of (owner, repo, issue_number)
        """
        pattern = r"https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.match(pattern, issue_url)

        if not match:
            raise ValueError(
                f"Invalid issue URL format: {issue_url}\n"
                "Expected: https://github.com/owner/repo/issues/123"
            )

        return match.group(1), match.group(2), int(match.group(3))

    def _generate_sandbox_id(self, owner: str, repo: str, issue_num: int) -> str:
        """Generate unique sandbox ID."""
        return f"ggs-{owner}-{repo}-{issue_num}"

    def _check_resources(self, profile: SandboxProfile) -> None:
        """Check if host has sufficient resources for new sandbox."""
        active = self.list_sandboxes(status_filter=SandboxStatus.RUNNING)

        if len(active) >= self.MAX_CONCURRENT_SANDBOXES:
            raise ResourceError(
                f"Maximum concurrent sandboxes ({self.MAX_CONCURRENT_SANDBOXES}) reached. "
                f"Cleanup an existing sandbox first: ggs sandbox list"
            )

        total_allocated = sum(s.profile.memory_mb for s in active)
        available = (64 * 1024) - self.HOST_RESERVED_MB - total_allocated

        if profile.memory_mb > available:
            raise ResourceError(
                f"Insufficient memory. Requested: {profile.memory_mb}MB, "
                f"Available: {available}MB. Try a lighter profile or cleanup sandboxes."
            )

    def create(
        self,
        issue_url: str,
        profile: SandboxProfile | None = None,
    ) -> Sandbox:
        """
        Create a new sandbox for contributing to an issue.

        Args:
            issue_url: GitHub issue URL
            profile: Resource profile (default: STANDARD)

        Returns:
            Created Sandbox instance
        """
        profile = profile or SandboxProfile.STANDARD
        owner, repo, issue_num = self._parse_issue_url(issue_url)
        sandbox_id = self._generate_sandbox_id(owner, repo, issue_num)

        # Check if sandbox already exists
        if sandbox_id in self._sandboxes:
            existing = self._sandboxes[sandbox_id]
            if existing.status == SandboxStatus.RUNNING:
                logger.info("sandbox_already_exists", sandbox_id=sandbox_id)
                return existing

        # Check resource availability
        self._check_resources(profile)

        logger.info(
            "creating_sandbox",
            sandbox_id=sandbox_id,
            issue_url=issue_url,
            profile=profile.name,
        )

        # Create sandbox instance
        sandbox = Sandbox(
            id=sandbox_id,
            issue_url=issue_url,
            owner=owner,
            repo=repo,
            issue_num=issue_num,
            status=SandboxStatus.CREATING,
            profile=profile,
        )

        # Create linked clone via moltdown
        result = self._run_moltdown_script(
            "clone_manager.sh",
            [
                "create",
                self.base_vm,
                "--linked",
                "--memory",
                str(profile.memory_mb),
                "--vcpus",
                str(profile.vcpus),
                "--name",
                sandbox.vm_name,
            ],
        )

        if result.returncode != 0:
            sandbox.status = SandboxStatus.ERROR
            self._sandboxes[sandbox_id] = sandbox
            raise SandboxError(f"Failed to create sandbox: {result.stderr}")

        # Start the clone
        start_result = self._run_moltdown_script(
            "clone_manager.sh",
            ["start", sandbox.vm_name],
        )

        if start_result.returncode != 0:
            sandbox.status = SandboxStatus.ERROR
            self._sandboxes[sandbox_id] = sandbox
            raise SandboxError(f"Failed to start sandbox: {start_result.stderr}")

        # Get IP address
        sandbox.ip_address = self._get_vm_ip(sandbox.vm_name)
        sandbox.status = SandboxStatus.RUNNING
        self._sandboxes[sandbox_id] = sandbox

        logger.info(
            "sandbox_created",
            sandbox_id=sandbox_id,
            vm_name=sandbox.vm_name,
            ip_address=sandbox.ip_address,
        )

        return sandbox

    def _get_vm_ip(self, vm_name: str) -> str | None:
        """Get IP address of a VM."""
        result = subprocess.run(
            ["virsh", "domifaddr", vm_name],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return None

        # Parse IP from output
        for line in result.stdout.split("\n"):
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if match:
                return match.group(1)

        return None

    def get(self, sandbox_id: str) -> Sandbox | None:
        """Get sandbox by ID."""
        return self._sandboxes.get(sandbox_id)

    def list_sandboxes(
        self,
        status_filter: SandboxStatus | None = None,
    ) -> list[Sandbox]:
        """
        List all sandboxes.

        Args:
            status_filter: Filter by status (optional)

        Returns:
            List of Sandbox instances
        """
        sandboxes = list(self._sandboxes.values())

        if status_filter:
            sandboxes = [s for s in sandboxes if s.status == status_filter]

        return sandboxes

    def enter(self, sandbox_id: str) -> str:
        """
        Get SSH command to enter a sandbox.

        Args:
            sandbox_id: Sandbox ID

        Returns:
            SSH command string
        """
        sandbox = self._sandboxes.get(sandbox_id)
        if not sandbox:
            raise SandboxError(f"Sandbox not found: {sandbox_id}")

        if sandbox.status != SandboxStatus.RUNNING:
            raise SandboxError(f"Sandbox is not running: {sandbox.status.value}")

        if not sandbox.ip_address:
            sandbox.ip_address = self._get_vm_ip(sandbox.vm_name)

        if not sandbox.ip_address:
            raise SandboxError(f"Could not determine IP for sandbox: {sandbox_id}")

        return f"ssh agent@{sandbox.ip_address}"

    def exec(self, sandbox_id: str, command: str) -> subprocess.CompletedProcess[str]:
        """
        Execute a command inside a sandbox.

        Args:
            sandbox_id: Sandbox ID
            command: Command to execute

        Returns:
            CompletedProcess with output
        """
        sandbox = self._sandboxes.get(sandbox_id)
        if not sandbox:
            raise SandboxError(f"Sandbox not found: {sandbox_id}")

        if not sandbox.ip_address:
            sandbox.ip_address = self._get_vm_ip(sandbox.vm_name)

        if not sandbox.ip_address:
            raise SandboxError(f"Could not determine IP for sandbox: {sandbox_id}")

        return subprocess.run(
            ["ssh", f"agent@{sandbox.ip_address}", command],
            capture_output=True,
            text=True,
        )

    def cleanup(self, sandbox_id: str, force: bool = False) -> None:
        """
        Destroy a sandbox.

        Args:
            sandbox_id: Sandbox ID
            force: Force destruction even if running
        """
        sandbox = self._sandboxes.get(sandbox_id)
        if not sandbox:
            raise SandboxError(f"Sandbox not found: {sandbox_id}")

        if sandbox.status == SandboxStatus.RUNNING and not force:
            # Stop first
            self._run_moltdown_script(
                "clone_manager.sh",
                ["stop", sandbox.vm_name],
            )

        # Delete the clone
        result = self._run_moltdown_script(
            "clone_manager.sh",
            ["delete", sandbox.vm_name],
        )

        if result.returncode != 0:
            logger.warning(
                "sandbox_cleanup_warning",
                sandbox_id=sandbox_id,
                stderr=result.stderr,
            )

        sandbox.status = SandboxStatus.DESTROYED
        logger.info("sandbox_destroyed", sandbox_id=sandbox_id)

    def cleanup_all(self) -> int:
        """
        Destroy all sandboxes.

        Returns:
            Number of sandboxes destroyed
        """
        count = 0
        for sandbox_id in list(self._sandboxes.keys()):
            try:
                self.cleanup(sandbox_id, force=True)
                count += 1
            except SandboxError as e:
                logger.warning("cleanup_failed", sandbox_id=sandbox_id, error=str(e))

        return count


class SandboxError(Exception):
    """Base exception for sandbox operations."""

    pass


class ResourceError(SandboxError):
    """Raised when host resources are insufficient."""

    pass

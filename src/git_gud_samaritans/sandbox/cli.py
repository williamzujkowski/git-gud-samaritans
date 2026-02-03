"""
CLI commands for sandbox management.

Provides ggs sandbox subcommands for creating, managing, and destroying
isolated contribution environments.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .manager import (
    ResourceError,
    Sandbox,
    SandboxError,
    SandboxManager,
    SandboxProfile,
    SandboxStatus,
)

console = Console()

# Singleton manager instance
_manager: SandboxManager | None = None


def get_manager() -> SandboxManager:
    """Get or create the sandbox manager singleton."""
    global _manager
    if _manager is None:
        try:
            _manager = SandboxManager()
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/] {e}")
            sys.exit(1)
    return _manager


@click.group()
def sandbox() -> None:
    """
    Manage sandbox VMs for isolated contributions.

    Sandboxes provide isolated VM environments to safely clone, test,
    and contribute to external repositories.

    \b
    Examples:
        ggs sandbox create https://github.com/owner/repo/issues/123
        ggs sandbox list
        ggs sandbox enter ggs-owner-repo-123
        ggs sandbox cleanup ggs-owner-repo-123
    """
    pass


@sandbox.command()
@click.argument("issue_url")
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["light", "standard", "heavy"]),
    default="standard",
    help="Resource profile for the sandbox",
)
@click.pass_context
def create(ctx: click.Context, issue_url: str, profile: str) -> None:
    """
    Create a new sandbox for contributing to an issue.

    Creates an isolated VM clone to safely work on the contribution.
    The target repository will be cloned inside the sandbox.

    \b
    Examples:
        ggs sandbox create https://github.com/owner/repo/issues/123
        ggs sandbox create https://github.com/owner/repo/issues/456 --profile heavy
    """
    manager = get_manager()

    # Map profile string to SandboxProfile
    profile_map = {
        "light": SandboxProfile.LIGHT,
        "standard": SandboxProfile.STANDARD,
        "heavy": SandboxProfile.HEAVY,
    }
    selected_profile = profile_map[profile]

    console.print(f"[bold]Creating sandbox for:[/] {issue_url}")
    console.print(
        f"[dim]Profile: {selected_profile.name} ({selected_profile.memory_mb}MB, {selected_profile.vcpus} vCPUs)[/]"
    )

    try:
        with console.status("[bold green]Creating sandbox VM..."):
            sandbox_instance = manager.create(issue_url, profile=selected_profile)

        _print_sandbox_created(sandbox_instance)

    except ResourceError as e:
        console.print(f"\n[red]Resource Error:[/] {e}")
        sys.exit(1)
    except SandboxError as e:
        console.print(f"\n[red]Sandbox Error:[/] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"\n[red]Invalid Input:[/] {e}")
        sys.exit(1)


def _print_sandbox_created(sandbox_instance: Sandbox) -> None:
    """Print sandbox creation success message."""
    panel_content = f"""
[bold green]Sandbox created successfully![/]

[bold]ID:[/]          {sandbox_instance.id}
[bold]VM Name:[/]     {sandbox_instance.vm_name}
[bold]IP Address:[/]  {sandbox_instance.ip_address or "Pending..."}
[bold]Profile:[/]     {sandbox_instance.profile.name}
[bold]Issue:[/]       {sandbox_instance.issue_url}

[bold]Next steps:[/]
  1. Enter the sandbox:
     [cyan]ggs sandbox enter {sandbox_instance.id}[/]

  2. Clone the target repo inside:
     [cyan]gh repo clone {sandbox_instance.owner}/{sandbox_instance.repo}[/]

  3. When done, cleanup:
     [cyan]ggs sandbox cleanup {sandbox_instance.id}[/]
"""
    console.print(Panel(panel_content, title="Sandbox Ready", border_style="green"))


@sandbox.command("list")
@click.option(
    "--status",
    "-s",
    type=click.Choice(["running", "stopped", "all"]),
    default="all",
    help="Filter by status",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_sandboxes(ctx: click.Context, status: str, output_format: str) -> None:
    """
    List all sandboxes.

    \b
    Examples:
        ggs sandbox list
        ggs sandbox list --status running
        ggs sandbox list --format json
    """
    manager = get_manager()

    # Map status filter
    status_filter = None
    if status == "running":
        status_filter = SandboxStatus.RUNNING
    elif status == "stopped":
        status_filter = SandboxStatus.STOPPED

    sandboxes = manager.list_sandboxes(status_filter=status_filter)

    if not sandboxes:
        console.print("[dim]No sandboxes found.[/]")
        console.print("\nCreate one with: [cyan]ggs sandbox create <issue-url>[/]")
        return

    if output_format == "json":
        import json

        console.print(json.dumps([s.to_dict() for s in sandboxes], indent=2))
    else:
        _print_sandbox_table(sandboxes)


def _print_sandbox_table(sandboxes: list[Sandbox]) -> None:
    """Print sandboxes as a table."""
    table = Table(title="Active Sandboxes")
    table.add_column("ID", style="cyan")
    table.add_column("Repository", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Profile")
    table.add_column("IP Address")
    table.add_column("Uptime", justify="right")

    for s in sandboxes:
        # Calculate uptime
        uptime = datetime.now() - s.created_at
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m"

        # Status with color
        status_color = {
            SandboxStatus.RUNNING: "green",
            SandboxStatus.STOPPED: "yellow",
            SandboxStatus.CREATING: "blue",
            SandboxStatus.ERROR: "red",
            SandboxStatus.DESTROYED: "dim",
        }.get(s.status, "white")

        table.add_row(
            s.id,
            f"{s.owner}/{s.repo}",
            f"[{status_color}]{s.status.value}[/{status_color}]",
            s.profile.name,
            s.ip_address or "-",
            uptime_str if s.status == SandboxStatus.RUNNING else "-",
        )

    console.print(table)


@sandbox.command()
@click.argument("sandbox_id")
@click.pass_context
def enter(ctx: click.Context, sandbox_id: str) -> None:
    """
    SSH into a sandbox.

    Opens an interactive SSH session to the sandbox VM.

    \b
    Example:
        ggs sandbox enter ggs-owner-repo-123
    """
    manager = get_manager()

    try:
        ssh_cmd = manager.enter(sandbox_id)
        console.print(f"[bold]Connecting to sandbox:[/] {sandbox_id}")
        console.print(f"[dim]Command: {ssh_cmd}[/]\n")

        # Execute SSH interactively
        subprocess.run(ssh_cmd.split(), check=False)

    except SandboxError as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@sandbox.command()
@click.argument("sandbox_id")
@click.argument("command")
@click.pass_context
def exec(ctx: click.Context, sandbox_id: str, command: str) -> None:
    """
    Execute a command inside a sandbox.

    Runs the specified command via SSH and returns the output.

    \b
    Example:
        ggs sandbox exec ggs-owner-repo-123 "pytest tests/"
        ggs sandbox exec ggs-owner-repo-123 "git status"
    """
    manager = get_manager()

    try:
        console.print(f"[bold]Executing in {sandbox_id}:[/] {command}")

        result = manager.exec(sandbox_id, command)

        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/]")

        if result.returncode != 0:
            console.print(f"\n[yellow]Exit code: {result.returncode}[/]")
            sys.exit(result.returncode)

    except SandboxError as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@sandbox.command()
@click.argument("sandbox_id", required=False)
@click.option("--all", "-a", "cleanup_all", is_flag=True, help="Cleanup all sandboxes")
@click.option("--force", "-f", is_flag=True, help="Force cleanup of running sandboxes")
@click.confirmation_option(prompt="Are you sure you want to destroy the sandbox(es)?")
@click.pass_context
def cleanup(
    ctx: click.Context,
    sandbox_id: str | None,
    cleanup_all: bool,
    force: bool,
) -> None:
    """
    Destroy a sandbox.

    Removes the sandbox VM and frees resources.

    \b
    Examples:
        ggs sandbox cleanup ggs-owner-repo-123
        ggs sandbox cleanup --all
        ggs sandbox cleanup ggs-owner-repo-123 --force
    """
    manager = get_manager()

    if cleanup_all:
        console.print("[bold]Destroying all sandboxes...[/]")
        count = manager.cleanup_all()
        console.print(f"[green]Destroyed {count} sandbox(es)[/]")
        return

    if not sandbox_id:
        console.print("[red]Error:[/] Please specify a sandbox ID or use --all")
        sys.exit(1)

    try:
        console.print(f"[bold]Destroying sandbox:[/] {sandbox_id}")
        manager.cleanup(sandbox_id, force=force)
        console.print("[green]Sandbox destroyed successfully[/]")

    except SandboxError as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@sandbox.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """
    Show sandbox system status.

    Displays resource usage and availability.
    """
    manager = get_manager()

    sandboxes = manager.list_sandboxes()
    running = [s for s in sandboxes if s.status == SandboxStatus.RUNNING]

    total_memory = sum(s.profile.memory_mb for s in running)
    total_vcpus = sum(s.profile.vcpus for s in running)

    host_available_mb = (64 * 1024) - manager.HOST_RESERVED_MB
    memory_used_pct = (
        (total_memory / host_available_mb) * 100 if host_available_mb > 0 else 0
    )

    panel_content = f"""
[bold]Host Resources:[/]
  Total RAM:        64 GB
  Reserved:         {manager.HOST_RESERVED_MB // 1024} GB
  Available for VMs: {host_available_mb // 1024} GB

[bold]Current Usage:[/]
  Running Sandboxes: {len(running)} / {manager.MAX_CONCURRENT_SANDBOXES}
  Memory Allocated:  {total_memory // 1024} GB ({memory_used_pct:.0f}%)
  vCPUs Allocated:   {total_vcpus}

[bold]Moltdown:[/]
  Path: {manager.moltdown_path}
  Base VM: {manager.base_vm}
"""
    console.print(
        Panel(panel_content, title="Sandbox System Status", border_style="blue")
    )

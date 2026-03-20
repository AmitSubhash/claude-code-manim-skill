"""Shared UI helpers for CLI commands."""

from __future__ import annotations

import sys

import click

from .generate import PROVIDERS


def prompt_provider() -> str:
    """Interactive provider selection prompt."""
    click.echo("\nWhich LLM provider?\n")
    items = list(PROVIDERS.items())
    for i, (key, cfg) in enumerate(items, 1):
        click.echo(f"  {i}. {cfg['label']}")
    click.echo()
    choice = click.prompt("Provider", type=click.IntRange(1, len(items)))
    return items[choice - 1][0]


def confirm_plan(plan: str) -> str:
    """Show the video plan and let the user approve, edit, or quit."""
    click.echo("\n" + "=" * 60 + "\nVIDEO PLAN\n" + "=" * 60)
    click.echo(plan)
    click.echo("=" * 60 + "\n")
    while True:
        choice = click.prompt(
            "Proceed? [y]es / [e]dit / [q]uit", default="y"
        ).strip().lower()
        if choice in ("y", "yes"):
            return plan
        if choice in ("q", "quit"):
            click.echo("Aborted.")
            sys.exit(0)
        if choice in ("e", "edit"):
            edited = click.edit(plan)
            return edited if edited is not None else plan
        click.echo("  Please enter y, e, or q.")

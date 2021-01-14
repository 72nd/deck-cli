"""
Main file for the CLI interface.
"""
from deck_cli.cli.config import Config

import click


@click.group()
def cli():
    """
    deck-cli is a collection of CLI tools for working with the Deck App
    from Nextcloud.
    """


@click.command()
def add():
    """Add a new card to a deck."""


@click.command()
@click.argument("PATH", type=click.File("wb"))
def config(path: click.File):
    """Creates a default configuration file for the application."""
    cfg = Config()
    path.write(bytes(cfg.to_yaml(), "utf-8"))


@click.command()
def mail():
    """The mail command sends a notification mail to all users."""


@click.command()
def mail_template():
    """Saves the default template for the mail notification for
    further customization."""


@click.command()
def report():
    """The report command creates a overview over all tasks."""
    print("the report command")


@click.command()
def report_template():
    """Creates the default template for the report for further
    customization."""


cli.add_command(add)
cli.add_command(config)
cli.add_command(mail)
cli.add_command(mail_template)
cli.add_command(report)

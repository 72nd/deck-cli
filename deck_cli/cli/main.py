"""
Main file for the CLI interface.
"""
import logging

from deck_cli.cli.config import Config as ConfigClass
from deck_cli.cli.report import Report

import click


mute_progress: bool = False


@click.group()
@click.option("-d", "--debug", is_flag=True)
@click.option("--mute", is_flag=True, help="disable the progress update")
def cli(debug, mute):
    """
    deck-cli is a collection of CLI tools for working with the Deck App
    from Nextcloud.
    """
    if debug:
        logger = logging.getLogger("deck")
        logger.setLevel(logging.DEBUG)
    if mute:
        mute_progress = True


@click.command()
def add():
    """Add a new card to a deck."""


@click.command()
@click.argument("PATH", type=click.File("wb"))
def config(path: click.File):
    """Creates a default configuration file for the application."""
    cfg = ConfigClass.defaults()
    path.write(bytes(cfg.to_yaml(), "utf-8"))


@click.command()
def mail():
    """The mail command sends a notification mail to all users."""


@click.command()
def mail_template():
    """Saves the default template for the mail notification for
    further customization."""


@click.command()
@click.argument("CONFIG", type=click.File("r"))
def report(config: click.File):
    """The report command creates a overview over all tasks."""
    data = ConfigClass.from_yaml(config)
    report = Report(data)
    report.run(on_progress)


@click.command()
def report_template():
    """Creates the default template for the report for further
    customization."""


def on_progress(current_step: int, total_steps: int, message: str):
    """
    ProgressCallback implementation for this CLI. Used to display the progress
    of the API calls to the user (as this can take some time).
    """
    if mute_progress:
        return
    total = str(total_steps)
    if total_steps == 0:
        total = "x"
    print("[{}/{}] {}".format(current_step, total, message))


cli.add_command(add)
cli.add_command(config)
cli.add_command(mail)
cli.add_command(mail_template)
cli.add_command(report)

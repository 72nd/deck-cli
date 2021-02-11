"""
Main file for the CLI interface.
"""
import logging

from deck_cli.cli.config import Config as ConfigClass
from deck_cli.cli import fetch
from deck_cli.cli.interactive import Interactive
from deck_cli.cli.query import Query
from deck_cli.cli.report import Report

import click


class State:
    """Contains the global state for all subcommands of the group."""
    do_debug: bool = False
    muted: bool = False

    def __init__(self, do_debug: bool, muted: bool):
        self.do_debug = do_debug
        self.do_mute = muted

    def on_progress(
            self,
            current_step: int,
            total_steps:
            int,
            message: str
    ):
        """
        ProgressCallback implementation for this CLI. Used to display the
        progress of the API calls to the user (as this can take some time).
        """
        if self.muted:
            return
        total = str(total_steps)
        if total_steps == 0:
            total = "x"
        print("[{}/{}] {}".format(current_step, total, message))


pass_state = click.make_pass_decorator(State)


@click.group()
@click.option("-d", "--debug", is_flag=True)
@click.option("--muted", is_flag=True, help="disable the progress update")
@click.pass_context
def cli(ctx, debug, muted):
    """
    deck-cli is a collection of CLI tools for working with the Deck App
    from Nextcloud.
    """
    if debug:
        logger = logging.getLogger("deck")
        logger.setLevel(logging.DEBUG)
    ctx.obj = State(debug, muted)


@click.command()
@click.argument(
    "CONFIG",
    type=click.File("r"),
)
@pass_state
def add(state, config):
    """Add a new card to a deck."""
    cfg = ConfigClass.from_yaml(config)
    intr = Interactive(cfg)
    intr.add()


@click.command()
@click.argument("PATH", type=click.File("wb"))
def config(path: click.File):
    """Creates a default configuration file for the application."""
    cfg = ConfigClass.defaults()
    path.write(bytes(cfg.to_yaml(), "utf-8"))


@click.command()
@click.argument(
    "CONFIG",
    type=click.File("r"),
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    help="path to output file",
    default="api-dump.yaml"
)
@pass_state
def dump(state, config: click.File, output: click.File):
    """Dumps the Deck from the API and saves to the given path."""
    cfg = ConfigClass.from_yaml(config)
    fetch.deck_to_file(cfg, output, state.on_progress)


@click.command()
@click.argument(
    "CONFIG",
    type=click.File("r"),
)
def mail():
    """The mail command sends a notification mail to all users."""


@click.command()
def mail_template():
    """Saves the default template for the mail notification for
    further customization."""


@click.command()
@click.argument(
    "CONFIG",
    type=click.File("r"),
)
@click.option(
    "-b",
    "--blocks",
    type=click.Choice(
        ["overdue", "overview", "stats"],
        case_sensitive=False,
    ),
    multiple=True,
    default=["overdue", "overview", "stats"],
)
@click.option(
    "--dump",
    type=click.File("r"),
    help="path to Deck API dump",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["plain", "markdown"], case_sensitive=False),
    help="choose output format",
    default="plain"
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    help="path to output file",
)
@pass_state
def report(
    state,
    blocks: click.Choice,
    config: click.File,
    dump: click.File,
    fmt: click.Choice,
    output: click.File,
):
    """The report command creates a overview over all tasks."""
    cfg = ConfigClass.from_yaml(config)
    rep = Report(blocks, cfg, dump, fmt, output, state.on_progress)
    rep.render()


@click.group()
def query():
    """Multiple commands to output the content of the output."""


@click.command()
@click.argument(
    "CONFIG",
    type=click.File("r"),
)
@click.option(
    "--dump",
    type=click.File("r"),
    help="path to Deck API dump",
)
@pass_state
def users(state, config: click.File, dump: click.File):
    """List the available users."""
    cfg = ConfigClass.from_yaml(config)
    query = Query(cfg, dump, state.on_progress)
    query.users()


query.add_command(users)


@click.command()
def report_template():
    """Creates the default template for the report for further
    customization."""


cli.add_command(add)
cli.add_command(config)
cli.add_command(dump)
# cli.add_command(mail)
# cli.add_command(mail_template)
# cli.add_command(query)
cli.add_command(report)

"""
Contains all functionality to create the reports for
the Desk content.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import importlib.resources

from deck_cli.cli import fetch
from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch, ProgressCallback
from deck_cli.deck.simplified import Card, Deck, UserWithCards

import click
from jinja2 import Template


class ReportFromat(Enum):
    """The possible output formats for an Report."""
    PLAIN = "simple-report.jinja"
    MARKDOWN = "markdown-report.jinja"


class ReportOptions:
    """The options for a report."""
    fmt: ReportFromat
    do_overdue: bool
    do_overview: bool
    do_stats: bool

    def __init__(self, blocks: click.Choice, fmt: click.Choice):
        self.fmt = ReportFromat.PLAIN
        if fmt == "markdown":
            self.fmt = ReportFromat.MARKDOWN
        self.do_overdue = "overdue" in blocks
        self.do_overview = "overview" in blocks
        self.do_stats = "stats" in blocks


class Report:
    """A Deck Report."""
    config: 'Config'
    dump: Optional[click.File]
    options: ReportOptions
    output: Optional[click.File]
    on_progress: ProgressCallback

    def __init__(
        self,
        blocks: click.Choice,
        config: Config,
        dump: Optional[click.File],
        fmt: click.Choice,
        output: Optional[click.File],
        on_progress: ProgressCallback
    ):
        self.config = config
        self.dump_file = dump
        self.options = ReportOptions(blocks, fmt)
        self.output = output
        self.on_progress = lambda *args: None
        if output is not None:
            self.on_progress = on_progress

    def render(self):
        """Fetches the data and renders the requested report."""
        deck: Deck
        if self.dump_file is None:
            deck = self.__fetch_deck()
        else:
            deck = fetch.load_deck_from_file(self.dump_file)

        users = UserWithCards.from_deck(deck)
        overdue: List[Card] = []
        if self.options.do_overdue:
            overdue = deck.overdue_cards()
        tpl_raw = importlib.resources.read_text(
            "deck_cli.cli.templates", self.options.fmt.value)
        tpl = Template(tpl_raw)
        rsl = tpl.render(
            now=datetime.now(tz=timezone.utc),
            options=self.options,
            overdue=Card.by_board(overdue),
            users=users
        )

        if self.output is not None:
            self.output.write(rsl)
        else:
            print(rsl)

    def __fetch_deck(self) -> List[UserWithCards]:
        f = Fetch(
            self.config.url,
            self.config.user,
            self.config.password,
            progress_callback=self.on_progress
        )
        return Deck.from_nc_boards(
            f.all_boards_with_stacks(),
            self.config.backlog_stacks,
            self.config.progress_stacks,
            self.config.done_stacks
        )

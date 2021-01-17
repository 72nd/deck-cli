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
    do_per_user: bool
    do_stats: bool

    def __init__(self, blocks: click.Choice, fmt: click.Choice):
        self.fmt = ReportFromat.PLAIN
        if fmt == "markdown":
            self.fmt = ReportFromat.MARKDOWN
        self.do_overdue = "overdue" in blocks
        self.do_overview = "overview" in blocks
        self.do_per_user = "per-user" in blocks
        self.do_stats = "stats" in blocks


class Report:
    """A Deck Report."""
    config: 'Config'
    dump: Optional[click.File]
    options: ReportOptions

    def __init__(
        self,
        blocks: click.Choice,
        config: Config,
        dump: Optional[click.File],
        fmt: click.Choice,
    ):
        self.config = config
        self.dump_file = dump
        self.options = ReportOptions(blocks, fmt)

    def render(self, on_progress: ProgressCallback):
        """Fetches the data and renders the requested report."""
        deck: Deck
        if self.dump_file is None:
            deck = self.__fetch_deck(on_progress)
        else:
            deck = fetch.load_deck_from_file(self.dump_file)

        users = UserWithCards.from_deck(deck)
        overdue: List[Card] = []
        if self.options.do_overdue:
            overdue = deck.overdue_cards()
        tpl_raw = importlib.resources.read_text(
            "deck_cli.cli.templates", self.options.fmt.value)
        tpl = Template(tpl_raw)
        print(tpl.render(
            now=datetime.now(tz=timezone.utc),
            options=self.options,
            overdue=Card.by_board(overdue),
            users=users
        ))

    def __fetch_deck(
            self,
            on_progress: ProgressCallback
    ) -> List[UserWithCards]:
        deck = Fetch(self.config.url, self.config.user,
                     self.config.password, progress_callback=on_progress)
        return Deck.from_nc_boards(
            deck.all_boards_with_stacks(),
            self.config.backlog_stacks,
            self.config.progress_stacks,
            self.config.done_stacks
        )

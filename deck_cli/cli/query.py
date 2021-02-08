"""
Query contents of the Deck content and outputs it as a string.
"""
from typing import Optional


from deck_cli.cli import fetch
from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch, ProgressCallback
from deck_cli.deck.simplified import Card, Deck, UserWithCards

import click


class Query:
    """
    A Query object used to render certain parts of the Deck content as a
    string. The output gets ordered alphabetically.
    """
    config: Config
    dump: Optional[click.File]
    on_progress: ProgressCallback

    def __init__(
        self,
        config: Config,
        dump: Optional[click.File],
        on_progress: ProgressCallback,
    ):
        self.config = config
        self.dump = dump
        self.on_progress = on_progress

    def users(self):
        """List all users of the Deck."""
        deck = self.__fetch_data()
        print(deck.users)

    def __fetch_data(self) -> Deck:
        """Fetches the data from the API or loads it from the dump file."""
        if self.dump is None:
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
        deck = fetch.load_deck_from_file(self.dump)
        return deck

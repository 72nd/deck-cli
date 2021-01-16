"""
Contains all functionality to create the reports for
the Desk content.
"""

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch
from deck_cli.deck.simplified import Deck


class Report:
    """A Deck Report."""
    config: 'Config'

    def __init__(self, config: 'Config'):
        self.config = config

    def run(self):
        """Starts the generation of the report."""
        deck = Fetch(self.config.url, self.config.user, self.config.password)
        print(Deck.from_nc_boards(
            deck.all_boards(),
            self.config.backlog_stacks,
            self.config.progress_stacks,
            self.config.done_stacks
        ))

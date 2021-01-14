"""
Contains all functionality to create the reports from
the Desk content.
"""

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch


class Report:
    """A Deck Report."""
    config: 'Config'

    def __init__(self, config: 'Config'):
        self.config = config

    def run(self):
        """Starts the generation of the report."""
        deck = Fetch(self.config.url, self.config.user, self.config.password)
        print(deck.stacks_by_board(9))

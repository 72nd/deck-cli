"""
Contains all functionality to create the reports for
the Desk content.
"""

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch, ProgressCallback
from deck_cli.deck.simplified import Deck


class Report:
    """A Deck Report."""
    config: 'Config'

    def __init__(self, config: 'Config'):
        self.config = config

    def run(self, on_progress: ProgressCallback):
        """Starts the generation of the report."""
        deck = Fetch(self.config.url, self.config.user,
                     self.config.password, progress_callback=on_progress)
        print(Deck.from_nc_boards(
            deck.all_boards_with_stacks(),
            self.config.backlog_stacks,
            self.config.progress_stacks,
            self.config.done_stacks
        )[1])

"""
Contains all functionality to create the reports for
the Desk content.
"""
from typing import List

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch, ProgressCallback
from deck_cli.deck.simplified import Deck, UserWithCards


class Report:
    """A Deck Report."""
    config: 'Config'

    def __init__(self, config: 'Config'):
        self.config = config

    def simple_report(self, on_progress: ProgressCallback):
        """
        Starts the generation of a simple report. A simple Report doesn't
        relay on any external template.
        """
        users = self.__fetch_user_with_cards(on_progress)
        for user in users:
            print(user.full_name.capitalize)

    def __fetch_user_with_cards(
            self,
            on_progress: ProgressCallback
    ) -> List[UserWithCards]:
        deck = Fetch(self.config.url, self.config.user,
                     self.config.password, progress_callback=on_progress)
        deck = Deck.from_nc_boards(
            deck.all_boards_with_stacks(),
            self.config.backlog_stacks,
            self.config.progress_stacks,
            self.config.done_stacks
        )
        return UserWithCards.from_deck(deck)

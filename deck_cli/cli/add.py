"""
This module handles the adding of Cards to the Deck.
"""

from deck_cli.cli.config import Config


class Add:
    """
    Add interactive new Cards to the Deck.
    """
    config: Config

    def __init(self, config: Config):
        self.config = config

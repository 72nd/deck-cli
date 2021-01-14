"""
Fetch abstracts all calls to the Nextcloud and Deck API.
"""

DECK_APP_URL = "apps/deck/api/v1.0"
ALL_USER_BOARDS_URL = "boards"
SINGLE_BOARD_URL = "boards/{board_id}"
ALL_STACKS_URL = "boards/{board_id}/stacks"
SINGLE_CARD_URL = "boards/{board_id}/stacks/{stack_id}/cards/{card_id}"


class Fetch:
    """Contains all calls to the Nextcloud and Deck API."""
    base_url: str
    user: str
    password: str

    def all_boards(self):
        """Returns all boards of the given user."""

    def board_by_id(self, board_id: int):
        """Returns a board by a given board id."""

    def stacks_by_board(self, board_id: int):
        """Returns all stacks of a given board with the given id."""

    def card_by_board_stack_id(self, board_id: int, stack_id: int):
        """Retruns a card of a given board and it's stack defined by id."""

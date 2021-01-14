"""
Fetch abstracts all calls to the Nextcloud and Deck API.
"""

from deck_cli.deck.nc_board import NCBoard

import requests

DECK_APP_URL = "apps/deck/api/v1.0"
USER_DETAILS_URL = "ocs/v1.php/cloud/{user_uuid}"
ALL_USER_BOARDS_URL = "boards"
SINGLE_BOARD_URL = "boards/{board_id}"
ALL_STACKS_URL = "boards/{board_id}/stacks"
SINGLE_CARD_URL = "boards/{board_id}/stacks/{stack_id}/cards/{card_id}"


class Fetch:
    """Contains all calls to the Nextcloud and Deck API."""
    base_url: str
    user: str
    password: str

    def __init__(self, base_url: str, user: str, password: str):
        self.base_url = base_url
        self.user = user
        self.password = password

    def all_boards(self):
        """Returns all boards of the given user."""
        url = self.__deck_api_url(ALL_USER_BOARDS_URL)
        rqs = requests.get(
            url,
            headers=self.__request_header(),
            auth=(self.user, self.password))
        board = NCBoard.from_json(rqs.text)
        print(board)

    def board_by_id(self, board_id: int):
        """Returns a board by a given board id."""

    def stacks_by_board(self, board_id: int):
        """Returns all stacks of a given board with the given id."""

    def card_by_board_stack_id(self, board_id: int, stack_id: int):
        """Returns a card of a given board and it's stack defined by id."""

    def user_mail(self):
        """
        Returns a dictionary mapping the user names to their mail address.
        """

    def __deck_api_url(self, postfix: str) -> str:
        """Returns the Deck API URL with a given postfix."""
        return "{}/{}/{}".format(self.base_url, DECK_APP_URL, postfix)

    def __request_header(self) -> dict[str, str]:
        """Retruns the request header for all Deck API calls."""
        return {
            "OCS-APIRequest": "true",
            "Content-Type": "application/json",
        }

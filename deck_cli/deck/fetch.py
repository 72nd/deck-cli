"""
Fetch abstracts all calls to the Nextcloud and Deck API.
"""

from deck_cli.deck.models import NCBoard, NCBaseBoard, NCDeckStack

from typing import List

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

    def all_boards(self) -> List[NCBoard]:
        """Returns all boards of the given user."""
        data = self.__send_get_request(ALL_USER_BOARDS_URL)
        return NCBoard.from_json(data, True)

    def board_by_id(self, board_id: int) -> NCBaseBoard:
        """Returns a board by a given board id."""
        data = self.__send_get_request(
            SINGLE_BOARD_URL.format(board_id=board_id))
        return NCBaseBoard.from_json(data, False)

    def stacks_by_board(self, board_id: int) -> NCDeckStack:
        """Returns all stacks of a given board with the given id."""
        data = self.__send_get_request(
            ALL_STACKS_URL.format(board_id=board_id))
        print(NCDeckStack.from_json(data, True))

    def user_mail(self, name: str) -> str:
        """
        Returns a dictionary mapping the given user name to his/her
        mail address.
        """

    def __send_get_request(self, postfix: str) -> str:
        """
        Calls the DECK API with the given URL postfix and returns
        the answer as a string.
        """
        url = self.__deck_api_url(postfix)
        rqs = requests.get(
            url,
            headers=self.__request_header(),
            auth=(self.user, self.password))
        return rqs.text

    def __deck_api_url(self, postfix: str) -> str:
        """Returns the Deck API URL with a given postfix."""
        return "{}/{}/{}".format(self.base_url, DECK_APP_URL, postfix)

    def __request_header(self) -> dict[str, str]:
        """Retruns the request header for all Deck API calls."""
        return {
            "OCS-APIRequest": "true",
            "Content-Type": "application/json",
        }

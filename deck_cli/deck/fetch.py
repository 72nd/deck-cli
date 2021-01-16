"""
Fetch abstracts all calls to the Nextcloud and Deck API.
"""

import xml.etree.ElementTree as ET
from typing import List

from deck_cli.deck.models import NCBoard, NCBaseBoard, NCDeckStack

import requests

DECK_APP_URL = "apps/deck/api/v1.0"
USER_DETAILS_URL = "ocs/v1.php/cloud/users/{user_uuid}"
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
        data = self.__send_get_request(
            self.__deck_api_url(ALL_USER_BOARDS_URL))
        return NCBoard.from_json(data, True)

    def board_by_id(self, board_id: int) -> NCBaseBoard:
        """Returns a board by a given board id."""
        data = self.__send_get_request(
            self.__deck_api_url(SINGLE_BOARD_URL.format(board_id=board_id)))
        return NCBaseBoard.from_json(data, False)

    def stacks_by_board(self, board_id: int) -> NCDeckStack:
        """Returns all stacks of a given board with the given id."""
        data = self.__send_get_request(
            self.__deck_api_url(ALL_STACKS_URL.format(board_id=board_id)))
        print(NCDeckStack.from_json(data, True))

    def user_mail(self, name: str) -> str:
        """
        Returns a dictionary mapping the given user name to his/her
        mail address.
        """
        api_url = USER_DETAILS_URL.format(user_uuid=name)
        data = self.__send_get_request("{}/{}".format(self.base_url, api_url))
        root = ET.fromstring(data)
        return root.find("./data/email").text

    def __send_get_request(self, url: str) -> str:
        """
        Calls a Nextcloud/Deck API with the given URL and returns
        the answer as a string.
        """
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

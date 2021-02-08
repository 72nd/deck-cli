"""
Fetch abstracts all calls to the Nextcloud and Deck API.
"""

from collections.abc import Callable
import xml.etree.ElementTree as ET
from typing import List

from deck_cli.deck.models import NCBoard, NCBaseBoard, NCDeckStack, NCCardPost

import requests

DECK_APP_URL = "apps/deck/api/v1.0"
USER_DETAILS_URL = "ocs/v1.php/cloud/users/{user_uuid}"
ALL_USER_BOARDS_URL = "boards"
SINGLE_BOARD_URL = "boards/{board_id}"
ALL_STACKS_URL = "boards/{board_id}/stacks"
SINGLE_CARD_URL = "boards/{board_id}/stacks/{stack_id}/cards/{card_id}"
SINGLE_CARD_POST_URL = "boards/{board_id}/stacks/{stack_id}/cards"


ProgressCallback = Callable[[int, int, str], ]
"""
Called by the Fetch class before doing a request. Can be used to inform the
user about the progress. The following parameters are provided:
    1. The number of the current step.
    2. The total number of steps needed to complete the task. 0 if unknown.
    3. A short description of the task.
"""


class Fetch:
    """
    Contains all calls to the Nextcloud and Deck API.

    The progress_callback can be used to display a update to the user
    when doing multiple API calls at once.
    """
    base_url: str
    user: str
    password: str
    progress_callback: ProgressCallback

    def __init__(
        self,
        base_url: str,
        user: str,
        password: str,
        progress_callback: ProgressCallback = lambda *args: None
    ):
        self.base_url = base_url
        self.user = user
        self.password = password
        self.progress_callback = progress_callback

    def all_boards(self) -> List[NCBoard]:
        """Returns all boards for the given user."""
        self.progress_callback(1, 1, "requests overview over all boards")
        data = self.__send_get_request(
            self.__deck_api_url(ALL_USER_BOARDS_URL))
        return NCBoard.from_json(data, True)

    def all_boards_with_stacks(self) -> List[NCBoard]:
        """
        Returns all boards for the given user, fetches for all Boards their
        Stacks and inserts them into the resulting data structure.
        """
        self.progress_callback(1, 0, "requests overview over all boards")
        data = self.__send_get_request(
            self.__deck_api_url(ALL_USER_BOARDS_URL))
        boards = NCBoard.from_json(data, True)
        i: int = 1
        for board in boards:
            self.progress_callback(
                i, len(boards),
                "request stacks for {} board".format(board.title))
            board.stacks = self.stacks_by_board(board.board_id)
            i += 1
        return boards

    def board_by_id(self, board_id: int) -> NCBaseBoard:
        """Returns a board by a given board id."""
        data = self.__send_get_request(
            self.__deck_api_url(SINGLE_BOARD_URL.format(board_id=board_id)))
        return NCBaseBoard.from_json(data, False)

    def stacks_by_board(self, board_id: int) -> List[NCDeckStack]:
        """Returns all stacks of a given board with the given id."""
        data = self.__send_get_request(
            self.__deck_api_url(ALL_STACKS_URL.format(board_id=board_id)))
        return NCDeckStack.from_json(data, True)

    def user_mail(self, name: str) -> str:
        """
        Returns a dictionary mapping the given user name to his/her
        mail address.
        """
        api_url = USER_DETAILS_URL.format(user_uuid=name)
        data = self.__send_get_request("{}/{}".format(self.base_url, api_url))
        root = ET.fromstring(data)
        return root.find("./data/email").text

    def add_card(self, board_id: int, stack_id: int, card: NCCardPost):
        """Adds a given card to the Deck via the API."""
        api_url = self.__deck_api_url(
            SINGLE_CARD_POST_URL.format(
                board_id=board_id,
                stack_id=stack_id,
            )
        )
        print(api_url)
        self.__send_post_request(api_url, card.dumps())

    def __send_get_request(self, url: str) -> str:
        """
        Calls a Nextcloud/Deck API with the given URL and returns
        the answer as a string.
        """
        rqs = requests.get(
            url,
            headers=self.__request_header(),
            auth=(self.user, self.password)
        )
        return rqs.text

    def __send_post_request(self, url: str, data):
        """Send POST Request to the API with a given data body."""
        print(data) # <-- HERE, check Order
        rqs = requests.post(
            url,
            data=data,
            headers=self.__request_header(),
            auth=(self.user, self.password)
        )
        print(rqs.text)

    def __deck_api_url(self, postfix: str) -> str:
        """Returns the Deck API URL with a given postfix."""
        return "{}/{}/{}".format(self.base_url, DECK_APP_URL, postfix)

    def __request_header(self) -> dict[str, str]:
        """Retruns the request header for all Deck API calls."""
        return {
            "OCS-APIRequest": "true",
            "Content-Type": "application/json",
        }

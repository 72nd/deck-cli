"""
This module handles the interactive CLI interaction with Deck.
"""
from collections.abc import Callable
from datetime import datetime
from typing import Dict, List, Optional

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch
from deck_cli.deck.models import NCBoard, NCDeckStack, NCCardPost

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.validation import Validator, ValidationError


INPUT_DATEFORMAT = "%Y-%m-%d %H%M"
"""Input format used for datetime input."""


OnWaitCallback = Callable[[str], ]
"""Called when the user has to wait."""


class IBoards(Completer, Validator):
    """
    Handles the interactive interaction with Deck Boards. Also handles the
    caching to prevent unnecessary API calls during the same session.
    """
    boards: List[NCBoard]

    def __init__(self, fetch: Fetch, on_wait: OnWaitCallback):
        on_wait("Fetching Boards from server...")
        self.boards = fetch.all_boards()

    def select(self, session: PromptSession) -> NCBoard:
        """
        Queries the available Boards from the API and lets the user choose one.
        """
        selection = session.prompt(
            HTML("<SkyBlue><b>Board,</b> select a Board: </SkyBlue>"),
            completer=FuzzyCompleter(self),
            validator=self,
        )
        return self.__board_by_input(selection)

    def list(self):
        """Lists the available boards."""
        output = "\n".join(["<DarkGreen>- {}</DarkGreen>".format(x.title)
                            for x in self.boards])
        print_formatted_text(HTML(output))

    def __board_by_input(self, text: str) -> NCBoard:
        """Returns the Board by the input (NCBoard title)."""
        for board in self.boards:
            if board.title == text:
                return board
        raise KeyError("no Board for {} found".format(text))

    def get_completions(self, document, complete_event):
        """Implements the interactive completion for Boards."""
        for board in self.boards:
            yield Completion(board.title)

    def validate(self, document):
        """Implements input Validation for Boards."""
        if document.text in [x.title for x in self.boards]:
            return
        raise ValidationError(
            message="{} is not a valid Board".format(document.text)
        )


class IStacks(Completer, Validator):
    """
    Handles the interactive interaction with Deck Stacks. Also handles the
    caching to prevent unnecessary API calls during the same session.
    """
    stacks: Dict[int, List[NCDeckStack]] = {}
    __fetch: Fetch
    __on_wait = OnWaitCallback
    __current_stacks: Optional[List[NCDeckStack]] = None

    def __init__(self, fetch: Fetch, on_wait: OnWaitCallback):
        self.__fetch = fetch
        self.__on_wait = on_wait

    def select(self, board_id: int, session: PromptSession) -> NCBoard:
        """
        Queries the available Boards from the API and lets the user choose one.
        """
        self.__current_stacks = self.__stacks_by_board(board_id)
        selection = session.prompt(
            HTML(
                "<SkyBlue><b>Stack,</b> select a Stack for the Card: "
                "</SkyBlue>"
            ),
            completer=FuzzyCompleter(self),
            validator=self,
        )
        return self.__stack_by_input(board_id, selection)

    def list(self, board_id: int):
        self.__current_stacks = self.__stacks_by_board(board_id)
        """Lists the available stacks for a given board."""
        output = "\n".join(["<DarkGreen>- {}</DarkGreen>".format(x.title)
                            for x in self.__current_stacks])
        print_formatted_text(HTML(output))

    def __stacks_by_board(self, board_id: int) -> List[NCDeckStack]:
        """
        Returns the stacks for a given board id. Fetches them via the API
        if not present.
        """
        if board_id in self.stacks:
            return self.stacks[board_id]
        self.__on_wait("Fetching Stacks from server...")
        self.stacks[board_id] = self.__fetch.stacks_by_board(board_id)
        return self.__stacks_by_board(board_id)

    def __stack_by_input(self, board_id: int, text: str) -> NCDeckStack:
        """Returns a Stack by a given Board id and selection input."""
        stacks = self.__stacks_by_board(board_id)
        for stack in stacks:
            if stack.title == text:
                return stack
        raise KeyError("no Stack for {} found".format(text))

    def get_completions(self, document, complete_event):
        """Implements the interactive completion for Stacks."""
        for stack in self.__current_stacks:
            yield Completion(stack.title)

    def validate(self, document):
        """Implements input Validation for Stacks."""
        if document.text in [x.title for x in self.__current_stacks]:
            return
        raise ValidationError(
            message="{} is not a valid Stack in current Board".format(
                document.text
            )
        )


class IUsers(Completer, Validator):
    """
    Handles the interactive interaction with the Nextcloud Users. Also handles
    the caching to prevent unnecessary API calls during the same session.
    """
    users: List[str]

    def __init__(self, fetch: Fetch, on_wait: OnWaitCallback):
        on_wait("Fetching Users from server...")
        self.users = fetch.user_ids()

    def select(self, session: PromptSession) -> List[str]:
        """Let the user select one or more User to assign the Card to."""
        rsl: List[str] = []
        while True:
            selection = session.prompt(
                HTML(
                    "<SkyBlue><b>Assigned user,</b> empty for none/no "
                    "additional: </SkyBlue>"
                ),
                completer=FuzzyCompleter(self),
                validator=self,
            )
            if selection == "":
                break
            rsl.append(selection)
        return rsl

    def list(self):
        """Lists the available Users."""
        output = ", ".join(self.users)
        print_formatted_text(HTML(output))

    def get_completions(self, document, complete_event):
        """Implements the interactive completion for Users."""
        for user in self.users:
            yield Completion(user)

    def validate(self, document):
        """Implements input Validation for Users."""
        if document.text != "" and document.text in self.users:
            return
        raise ValidationError(
            message="{} is not a valid User".format(document.text)
        )


class TitleValidator(Validator):
    """
    A Card title is not allowed to be empty and is limited to 255 characters.
    """

    def validate(self, document):
        if len(document.text) > 255:
            raise ValidationError(
                message="Title length cannot exceed 255 characters"
            )
        if document.text == "":
            raise ValidationError(message="Title is not allowed to be empty")


class InputDateValidator(Validator):
    """Validates the input against the datetime input format."""

    def validate(self, document):
        if document.text == "":
            return
        try:
            datetime.strptime(document.text, INPUT_DATEFORMAT)
        except ValueError:
            raise ValidationError(
                message="date format has to be YYYY-MM-DD HHMM"
            )


class DummyValidator(Validator):
    """Validates all input as valid."""

    def validate(self, document):
        pass


class Interactive:
    """
    Handles the interactive interaction with Deck via the CLI.
    """
    boards: IBoards
    stacks: IStacks
    __session: PromptSession

    def __init__(self, config: Config):
        self.fetch = Fetch(
            config.url,
            config.user,
            config.password,
        )
        self.__session = PromptSession()
        self.boards = IBoards(self.fetch, self.__on_wait)
        self.stacks = IStacks(self.fetch, self.__on_wait)

    def add(self):
        """Interactively adds a new card to the Deck."""
        self.fetch.user_ids()
        title = self.__session.prompt(
            HTML("<SkyBlue><b>Title,</b> enter the Card title: </SkyBlue>"),
            validator=TitleValidator()
        )
        description = self.__session.prompt(
            HTML(
                "<SkyBlue><b>Description,</b> enter a (optional) "
                "description: </SkyBlue>"
            ),
            validator=DummyValidator()
        )
        if description == "":
            description = None
        self.boards.list()
        board = self.boards.select(self.__session)
        self.stacks.list(board.board_id)
        stack = self.stacks.select(board.board_id, self.__session)
        duedate = self.__session.prompt(
            HTML(
                "<SkyBlue><b>Due Date,</b> enter a (optional) "
                "due-date: </SkyBlue>"
            ),
            validator=InputDateValidator(),
        )
        if duedate != "":
            duedate = datetime.strptime(duedate, INPUT_DATEFORMAT)
        else:
            duedate = None
        data = NCCardPost(
            title=title,
            description=description,
            duedate=duedate
        )
        self.fetch.add_card(board.board_id, stack.stack_id, data)

    def __on_wait(self, msg: str):
        """Output informing the user about a ongoing request."""
        print_formatted_text(HTML("<Gray>{}</Gray>".format(msg)))

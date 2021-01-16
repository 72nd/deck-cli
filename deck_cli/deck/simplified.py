"""
This module contains a simplified version of the API result
optimized for further processing and omitting most of the
redundancy.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from deck_cli.deck.models import NCBoard, NCDeckStack, NCDeckCard
from deck_cli.deck.models import NCDeckAssignedUser


@dataclass
class User:
    """A Deck user."""
    username: str
    full_name: str

    @classmethod
    def from_nc_assigned_user(cls, user: NCDeckAssignedUser) -> 'User':
        """Returns a new User instance based on a Deck assigned User."""
        return User(
            username=user.participant.uid,
            full_name=user.participant.display_name,
        )


@dataclass
class UserWithCards(User):
    """
    A User representation containing all cards for the given User. This is a
    helper-class especially useful for creating reports as such documents are
    often ordered per User.
    """


class CardState(Enum):
    """Describes the state of a task. Can be Backlog, In Progress, or Done."""
    BACKLOG = 0
    IN_PROGRESS = 1
    DONE = 2


@ dataclass
class Card:
    """A Deck Card."""
    identifier: int
    name: str
    description: str
    labels: List[str]
    assigned_users: List[User]
    duedate: Optional[datetime]
    state: Optional[CardState]
    archived: bool

    @ classmethod
    def from_nc_card(
        cls,
        card: NCDeckCard,
        state: Optional[CardState]
    ) -> 'Card':
        """Returns a new instance of Card based on the given Deck Card."""
        return Card(
            identifier=card.card_id,
            name=card.title,
            description=card.description,
            labels=[x.title for x in card.labels],
            assigned_users=[User.from_nc_assigned_user(
                x) for x in card.assigned_users],
            duedate=card.duedate,
            state=state,
            archived=card.archived,
        )


@ dataclass
class Stack:
    """A Deck Stack containing Cards."""
    identifier: int
    name: str
    cards: List[Card]

    @ classmethod
    def from_nc_stack(
        cls,
        stack: NCDeckStack,
        backlog_stacks: List[str] = [],
        progress_stacks: List[str] = [],
        done_stacks: List[str] = [],
    ) -> 'Stack':
        """Returns a new Stack instance based on a Nextcloud Stack."""
        state: Optional[CardState] = None
        if stack.title in backlog_stacks:
            state = CardState.BACKLOG
        elif stack.title in progress_stacks:
            state = CardState.IN_PROGRESS
        elif stack.title in done_stacks:
            state = CardState.DONE

        cards: List[Card] = []
        if stack.cards is not None:
            cards = [Card.from_nc_card(x, state) for x in stack.cards]

        return Stack(
            identifier=stack.stack_id,
            name=stack.title,
            cards=cards,
        )


@dataclass
class Board:
    """A Deck Board."""
    identifier: int
    name: str
    stacks: List[Stack]

    @ classmethod
    def from_nc_board(
        cls,
        board: NCBoard,
        backlog_stacks: List[str] = [],
        progress_stacks: List[str] = [],
        done_stacks: List[str] = [],
    ) -> 'Board':
        """Returns a new Board instance based on a NCBoard."""
        return Board(
            identifier=board.board_id,
            name=board.title,
            stacks=[Stack.from_nc_stack(
                x, backlog_stacks=backlog_stacks,
                progress_stacks=progress_stacks,
                done_stacks=done_stacks)
                for x in board.stacks]
        )


@ dataclass
class Deck:
    """All Boards of a deck combined. Also contains the users."""
    users: List[User]

    @ classmethod
    def from_nc_boards(
            cls,
            boards: List[NCBoard],
            backlog_stacks: List[str],
            progress_stacks: List[str],
            done_stacks: List[str]
    ) -> 'Deck':
        """Returns a new Deck instance from a list of NCBoards."""
        return [Board.from_nc_board(
            x, backlog_stacks, progress_stacks, done_stacks) for x in boards]

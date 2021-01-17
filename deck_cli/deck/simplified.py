"""
This module contains a simplified version of the API result
optimized for further processing and omitting most of the
redundancy.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from itertools import chain
from typing import Dict, List, Optional

from deck_cli.deck.models import NCBoard, NCDeckStack, NCDeckCard
from deck_cli.deck.models import NCDeckUser, NCDeckAssignedUser


@dataclass
class User:
    """A Deck user."""
    username: str
    full_name: str

    @classmethod
    def from_nc_deck_user(cls, user: NCDeckUser) -> 'User':
        """Returns a new User instance based on a Deck User."""
        return User(
            username=user.uid,
            full_name=user.display_name,
        )

    @classmethod
    def from_nc_assigned_user(cls, user: NCDeckAssignedUser) -> 'User':
        """Returns a new User instance based on a Deck assigned User."""
        return User(
            username=user.participant.uid,
            full_name=user.participant.display_name,
        )

    def __eq__(self, o) -> bool:
        if not isinstance(o, User):
            return False
        return self.username == o.username and self.full_name == self.full_name

    def __hash__(self):
        return hash((self.username, self.full_name))


class CardState(Enum):
    """Describes the state of a task. Can be Backlog, In Progress, or Done."""
    BACKLOG = 0
    IN_PROGRESS = 1
    DONE = 2


@dataclass
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
    board_name: str
    stack_name: str

    @ classmethod
    def from_nc_card(
        cls,
        card: NCDeckCard,
        state: Optional[CardState],
        board_name: str,
        stack_name: str
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
            board_name=board_name,
            stack_name=stack_name,
        )


@dataclass
class Stack:
    """A Deck Stack containing Cards."""
    identifier: int
    name: str
    cards: List[Card]

    @classmethod
    def from_nc_stack(
        cls,
        stack: NCDeckStack,
        board_name: str,
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
            cards = [Card.from_nc_card(
                x, state, board_name, stack.title) for x in stack.cards]

        return Stack(
            identifier=stack.stack_id,
            name=stack.title,
            cards=cards,
        )

    def assigned_users(self) -> List[User]:
        """Returns all Users with Tasks assigned in this Stack."""
        rsl: List[User] = []
        for card in self.cards:
            rsl = rsl + card.assigned_users
        return list(set(rsl))


@dataclass
class Board:
    """A Deck Board."""
    identifier: int
    name: str
    stacks: List[Stack]

    @classmethod
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
                x,
                board.title,
                backlog_stacks=backlog_stacks,
                progress_stacks=progress_stacks,
                done_stacks=done_stacks)
                for x in board.stacks]
        )

    def assigned_users(self) -> List[User]:
        """Returns all Users with Tasks assigned in this Board."""
        rsl: List[User] = []
        for stack in self.stacks:
            rsl = rsl + stack.assigned_users()
        return list(set(rsl))

    def cards(self) -> List[Card]:
        """Returns a list of all Cards of this board."""
        return list(chain.from_iterable([x.cards for x in self.stacks]))


@dataclass
class Deck:
    """All Boards of a deck combined. Also contains the users."""
    users: List[User]
    boards: List[Board]

    @classmethod
    def from_nc_boards(
            cls,
            boards: List[NCBoard],
            backlog_stacks: List[str],
            progress_stacks: List[str],
            done_stacks: List[str]
    ) -> 'Deck':
        """Returns a new Deck instance from a list of NCBoards."""
        boards = [Board.from_nc_board(
            x,
            backlog_stacks,
            progress_stacks,
            done_stacks) for x in boards
        ]

        users: List[User] = []
        for board in boards:
            users = users + board.assigned_users()

        return Deck(
            users=list(set(users)),
            boards=boards,
        )

    def cards(self) -> List[Card]:
        """Returns a list of all Cards in all Boards."""
        return list(chain.from_iterable([x.cards() for x in self.boards]))

    def overdue_cards(self) -> List[Card]:
        """Returns all Cards which are overdue and not in a done Stack."""
        cards = self.cards()
        now = datetime.now(tz=timezone.utc)
        return [card for card in cards if card.duedate
                is not None and card.duedate < now]


@dataclass
class UserWithCards(User):
    """
    A User representation containing all cards for the given User. The cards
    are sorted by their state in differen lists. This is a helper-class
    especially useful for creating reports as such documents are often ordered
    per User.
    """
    backlog_cards: List[Card]
    progress_cards: List[Card]
    done_cards: List[Card]
    other_cards: List[Card]

    def __init__(self, user: User) -> 'UserWithCards':
        self.username = user.username
        self.full_name = user.full_name
        self.backlog_cards = []
        self.progress_cards = []
        self.done_cards = []
        self.other_cards = []

    @classmethod
    def from_deck(cls, deck: Deck) -> List['UserWithCards']:
        """
        Returns a list of UserWithCards based on a (simplified) Deck object.
        """
        rsl: Dict[str, 'UserWithCards'] = {}
        for user in deck.users:
            rsl[user.username] = UserWithCards(user)

        cards = deck.cards()
        for card in cards:
            for usr in card.assigned_users:
                if card.state == CardState.BACKLOG:
                    rsl[usr.username].backlog_cards.append(card)
                elif card.state == CardState.IN_PROGRESS:
                    rsl[usr.username].progress_cards.append(card)
                elif card.state == CardState.DONE:
                    rsl[usr.username].done_cards.append(card)
                else:
                    rsl[usr.username].other_cards.append(card)
        return list(rsl.values())

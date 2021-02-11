"""
Describes the data structure of the get-all-boards API call.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
import json
from typing import List, Optional, Any, Union

from marshmallow import post_dump, pre_load
import marshmallow_dataclass


class DeckException(Exception):
    """Catches Nextcloud API errors."""

    def __init__(self, raw: str):
        data = json.loads(raw)
        Exception.__init__(self, data["message"])


@ dataclass
class Base:
    """
    The base class for all data classes. Provides the JSON
    unmarshaling for all classes.
    """

    @ classmethod
    def from_json(cls, raw: str, many=bool) -> 'NCBoard':
        """Reads the NCBoard from a JSON string."""
        data = json.loads(raw)
        if isinstance(data, dict) and "status" in data and data["status"] == 400:
            raise DeckException(raw)
        schema = marshmallow_dataclass.class_schema(cls)()
        return schema.loads(raw, many=many)


@ dataclass
class NCDeckUser:
    """The user in Nextcloud Deck."""
    primary_key: str = field(metadata=dict(data_key="primaryKey"))
    uid: str
    display_name: str = field(metadata=dict(data_key="displayname"))
    user_type: int = field(metadata=dict(data_key="type"))


@ dataclass
class NCDeckAssignedUser(Base):
    """A user which is assigned to a Card."""
    user_id: int = field(metadata=dict(data_key="id"))
    participant: NCDeckUser
    card_id: int = field(metadata=dict(data_key="cardId"))
    assignment_type: int = field(metadata=dict(data_key="type"))


@ dataclass
class NCDeckLabel:
    """Labels are used to tag cards or boards."""
    title: str
    color: str
    board_id: int = field(metadata=dict(data_key="boardId"))
    card_id: Optional[int] = field(metadata=dict(data_key="cardId"))
    last_modified: datetime.datetime = field(
        metadata=dict(data_key="lastModified"))
    label_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))

    @ pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        _func_on_dict(data, _timestamp_to_optional_date,
                      ["lastModified"])
        return data


@ dataclass
class NCDeckSharedEntity:
    """Entity a Deck resource was shared (also known as acl)."""
    participant: NCDeckUser
    entity_type: int = field(metadata=dict(data_key="type"))
    board_id: int = field(metadata=dict(data_key="boardId"))
    permission_edit: bool = field(metadata=dict(data_key="permissionEdit"))
    permission_share: bool = field(metadata=dict(data_key="permissionShare"))
    permission_manage: bool = field(metadata=dict(data_key="permissionManage"))
    owner: bool
    entity_id: int = field(metadata=dict(data_key="id"))


@ dataclass
class NCDeckPermissions:
    """Describes the permission a certain entity can have over a resource."""
    permission_read: bool = field(metadata=dict(data_key="PERMISSION_READ"))
    permission_edit: bool = field(metadata=dict(data_key="PERMISSION_EDIT"))
    permission_manage: bool = field(
        metadata=dict(data_key="PERMISSION_MANAGE"))
    permission_share: bool = field(metadata=dict(data_key="PERMISSION_SHARE"))


@ dataclass
class NCDeckCard(Base):
    """A single card of the Deck. Typically represents a task."""
    title: str
    description: str
    stack_id: int = field(metadata=dict(data_key="stackId"))
    card_type: str = field(metadata=dict(data_key="type"))
    last_modified: Optional[datetime.datetime] = field(
        metadata=dict(data_key="lastModified"))
    last_editor: Any = field(metadata=dict(data_key="lastEditor"))
    created_at: Optional[datetime.datetime] = field(
        metadata=dict(data_key="createdAt"))
    labels: Optional[List[NCDeckLabel]]
    assigned_users: Optional[List[NCDeckAssignedUser]] = field(
        metadata=dict(data_key="assignedUsers"))
    attachments: Any
    attachment_count: Optional[int] = field(
        metadata=dict(data_key="attachmentCount"))
    owner: Union[str, NCDeckUser]
    order: int
    archived: bool
    duedate: Optional[datetime.datetime]
    deleted_at: Optional[datetime.datetime] = field(
        metadata=dict(data_key="deletedAt"))
    comments_unread: int = field(metadata=dict(data_key="commentsUnread"))
    card_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))
    overdue: int

    @ pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        _func_on_dict(data, _timestamp_to_optional_date,
                      ["deletedAt", "lastModified", "createdAt"])
        return data


@ dataclass
class NCDeckBoardSettings:
    """The settings of a Deck board."""
    notify_due: str = field(metadata=dict(data_key="notify-due"))
    calendar: bool


@ dataclass
class NCDeckStack(Base):
    """A Stack of a Deck Board."""
    title: str
    board_id: int = field(metadata=dict(data_key="boardId"))
    deleted_at: Optional[datetime.datetime] = field(
        metadata=dict(data_key="deletedAt"))
    last_modified: Optional[datetime.datetime] = field(
        metadata=dict(data_key="lastModified"))
    cards: Optional[List[NCDeckCard]]
    order: int
    stack_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))

    @ pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        _func_on_dict(data, _timestamp_to_optional_date,
                      ["deletedAt", "lastModified"])
        return data


@ dataclass
class NCBaseBoard(Base):
    """
    A Deck Board as it's returned by the query for a specific board
    id. Get-all-boards at the other hand includes some extra fields
    as implemented by the NCBoard.
    """
    title: str
    owner: NCDeckUser
    color: str
    archived: bool
    labels: List[NCDeckLabel]
    shared_to: List[NCDeckSharedEntity] = field(metadata=dict(data_key="acl"))
    permissions: NCDeckPermissions
    users: List[NCDeckUser]
    stacks: List[NCDeckStack]
    deleted_at: Optional[datetime.datetime] = field(
        metadata=dict(data_key="deletedAt"))
    last_modified: Optional[datetime.datetime] = field(
        metadata=dict(data_key="lastModified"))
    settings: NCDeckBoardSettings
    board_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))

    @ pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        _func_on_dict(data, _timestamp_to_optional_date,
                      ["deletedAt", "lastModified"])
        return data


@ dataclass
class NCBoard(NCBaseBoard):
    """A Deck Board as returned by the get-all-boards API call."""
    shared: int


@ dataclass
class NCCardPost:
    """Post request body for a create new Card API call."""
    title: str
    type: str = "plain"
    order: int = 999
    description: Optional[str] = None
    duedate: Optional[datetime.datetime] = None

    class Meta:
        ordered = True

    @ post_dump
    def convert_date(self, data, **kwargs):
        """Converts the dates to ISO-8601."""
        if data["duedate"] is None:
            del data["duedate"]
        if data["description"] is None:
            del data["description"]
        return data

    def dumps(self):
        """Returns the content of the instance as JSON representation."""
        schema = marshmallow_dataclass.class_schema(NCCardPost)()
        return schema.dumps(self)


@ dataclass
class NCCardAssignUserRequest:
    """Put request body for assigning a User to a Deck card."""
    user_id: str = field(metadata=dict(data_key="userId"))

    def dumps(self):
        """Returns the content of the instance as JSON representation."""
        schema = marshmallow_dataclass.class_schema(NCCardAssignUserRequest)()
        return schema.dumps(self)


def _func_on_dict(
        data: dict[str, Any],
        func: Callable[[int], Any],
        keys: List[str]
) -> dict[str, Any]:
    """Applies the given function on all values with one of the given keys."""
    for key in data:
        if key not in keys:
            continue
        data[key] = func(data[key])
    return data


def _timestamp_to_date(value: int) -> datetime.datetime:
    """Converts a given unix timestamp to a datetime object."""
    return datetime.datetime.fromtimestamp(value)


def _timestamp_to_optional_date(value: int) -> Optional[str]:
    """
    Converts the the timestamp to a datetime obeject if the input
    value is > 0. This is helpful as the Deck API returns unset date's
    as 0 (example: deltedAt when a element isn't deleted.
    """
    if value < 1:
        return None
    # TODO: Remove this hack.
    return str(_timestamp_to_date(value))


def datetime_to_iso_8601(value: datetime) -> Optional[str]:
    """Formats a datetime to a ISO 8601 date string."""
    if not value:
        return None
    return value.isoformat()

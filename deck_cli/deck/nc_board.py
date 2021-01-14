"""
Describes the data structure of the get-all-boards API call.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
import datetime
from typing import List, Optional, Any

from marshmallow import pre_load, EXCLUDE
import marshmallow_dataclass


@dataclass
class NCDeckUser:
    """The user in Nextcloud Deck."""
    primary_key: str = field(metadata=dict(data_key="primaryKey"))
    uid: str
    display_name: str = field(metadata=dict(data_key="displayname"))
    user_type: int = field(metadata=dict(data_key="type"))


@dataclass
class NCDeckLabel:
    """Labels are used to tag cards or boards."""
    title: str
    color: str
    board_id: int = field(metadata=dict(data_key="boardId"))
    card_id: int = field(metadata=dict(data_key="cardId"))
    last_modified: datetime.datetime = field(
        metadata=dict(data_key="lastModified"))
    label_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))


@dataclass
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


@dataclass
class NCDeckPermissions:
    """Describes the permission a certain entity can have over a resource."""
    permission_read: bool = field(metadata=dict(data_key="PERMISSION_READ"))
    permission_edit: bool = field(metadata=dict(data_key="PERMISSION_EDIT"))
    permission_manage: bool = field(
        metadata=dict(data_key="PERMISSION_MANAGE"))
    permission_share: bool = field(metadata=dict(data_key="PERMISSION_SHARE"))


@dataclass
class NCDeckBoardSettings:
    """The settings of a Deck board."""
    notify_due: str = field(metadata=dict(data_key="notify-due"))
    calendar: bool


@dataclass
class NCBoard:
    """A Deck Board as returned by the get-all-boards API call."""
    title: str
    owner: NCDeckUser
    color: str
    archived: bool
    labels: List[NCDeckLabel]
    shared_to: List[NCDeckSharedEntity] = field(metadata=dict(data_key="acl"))
    permissions: NCDeckPermissions
    shared: int
    deleted_at: Optional[datetime.datetime] = field(
        metadata=dict(data_key="deletedAt"))
    last_modified: Optional[datetime.datetime] = field(
        metadata=dict(data_key="lastModified"))
    settings: NCDeckBoardSettings
    board_id: int = field(metadata=dict(data_key="id"))
    etag: str = field(metadata=dict(data_key="ETag"))

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        _func_on_dict(data, _timestamp_to_optional_date,
                      ["deletedAt", "lastModified"])
        return data

    @classmethod
    def from_json(cls, raw) -> 'NCBoard':
        """Reads the NCBoard from a JSON string."""
        schema = marshmallow_dataclass.class_schema(NCBoard)()
        return schema.loads(raw, many=True)


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
    rsl = datetime.datetime.fromtimestamp(value)
    print(rsl)
    return rsl


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

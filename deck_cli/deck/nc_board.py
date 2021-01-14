"""
Describes the data structure of the get-all-boards API call.
"""
from dataclasses import dataclass, field
import datetime
from typing import List, ClassVar, Type

from marshmallow import Schema, pre_load, EXCLUDE
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
    last_modified: datetime.date = field(
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
class NCBoard:
    """A Deck Board as returned by the get-all-boards API call."""
    title: str
    owner: NCDeckUser
    color: str
    archived: bool
    labels: List[NCDeckLabel]
    shared_to: List[NCDeckSharedEntity] = field(metadata=dict(data_key="acl"))
    # Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def convert_date(self, data, **kwargs):
        """Converts all Unix dates to normal python datetime objects."""
        return data

    @classmethod
    def from_json(cls, raw) -> 'NCBoard':
        """Reads the NCBoard from a JSON string."""
        schema = marshmallow_dataclass.class_schema(NCBoard)()
        # return NCBoard.Schema(many=True).loads(data)
        return schema.loads(raw, many=True)

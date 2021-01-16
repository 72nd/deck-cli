"""
Module handles all the configuration stuff.
"""
from dataclasses import dataclass, field
from typing import List, ClassVar, Type

from marshmallow import Schema
import marshmallow_dataclass
import yaml


@dataclass
class Config:
    """Config describes the configuration-file for the CLI application."""
    url: str = field(
        metadata=dict(
            description="Nextcloud URL",
            default="nc.example.com")
    )
    user: str = field(
        metadata=dict(
            description="Nextcloud user",
            default="usr")
    )
    password: str = field(
        metadata=dict(
            description="Nextcloud password",
            default="secret")
    )
    ignore_board: List[str] = field(
        metadata=dict(
            description="Name of boards to be ignored",
            default=["Personal"])
    )
    backlog_stacks: List[str] = field(
        metadata=dict(
            description="Name of stacks considered to be a backlog",
            default=["Backlog"])
    )
    progress_stacks: List[str] = field(
        metadata=dict(
            description="Stacks containing tasks in the progress",
            default=["In Progress"])
    )
    done_stacks: List[str] = field(
        metadata=dict(
            description="Stacks containing done tasks",
            default=["Done"])
    )
    mail_cache_path: str = field(
        metadata=dict(
            description="Path to mail-address cache",
            default="deck-cache.yaml",
        )
    )
    Schema: ClassVar[Type[Schema]] = Schema

    @classmethod
    def from_yaml(cls, raw: str) -> 'Config':
        """Loads the configuration from a given YAML string."""
        schema = marshmallow_dataclass.class_schema(Config)()
        data = yaml.load(raw, Loader=yaml.FullLoader)
        return schema.load(data)

    @classmethod
    def defaults(cls) -> 'Config':
        """Returns a new instance of the Config with the default values."""
        return Config(
            url="nc.example.com",
            user="usr",
            password="secret",
            ignore_board=["Personal"],
            backlog_stacks=["Backlog"],
            progress_stacks=["In Progress"],
            done_stacks=["Done"],
            mail_cache_path="check-cache.yaml"
        )

    def to_yaml(self) -> str:
        """Returns the config data-class as a YAML string."""
        #cfg = Config.Schema().dumps(self)
        schema = marshmallow_dataclass.class_schema(Config)()
        cfg = schema.dump(self)
        return yaml.dump(cfg)

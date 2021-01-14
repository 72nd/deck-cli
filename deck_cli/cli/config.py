"""
Module handles all the configuration stuff.
"""
from dataclasses import dataclass, field
from typing import List

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
    mail_cache_path: str = field(
        metadata=dict(
            description="Path to mail-address cache",
            default="deck-cache.yaml",
        )
    )

    def __init__(self) -> 'Config':
        pass

    @classmethod
    def load(cls, path: str) -> 'Config':
        with open(path, "r") as fil:
            raw = yaml.load(fil.read())
        schema = marshmallow_dataclass.class_schema(Config)
        return schema.load(raw)

    def to_yaml(self) -> str:
        """Returns the config data-class as a YAML string."""
        schema = marshmallow_dataclass.class_schema(Config)()
        cfg = schema.dump(self)
        return yaml.dump(cfg)

"""
Module handles all the configuration stuff.
"""
from dataclasses import dataclass, field

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

    def __init__(self):
        pass

    def to_yaml(self) -> str:
        """Returns the config data-class as a YAML string."""
        schema = marshmallow_dataclass.class_schema(Config)()
        cfg = schema.dump(self)
        return yaml.dump(cfg)

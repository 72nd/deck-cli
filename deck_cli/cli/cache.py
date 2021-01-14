"""
Manages the cache for the mail-addresses. To send notifications to
the users, the systems needs to now the mail addresses of them. As
this information is not part of the API response this information
has to be queried from the OSC (Nextcloud) API for each user individually.
To speed up this process the mail addresses get cached in a file.
"""
from dataclasses import dataclass, field

import marshmallow_dataclass
import yaml


@dataclass
class Cache:
    """The Mail-Address cache."""
    mails: dict[str, str] = field(
        metadata=dict(
            description="Maps the username to a mail-address")
    )
    internal_hash: str = field(
        metadata=dict(
            exclude=True)
    )

    @classmethod
    def open(cls, path: str) -> 'Cache':
        """Opens a cache YAML file. If no file exists an empty Cache
        is returned"""
        try:
            with open(path, "r") as fil:
                raw = yaml.load(fil.read())
            schema = marshmallow_dataclass.class_schema(Cache)
            rsl = schema.load(raw)
        except IOError:
            rsl = Cache()
        rsl.internal_hash = rsl.mails.hash()
        return rsl

    def save(self, path: str):
        """Saves the cache to a given path if the content has changed."""
        if self.internal_hash == self.mails.hash():
            return
        schema = marshmallow_dataclass.class_schema(Cache)
        cache = schema.dump(self)
        with open(path, "w") as fil:
            data = yaml.dump(cache)
            fil.write(data)

"""
Fetch API results and save them locally for further processing later.
"""

from deck_cli.cli.config import Config
from deck_cli.deck.fetch import Fetch, ProgressCallback
from deck_cli.deck.simplified import Deck

import click
import marshmallow_dataclass
import yaml


def deck_to_file(
    cfg: Config,
    path: click.File,
    on_progress: ProgressCallback
):
    """
    Fetch the current Deck (all Boards visible to the User) and writes them
    as a YAML file to the given path.
    """
    deck = Fetch(
        cfg.url,
        cfg.user,
        cfg.password,
        progress_callback=on_progress
    )
    deck = Deck.from_nc_boards(
        deck.all_boards_with_stacks(),
        cfg.backlog_stacks,
        cfg.progress_stacks,
        cfg.done_stacks
    )
    schema = marshmallow_dataclass.class_schema(Deck)()
    data = schema.dump(deck)
    path.write(yaml.dump(data))


def load_deck_from_file(path: click.File):
    """
    Loads a dumped Deck (all Boards visible to a given User) from the YAML file
    with the given path.
    """
    schema = marshmallow_dataclass.class_schema(Deck)()
    data = yaml.load(path.read(), Loader=yaml.FullLoader)
    return schema.load(data)

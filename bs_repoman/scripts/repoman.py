import click
import os
from pathlib import Path
from shutil import copytree
import sys
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger("bs_repoman")
logging.basicConfig(level=logging.INFO)


_BASE_PATH = Path(os.getcwd()).resolve()
_HOME_PATH = Path.home()
_CONFIG_PATH = _HOME_PATH / '.config' / 'bs_repoman'
_CACHE_PATH = _HOME_PATH / '.cache' / 'bs_repoman'


def ensure_path(name: str, path: Path) -> None:
    if not path.exists():
        logger.info("%s path does not exist, creating...", name)
        path.mkdir()
        logger.info("Created %s path @ %s", name, path)
        return
    logger.info("Detected %s path @ %s", name, path)


@click.group()
def cli():
    """Helps to eliminate repo boilerplate stuff."""
    ensure_path('config', _CONFIG_PATH)
    ensure_path('cache', _CACHE_PATH)


@cli.command()
def github_stuff():
    click.echo('Initializing github stuff.')

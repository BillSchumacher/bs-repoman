import click
import os
from pathlib import Path
from shutil import copytree
import sys
import logging
from typing import Optional, Tuple, List
from bs_pathutils import ensure_path

logger = logging.getLogger("bs_repoman")
logging.basicConfig(level=logging.INFO)


_BASE_PATH = Path(os.getcwd()).resolve()
_HOME_PATH = Path.home()
_CONFIG_PATH = _HOME_PATH / '.config' / 'bs_repoman'
_CACHE_PATH = _HOME_PATH / '.cache' / 'bs_repoman'


@click.group()
def cli():
    """Helps to eliminate repo boilerplate stuff."""
    logger.info("Starting bs_repoman...")
    ensure_path(_CACHE_PATH, 'cache')
    ensure_path(_CONFIG_PATH, 'config')


@cli.command()
@click.option('--language', default="python", help="Install github boilerplate.")
def install_github_template(language: str) -> None:
    click.echo('Initializing github issue templates.')
    _github_template_path = _CACHE_PATH / 'bs-repoman-github-templates'
    if not _github_template_path.exists():
        logger.info("Did not find repo at %s. Cloning bs-repoman-github-templates...", _github_template_path)
        os.system(f'git clone git@github.com:BillSchumacher/bs-repoman-github-templates.git {_github_template_path}')
        logger.info("Cloned bs-repoman-github-templates... to %s", _github_template_path)

    _github_template_path_all = _github_template_path / 'all'
    if language == "python":
        _github_template_path_specific = _github_template_path / 'python'
    else:
        raise NotImplementedError(f"Language {language} not implemented.")

    copytree(_github_template_path_all, _BASE_PATH, dirs_exist_ok=True)
    copytree(_github_template_path_specific, _BASE_PATH, dirs_exist_ok=True)
    logger.info("Copied github templates to %s", _BASE_PATH)

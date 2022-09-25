import click
import configparser
import os
from pathlib import Path
from shutil import copytree
import logging
from bs_pathutils import ensure_path
from contextvars import ContextVar


_config = ContextVar('config', default=None)
logger = logging.getLogger("bs_repoman")

_BASE_PATH = Path(os.getcwd()).resolve()
_HOME_PATH = Path.home()
_CONFIG_PATH = _HOME_PATH / '.config' / 'bs_repoman'
_CONFIG_FILE_PATH = _CONFIG_PATH / 'config.ini'
_CACHE_PATH = _HOME_PATH / '.cache' / 'bs_repoman'


# TODO: These lambdas are terrible, should probably make those functions and organize this better.
@click.group()
@click.option('--author', prompt='Your name please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['author'] if _config.get() else None)
@click.option('--author-email', prompt='Your email-address please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['author_email'] if _config.get() else None)
@click.option('--github-username', prompt='Your github username please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['github_username'] if _config.get() else None)
@click.option('--repo-name', default=lambda: _BASE_PATH.name)
@click.option('--debug/--no-debug', default=False)
@click.option('--update/--no-update', default=False)
@click.pass_context
def base_cli(ctx, author, author_email, github_username, repo_name, debug, update):
    """Helps to eliminate repo boilerplate stuff."""
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.info("Starting bs_repoman...")
    logger.debug("Debug mode is on")
    logger.debug("Author: %s", author)
    logger.debug("Author email: %s", author_email)
    logger.debug("Github username: %s", github_username)
    logger.debug("Repo name: %s", repo_name)

    ensure_path(_CACHE_PATH, 'cache')
    ensure_path(_CONFIG_PATH, 'config')
    ctx.obj['CONFIG'] = get_config()
    if not ctx.obj['CONFIG']:
        ctx.obj['CONFIG'] = create_default_config(author, author_email, github_username)
    ctx.obj['CONFIG']['DEFAULT']['author'] = author
    ctx.obj['CONFIG']['DEFAULT']['author_email'] = author_email
    ctx.obj['CONFIG']['DEFAULT']['github_username'] = github_username
    ctx.obj['REPO_NAME'] = repo_name
    ctx.obj['UPDATE'] = update
    write_config(ctx.obj['CONFIG'])


def cli():
    config = get_config()
    _config.set(config)
    base_cli(obj={})


def create_default_config(author, author_email, github_username):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'author': author,
        'author_email': author_email,
        'github_username': github_username
    }
    write_config(config)
    return config


def write_config(config):
    ensure_path(_CONFIG_PATH, 'config directory')
    with _CONFIG_FILE_PATH.open('w') as config_file:
        config.write(config_file)
    return config


def get_config():
    if _CONFIG_FILE_PATH.exists():
        config = configparser.ConfigParser()
        config.read(_CONFIG_FILE_PATH)
        return config


def get_files_from_path(path):
    path_str = str(path)
    glob = path.rglob('**/*.*')
    return [str(file_path).split(path_str)[1][1:] for file_path in glob]


def get_files_affected(path_all, path_specific):
    all_path_files = get_files_from_path(path_all)
    specific_path_files = get_files_from_path(path_specific)
    logger.debug("all template files: %s", all_path_files)
    logger.debug("specific template files: %s", specific_path_files)
    return all_path_files + specific_path_files


@base_cli.command()
@click.option('--language', default="python", help="Install github boilerplate.")
@click.pass_context
def install_github_template(ctx, language: str) -> None:
    click.echo('Initializing github template...')
    _github_template_path = _CACHE_PATH / 'bs-repoman-github-templates'
    if not _github_template_path.exists():
        logger.info("Did not find repo at %s. Cloning bs-repoman-github-templates...", _github_template_path)
        os.system(f'git clone git@github.com:BillSchumacher/bs-repoman-github-templates.git {_github_template_path}')
        logger.info("Cloned bs-repoman-github-templates... to %s", _github_template_path)
    if ctx.obj['UPDATE']:
        logger.info("Updating bs-repoman-github-templates...")
        os.system(f'cd {_github_template_path} && git pull')
        logger.info("Updated bs-repoman-github-templates... to %s", _github_template_path)
    _github_template_path_all = _github_template_path / 'all'
    if language == "python":
        _github_template_path_specific = _github_template_path / 'python'
    else:
        raise NotImplementedError(f"Language {language} not implemented.")

    copytree(_github_template_path_all, _BASE_PATH, dirs_exist_ok=True)
    copytree(_github_template_path_specific, _BASE_PATH, dirs_exist_ok=True)
    logger.info("Copied github templates to %s", _BASE_PATH)

    all_files = get_files_affected(_github_template_path_all, _github_template_path_specific)
    logger.debug("All files affected: %s", all_files)
    for file in all_files:
        current_file = _BASE_PATH / file
        if not current_file.is_file():
            continue
        logger.debug("Processing file: %s", current_file)
        with open(current_file, 'r') as f:
            content = f.read()
        content = content.replace('{{ author }}', ctx.obj['CONFIG']['DEFAULT']['author'])
        content = content.replace('{{ author_email }}', ctx.obj['CONFIG']['DEFAULT']['author_email'])
        content = content.replace('{{ github_username }}', ctx.obj['CONFIG']['DEFAULT']['github_username'])
        content = content.replace('{{ repo_name }}', ctx.obj['REPO_NAME'])
        with open(current_file, 'w') as f:
            f.write(content)
        logger.debug("Processed file: %s", current_file)
    logger.debug("Processed all files.")
    click.echo('Initialized github template!')

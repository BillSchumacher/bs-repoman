import click
import logging
from bs_pathutils import ensure_path
from contextvars import ContextVar

from bs_repoman.config import update_config, get_config, get_config_value
from bs_repoman.constants import BASE_PATH, CACHE_PATH, GITHUB_TEMPLATES_PATH_ALL
from bs_repoman.gh_templates import ensure_github_template, get_template_specific_path, get_files_affected, \
    process_template_files, copy_template_files
from bs_repoman.log import logger

_config = ContextVar('config', default=None)


@click.group()
@click.option('--author', prompt='Your name please', prompt_required=False,
              default=lambda: get_config_value(_config.get(), 'author'))
@click.option('--author-email', prompt='Your email-address please', prompt_required=False,
              default=lambda: get_config_value(_config.get(), 'author_email'))
@click.option('--github-username', prompt='Your github username please', prompt_required=False,
              default=lambda: get_config_value(_config.get(), 'github_username'))
@click.option('--repo-name', default=lambda: BASE_PATH.name)
@click.option('--debug/--no-debug', default=False)
@click.option('--update/--no-update', default=False)
@click.pass_context
def base_cli(ctx, author, author_email, github_username, repo_name, debug, update):
    """Helps to eliminate repo boilerplate stuff."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    logger.info("Starting bs_repoman...")
    log_args(author, author_email, github_username, repo_name, update)
    ensure_path(CACHE_PATH, 'cache')
    update_config(ctx, author, author_email, github_username, repo_name, update)


def log_args(author, author_email, github_username, repo_name, update):
    logger.debug("Debug mode is on")
    logger.debug("Author: %s", author)
    logger.debug("Author email: %s", author_email)
    logger.debug("Github username: %s", github_username)
    logger.debug("Repo name: %s", repo_name)
    logger.debug("Update: %s", update)


def cli():
    config = get_config()
    _config.set(config)
    base_cli(obj={})


@base_cli.command()
@click.option('--language', default="python", help="Install github boilerplate.")
@click.pass_context
def install_github_template(ctx, language: str) -> None:
    click.echo('Initializing github template...')
    ensure_github_template(ctx)
    github_template_path_specific = get_template_specific_path(language)
    copy_template_files(github_template_path_specific)
    all_files = get_files_affected(GITHUB_TEMPLATES_PATH_ALL, github_template_path_specific)
    logger.debug("All files affected: %s", all_files)
    process_template_files(all_files, ctx)
    click.echo('Initialized github template!')

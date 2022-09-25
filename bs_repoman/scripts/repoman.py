import click
import os
from shutil import copytree
import logging
from bs_pathutils import ensure_path
from contextvars import ContextVar

from bs_repoman.config import update_config, get_config
from bs_repoman.constants import BASE_PATH, CACHE_PATH, GITHUB_TEMPLATES_PATH, GITHUB_TEMPLATES_PATH_ALL

_config = ContextVar('config', default=None)
logger = logging.getLogger("bs_repoman")


# TODO: These lambdas are terrible, should probably make those functions and organize this better.
@click.group()
@click.option('--author', prompt='Your name please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['author'] if _config.get() else None)
@click.option('--author-email', prompt='Your email-address please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['author_email'] if _config.get() else None)
@click.option('--github-username', prompt='Your github username please', prompt_required=False,
              default=lambda: _config.get()['DEFAULT']['github_username'] if _config.get() else None)
@click.option('--repo-name', default=lambda: BASE_PATH.name)
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

    ensure_path(CACHE_PATH, 'cache')
    update_config(ctx, author, author_email, github_username, repo_name, update)


def cli():
    config = get_config()
    _config.set(config)
    base_cli(obj={})


def get_files_from_path(path):
    path_str = str(path)
    glob = path.rglob('**/*')
    return [str(file_path).split(path_str)[1][1:] for file_path in glob]


def get_files_affected(path_all, path_specific):
    all_path_files = get_files_from_path(path_all)
    specific_path_files = get_files_from_path(path_specific)
    logger.debug("all template files: %s", all_path_files)
    logger.debug("specific template files: %s", specific_path_files)
    return all_path_files + specific_path_files


def ensure_github_template(ctx):
    if not GITHUB_TEMPLATES_PATH.exists():
        logger.info("Did not find repo at %s. Cloning bs-repoman-github-templates...", GITHUB_TEMPLATES_PATH)
        os.system(f'git clone git@github.com:BillSchumacher/bs-repoman-github-templates.git {GITHUB_TEMPLATES_PATH}')
        logger.info("Cloned bs-repoman-github-templates... to %s", GITHUB_TEMPLATES_PATH)
    if ctx.obj['UPDATE']:
        logger.info("Updating bs-repoman-github-templates...")
        os.system(f'cd {GITHUB_TEMPLATES_PATH} && git pull')
        logger.info("Updated bs-repoman-github-templates...")


@base_cli.command()
@click.option('--language', default="python", help="Install github boilerplate.")
@click.pass_context
def install_github_template(ctx, language: str) -> None:
    click.echo('Initializing github template...')
    ensure_github_template(ctx)
    if language == "python":
        _github_template_path_specific = GITHUB_TEMPLATES_PATH / 'python'
    else:
        raise NotImplementedError(f"Language {language} not implemented.")

    copytree(GITHUB_TEMPLATES_PATH_ALL, BASE_PATH, dirs_exist_ok=True)
    copytree(_github_template_path_specific, BASE_PATH, dirs_exist_ok=True)
    logger.info("Copied github templates to %s", BASE_PATH)

    all_files = get_files_affected(GITHUB_TEMPLATES_PATH_ALL, _github_template_path_specific)
    logger.debug("All files affected: %s", all_files)
    process_template_files(all_files, ctx)
    click.echo('Initialized github template!')


def process_template_files(files, ctx):
    logger.debug("Replace template variables...")
    for f in files:
        current_file = BASE_PATH / f
        if not current_file.is_file():
            continue
        logger.debug("Processing file: %s", current_file)
        replace_variables(current_file, ctx)
        logger.debug("Processed file: %s", current_file)
    logger.debug("Processed all files.")


def replace_variables(current_file, ctx):
    with open(current_file, 'r') as f:
        content = f.read()
    content = content.replace('{{ author }}', ctx.obj['CONFIG']['DEFAULT']['author'])
    content = content.replace('{{ author_email }}', ctx.obj['CONFIG']['DEFAULT']['author_email'])
    content = content.replace('{{ github_username }}', ctx.obj['CONFIG']['DEFAULT']['github_username'])
    content = content.replace('{{ repo_name }}', ctx.obj['REPO_NAME'])
    with open(current_file, 'w') as f:
        f.write(content)

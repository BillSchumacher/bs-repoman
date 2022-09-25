import configparser

from bs_pathutils import ensure_path
from bs_repoman.constants import CONFIG_PATH, CONFIG_FILE_PATH


def get_config_value(config, key):
    return config['DEFAULT'][key] if config else None


def update_config(ctx, author, author_email, github_username, repo_name, update):
    ensure_path(CONFIG_PATH, 'config')
    ctx.obj['CONFIG'] = get_config()
    if not ctx.obj['CONFIG']:
        ctx.obj['CONFIG'] = create_default_config(author, author_email, github_username)
    ctx.obj['CONFIG']['DEFAULT']['author'] = author
    ctx.obj['CONFIG']['DEFAULT']['author_email'] = author_email
    ctx.obj['CONFIG']['DEFAULT']['github_username'] = github_username
    ctx.obj['REPO_NAME'] = repo_name
    ctx.obj['UPDATE'] = update
    write_config(ctx.obj['CONFIG'])


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
    ensure_path(CONFIG_PATH, 'config directory')
    with CONFIG_FILE_PATH.open('w') as config_file:
        config.write(config_file)
    return config


def get_config():
    if CONFIG_FILE_PATH.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config


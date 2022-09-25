import os
from shutil import copytree

from bs_repoman.constants import GITHUB_TEMPLATES_PATH, BASE_PATH, GITHUB_TEMPLATES_PATH_ALL
from bs_repoman.log import logger


def copy_template_files(specific_path):
    copytree(GITHUB_TEMPLATES_PATH_ALL, BASE_PATH, dirs_exist_ok=True)
    copytree(specific_path, BASE_PATH, dirs_exist_ok=True)
    logger.info("Copied github templates to %s", BASE_PATH)


def ensure_github_template(ctx):
    if not GITHUB_TEMPLATES_PATH.exists():
        logger.info("Did not find repo at %s. Cloning bs-repoman-github-templates...", GITHUB_TEMPLATES_PATH)
        os.system(f'git clone git@github.com:BillSchumacher/bs-repoman-github-templates.git {GITHUB_TEMPLATES_PATH}')
        logger.info("Cloned bs-repoman-github-templates... to %s", GITHUB_TEMPLATES_PATH)
    if ctx.obj['UPDATE']:
        logger.info("Updating bs-repoman-github-templates...")
        os.system(f'cd {GITHUB_TEMPLATES_PATH} && git pull')
        logger.info("Updated bs-repoman-github-templates...")


def get_files_affected(path_all, path_specific):
    all_path_files = get_files_from_path(path_all)
    specific_path_files = get_files_from_path(path_specific)
    logger.debug("all template files: %s", all_path_files)
    logger.debug("specific template files: %s", specific_path_files)
    return all_path_files + specific_path_files


def get_files_from_path(path):
    path_str = str(path)
    glob = path.rglob('**/*')
    return [str(file_path).split(path_str)[1][1:] for file_path in glob]


def get_template_specific_path(language):
    if language == "python":
        _github_template_path_specific = GITHUB_TEMPLATES_PATH / 'python'
    else:
        raise NotImplementedError(f"Language {language} not implemented.")
    return _github_template_path_specific


def process_template_files(files, ctx):
    logger.debug("Replace template variables...")
    for path in files:
        current_file = BASE_PATH / path
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

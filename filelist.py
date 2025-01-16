#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from urllib.parse import quote

EXCLUDE_DIRS = ['.git', 'docs', '.vscode', '.circleci', 'site']
README_MD = ['README.md', 'readme.md', 'index.md']
TXT_EXTS = ['md', 'txt']
URL_PREFIX = 'https://github.com/NjustLib/NjustDocs/blob/main/'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_readme(root, readme_files):
    for readme in readme_files:
        readme_path = os.path.join(root, readme)
        if os.path.isfile(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as file:
                    return file.read() + '\n\n', readme_path
            except IOError as e:
                logging.error(f"Error reading {readme_path}: {e}")
    return '', ''

def list_files(course: str):
    filelist_texts = '# 文件列表\n\n'
    readme_path = ''
    readme_content, readme_path = read_readme(course, README_MD)
    if readme_content:
        filelist_texts = readme_content + filelist_texts
    for root, dirs, files in os.walk(course):
        files.sort()
        level = root.replace(course, '').count(os.sep)
        indent = ' ' * 4 * level
        filelist_texts += '{}- {}\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in README_MD:
                file_url = URL_PREFIX + quote(f'{root}/{f}'.replace(os.sep, '/'))
                filelist_texts += '{}- [{}]({})\n'.format(subindent, f, file_url)
            elif root == course and readme_path == '':
                readme_path = f'{root}/{f}'
    return filelist_texts, readme_path

def generate_md(course: str, filelist_texts: str, readme_path: str):
    final_texts = [filelist_texts]
    if readme_path and not filelist_texts.startswith(read_readme(course, README_MD)[0]):
        try:
            with open(readme_path, 'r', encoding='utf-8') as file:
                final_texts = file.readlines() + final_texts
        except IOError as e:
            logging.error(f"Error reading {readme_path}: {e}")
            return
    try:
        with open(f'docs/{course}.md', 'w', encoding='utf-8') as file:
            file.writelines(final_texts)
    except IOError as e:
        logging.error(f"Error writing to docs/{course}.md: {e}")

def update_mkdocs_yml(courses):
    mkdocs_yml = 'mkdocs.yml'
    nav_entries = ['  - 课程资料:\n']
    for course in courses:
        nav_entries.append(f'    - {course}: {course}.md\n')
    try:
        with open(mkdocs_yml, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        nav_index = next(i for i, line in enumerate(lines) if line.strip() == 'nav:')
        nav_end_index = next((i for i, line in enumerate(lines[nav_index+1:], nav_index+1) if not line.startswith('  - ')), len(lines))
        
        lines = lines[:nav_index+1] + nav_entries + lines[nav_end_index:]
        
        with open(mkdocs_yml, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    except IOError as e:
        logging.error(f"Error updating mkdocs.yml: {e}")

if __name__ == '__main__':
    if not os.path.isdir('docs'):
        os.mkdir('docs')

    courses = list(filter(lambda x: os.path.isdir(x) and (x not in EXCLUDE_DIRS), os.listdir('.')))  # list courses

    for course in courses:
        logging.info(f'Processing course: {course}')
        filelist_texts, readme_path = list_files(course)
        generate_md(course, filelist_texts, readme_path)

    update_mkdocs_yml(courses)

    try:
        with open('README.md', 'r', encoding='utf-8') as file:
            mainreadme_lines = file.readlines()
        with open('docs/index.md', 'w', encoding='utf-8') as file:
            file.writelines(mainreadme_lines)
    except IOError as e:
        logging.error(f"Error processing main README.md: {e}")

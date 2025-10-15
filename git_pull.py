#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import traceback
from loguru import logger
from pathlib import Path

args = None
projects = ['Test_Big1', 'Test_Big2']

def execute_cmd(command):
    command_line = " ".join(command)
    logger.debug(command_line)

    process = subprocess.Popen(
        command_line,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        text = True,
        bufsize = 1,
        shell = True
    )

    output = []
    for line in process.stdout:
        line_without_end = line.rstrip('\n')
        print(line_without_end)
        output.append(line_without_end)

    process.wait()

    if not process.returncode == 0:
        logger.error(f'Return code: {process.returncode}')

    return output, process.returncode

def git_pull():
    logger.info(f'Git pull for the whole project')
    _, result = execute_cmd([f'git -C {str(args.path)} pull'])

    if not result == 0:
        raise Exception (f'Error while executing command')

def use_patches(project_name: str, applied_patches: dict, applied_patches_path: str):
    upstream = ""
    if args.upstream == "":
        logger.info(f'Get upstream branch for {project_name} project')
        output, _ = execute_cmd([f'git -C {str(args.path / project_name)} rev-parse --abbrev-ref --symbolic-full-name @{{u}}'])
        upstream = output[0]
        logger.success(f'Upstream for {project_name}: {upstream}')
    else:
        upstream = args.upstream

    logger.info(f'Use patches for {project_name} for {upstream} upstream')

    patch_dir = args.path / "overlay" / f'{project_name}_patches'
    patch_files = sorted(f for f in os.listdir(patch_dir) if f.endswith(".patch"))
    patch_paths = [os.path.join(patch_dir, f) for f in patch_files]

    applied_patches_for_project = applied_patches[project_name]
    begin_patches_processing = applied_patches_for_project == ""

    for patch in patch_paths:
        if not begin_patches_processing:
            if patch == applied_patches_for_project:
                begin_patches_processing = True
            continue

        execute_cmd([f'git -C {str(args.path / project_name)} am --3way {patch}'])
        applied_patches[project_name] = patch

    with open(applied_patches_path, 'w') as file:
        json.dump(applied_patches, file, indent = 4)

def load_applied_patches(file_path):

    if not file_path.exists():
        logger.info(f'Applied patches file {file_path} does not exist')
        json_file = {}
        for project in projects:
            json_file[project] = ""
        return json_file

    with open(file_path, 'r') as file:
        json_file = json.load(file)

        logger.success(f'Applied patches file {file_path} was read')
        return json_file

def main():
    global args

    parser = argparse.ArgumentParser(description = "Immitate git pull with patches usage")
    parser.add_argument("--path", type = str, required = False, default = os.getcwd(), help = "The directory with the project")
    parser.add_argument("--upstream", type = str, required = False, default = "", help = "upstream branch for sub projects; if empty, current upstream branch will be used")
    args = parser.parse_args()
    args.path = Path(args.path)

    git_pull()

    applied_patches_path = Path(args.path / "overlay" / "applied_patches.json")
    applied_patches = load_applied_patches(applied_patches_path)
    [use_patches(project, applied_patches, applied_patches_path) for project in projects]

if __name__ == "__main__":

    try:
        main()

    except Exception as exception:

        logger.critical(f"*** {exception}")

        logger.debug("Traceback")
        traceback.print_exc()

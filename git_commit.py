#!/usr/bin/env python3

import argparse
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

def make_commit(git_commands, project_name: str = None):
    if project_name:
        logger.info(f'Make commit "{args.message}" for {project_name}')
    else:
        logger.info(f'Make commit "{args.message}" for the whole repository')

    cmd = [f'git']
    if project_name:
        cmd.extend(['-C', str(args.path / project_name)])
    cmd.append('commit')
    cmd.extend(git_commands)

    _, returncode = execute_cmd(cmd)
    if not returncode == 0:
        raise Exception(f'Unable to make commit')

def make_patches(project_name: str):
    upstream = ""
    if args.upstream == "":
        logger.info(f'Get upstream branch for {project_name} project')
        output, _ = execute_cmd([f'git -C {str(args.path / project_name)} rev-parse --abbrev-ref --symbolic-full-name @{{u}}'])
        upstream = output[0]
        logger.success(f'Upstream for {project_name}: {upstream}')
    else:
        upstream = args.upstream

    logger.info(f'Make patches for {project_name} for {upstream} upstream')
    execute_cmd([f'git -C {str(args.path / project_name)} format-patch {upstream} -o {str(args.path / "overlay" / f"{project_name}_patches")}'])

def main():
    global args

    parser = argparse.ArgumentParser(description = "Immitage git command for all subprojects and make patches")
    parser.add_argument("--path", type = str, required = False, default = os.getcwd(), help = "The directory with the project")
    parser.add_argument("-m", "--message", type = str, required = True, help = "git message for subprojects")
    parser.add_argument("--upstream", type = str, required = False, default = "", help = "upstream branch for sub projects; if empty, current upstream branch will be used")
    args, unknown_args = parser.parse_known_args()
    args.path = Path(args.path)

    git_commands = unknown_args.copy()
    if args.message and '-m' not in unknown_args and '--message' not in unknown_args:
        git_commands.extend(['-m', f'"{args.message}"'])

    [make_commit(git_commands, project) for project in projects]
    [make_patches(project) for project in projects]
    make_commit(git_commands)

if __name__ == "__main__":

    try:
        main()

    except Exception as exception:

        logger.critical(f"*** {exception}")

        logger.debug("Traceback")
        traceback.print_exc()

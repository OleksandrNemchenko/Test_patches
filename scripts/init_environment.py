#!/usr/bin/env python3

import argparse
import os
import subprocess
import traceback
from loguru import logger
from pathlib import Path

args = None

def execute_cmd(command):
    logger.debug(" ".join(command))

    process = subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        text = True,
        bufsize = 1,
        shell = True
    )

    for line in process.stdout:
        print(line, end = '')

    process.wait()

    if process.returncode == 0:
        logger.success(f'Return code: {process.returncode}')
    else:
        logger.error(f'Return code: {process.returncode}')

def init_test_big1():
    logger.info('Init subproject Test_Big1')
    execute_cmd(['git', 'clone', 'https://github.com/OleksandrNemchenko/Test_Big1.git', str(args.path / "Test_Big1")])

def init_test_big2():
    logger.info('Init subproject Test_Big2')
    execute_cmd(['git', 'clone', '--recurse-submodules', 'https://github.com/OleksandrNemchenko/Test_Big2.git', str(args.path / "Test_Big2")])

def main():
    global args

    parser = argparse.ArgumentParser(description = "Init environment")
    parser.add_argument("path", type = str, default = os.getcwd(), help = "The directory with the project")
    args = parser.parse_args()
    args.path = Path(args.path)

    logger.info(f'Start environment initialization')

    if Path("Test_Big1").exists():
        logger.debug(f'Project "Test_Big1" exists')
    else:
        init_test_big1()

    if Path("Test_Big2").exists():
        logger.debug(f'Project "Test_Big2" exists')
    else:
        init_test_big2()

if __name__ == "__main__":

    try:
        main()

    except Exception as exception:

        logger.critical(f"*** {exception}")

        logger.debug("Traceback")
        traceback.print_exc()

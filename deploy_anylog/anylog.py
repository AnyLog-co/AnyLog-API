import argparse
import os.path
import subprocess
import importlib.util

URL = "http://173.255.254.34:31900/macosx/anylog_network-1.3.2309-cp311-cp311-macosx_13_0_x86_64.whl"
FILE_PATH = os.path.expanduser(os.path.expandvars(__file__))

def main():
    """
    Deploy AnyLog via python3 pip package using the deployment_script.al
    Users can update the deployment_script.al with their own TCP and REST service as well as license key
    :process:
        1. based on URL, install anylog_node packaae if doesn't exist
        2. deploy AnyLog with deployment_script.al (TCP server service, REST server service and license key)
    :global:
        URL:str - URL path to the latest Ubuntu build
        FILE_PATH:str - file path
    options:
        -h, --help          show this help message and exit
        --url   URL         AnyLog pip package URL (default is Ubuntu)
    :params:
        commands:list - commands to execute as part of AnyLog node deployment
        user_input:anylog_node.cmd.user_cmd.UserInput - initiate anyLog
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('--url', type=str, default=URL, help='AnyLog pip package URL (default is Ubuntu)')
    args = parse.parse_args()

    commands = [
        FILE_PATH,
        f"process {FILE_PATH.replace('anylog.py', 'deployment_script.al')}"
    ]
    argv = ' '.join(commands).split()
    argc = len(argv)

    if not importlib.util.find_spec("anylog_node"):
        subprocess.run(["pip", "install", args.url])

    if importlib.util.find_spec("anylog_node"):
        try:
            import anylog_node.cmd.user_cmd as user_cmd
        except Exception as error:
            print(f"anylog_node pacakge is not supported on this platform. Cannot continue...")
            exit(1)
    else:
        print(f"Failed to locate 'anylog_node' package. Cannot continue...")
        exit(1)

    user_input = user_cmd.UserInput()
    user_input.process_input(arguments=argc, arguments_list=argv)


if __name__ == '__main__':
    main()
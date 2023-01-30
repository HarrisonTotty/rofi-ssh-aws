#!/usr/bin/env python3
'''
rofi-ssh-aws

A script for ssh'ing into AWS EC2 nodes via rofi.
'''

from __future__ import annotations

import json
import os
import sys

from . import aws
from . import cli
from . import rofi
from . import ssh

def main() -> None:
    '''
    The entrypoint of the script.
    '''
    # Parse command-line arguments.
    args = cli.parse_arguments()

    # Determine command
    if args.command == 'dump':
        with open(os.path.expanduser(args.cache_file), 'r') as f:
            print(f.read())
        sys.exit(0)
    elif args.command == 'sync':
        instances = aws.get_instances(ignore_start=args.ignore_start)
        with open(os.path.expanduser(args.cache_file), 'w') as f:
            f.write(json.dumps(instances))
        sys.exit(0)
    elif args.command == 'ssh':
        with open(os.path.expanduser(args.cache_file), 'r') as f:
            instances = json.loads(f.read())
        selected = rofi.select_instance(instances)
        if not selected:
            sys.exit(0)
        ssh.launch(selected, term=args.term, terminal_format=args.terminal_format)

if __name__ == '__main__':
    main()

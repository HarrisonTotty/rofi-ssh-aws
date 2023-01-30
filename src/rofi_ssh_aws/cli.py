'''
Contains methods associated with the CLI.
'''

from __future__ import annotations

import argparse
import os

HELP_DESCRIPTION = '''
A script for ssh'ing into AWS EC2 instances via rofi.
'''

HELP_EPILOG = '''
'''

def parse_arguments() -> argparse.Namespace:
    '''
    Parses the command-line arguments passed to the script.
    '''
    argparser = argparse.ArgumentParser(
        description = HELP_DESCRIPTION,
        epilog = HELP_EPILOG,
        usage = 'rofi-ssh-aws dump|ssh|sync [...]',
        add_help = False
    )
    argparser.add_argument(
        'command',
        choices = ['dump', 'ssh', 'sync'],
        help = 'Whether to sync the instance cache or ssh into an instance. Can also dump the contents of the cache.',
    )
    argparser.add_argument(
        '-c',
        '--cache-file',
        default = os.getenv('ROFI_SSH_AWS_CACHE_FILE', os.path.expanduser('~/.cache/rofi-ssh-aws.json')),
        dest = 'cache_file',
        help = '[env: ROFI_SSH_AWS_CACHE_FILE] The location of the EC2 instance cache file. Defaults to "~/.cache/rofi-ssh-aws.json"',
        metavar = 'FILE'
    )
    argparser.add_argument(
        '-i',
        '--ignore-start',
        default = os.getenv('ROFI_SSH_AWS_IGNORE_START', 'eks-'),
        dest = 'ignore_start',
        help = '[env: ROFI_SSH_AWS_IGNORE_START] Ignores instances which start with the specified string.',
        metavar = 'STR'
    )
    argparser.add_argument(
        '-t',
        '--terminal-format',
        default = os.getenv(
            'ROFI_SSH_AWS_TERM_FMT',
            '/usr/bin/alacritty --title "SSH : [{profile}/{region}] {environment}/{application}/{name}/{id} @ {ip}" -e ssh {ip}'
        ),
        dest = 'terminal_format',
        help = '[env: ROFI_SSH_AWS_TERM_FMT] Terminal command to run. May be formatted to match any instance field.',
        metavar = 'STR'
    )
    argparser.add_argument(
        '-T',
        '--term',
        default = os.getenv('TERM', 'rxvt'),
        dest = 'term',
        help = '[env: TERM] Overrides the TERM environment variable sent to the spawned SSH session.',
        metavar = 'STR'
    )
    argparser.add_argument(
        '-h',
        '--help',
        action = 'help',
        help = 'Displays help and usage information.'
    )
    return argparser.parse_args()

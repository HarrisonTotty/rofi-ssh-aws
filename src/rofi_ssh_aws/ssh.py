'''
Contains methods associated with SSH
'''

import os
import subprocess

def launch(instance: dict[str, str], term: str, terminal_format: str) -> None:
    os.environ['TERM'] = term
    cmd = terminal_format.format(
        profile = instance['profile'],
        region = instance['region'],
        id = instance['id'],
        name = instance.get('name', '?'),
        environment = instance.get('environment', '?'),
        iclass = instance.get('class', '?'),
        requester = instance.get('requester', '?'),
        application = instance.get('application', '?'),
        hostname = instance['hostname'],
        ip = instance['ip'],
        term = term
    )
    subprocess.Popen(cmd, start_new_session=True, shell=True)

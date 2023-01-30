'''
rofi-related methods
'''

from os.path import join
import subprocess

ROFI_OPTS="-dmenu -markup-rows -i -no-custom -p ssh"

def rofi(stdin_str: str) -> tuple[str, int]:
    '''
    Launches rofi, returning a tuple of the form (STDOUT, RETNCODE)
    '''
    process = subprocess.Popen(
        f'/usr/bin/rofi {ROFI_OPTS}',
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        shell = True
    )
    output = process.communicate(input=stdin_str.encode('ascii', 'ignore'))[0].decode('ascii', 'ignore')
    exit_code = process.returncode
    return (output, exit_code)

def instances_to_rofi_str(instances: list[dict[str, str]]) -> str:
    '''
    Converts an instance into its rofi string.
    '''
    substrings = []
    for i, instance in enumerate(instances):
        substrings.append(
            '{i}: [{profile}/{region}] {env}/{app}/{name}/{id} <span weight="light" size="small"><i>({ip})</i></span>'.format(
                i = str(i),
                profile = instance['profile'],
                region = instance['region'],
                env = '?' if instance['environment'] is None else instance['environment'],
                app = '?' if instance['application'] is None else instance['application'],
                name = '?' if instance['name'] is None else instance['name'],
                id = instance['id'],
                ip = instance['ip']
            )
        )
    return '\n'.join(substrings)

def select_instance(instances: list[dict[str, str]]) -> dict[str, str]:
    '''
    Selects an instance using rofi.
    '''
    (output, exit_code) = rofi(instances_to_rofi_str(instances))
    if exit_code != 0:
        raise Exception('rofi subprocess returned non-zero exit code')
    if not output:
        return {}
    try:
        index = int(output.split(':', 1)[0])
    except:
        return {}
    return instances[index]

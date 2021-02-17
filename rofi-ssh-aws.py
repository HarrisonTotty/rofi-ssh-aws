#!/usr/bin/env python3

import argparse
import boto3
import datetime
import os
import subprocess
import sys

REGIONS = ['us-west-2']

argparser = argparse.ArgumentParser(
    description = 'A python wrapper script around rofi to SSH into AWS instances.',
    usage = 'rofi-ssh-aws [...]',
    add_help = False,
    formatter_class = lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=45, width=100)
)
argparser.add_argument(
    '-c',
    '--cache-file',
    default = os.getenv('ROFI_SSH_AWS_CACHE_FILE', os.path.expanduser('~/.cache/rofi-ssh-aws.cache')),
    dest = 'cache_file',
    help = '[env: ROFI_SSH_AWS_CACHE_FILE] Specifies the file within which cached server information will be placed. Defaults to "~/.cache/rofi-ssh-aws.cache".',
    metavar = 'FILE'
)
argparser.add_argument(
    '-h',
    '--help',
    action = 'help',
    help = 'Displays help and usage information.'
)
argparser.add_argument(
    '-t',
    '--cache-timeout',
    default = int(os.getenv('ROFI_SSH_AWS_CACHE_TIMEOUT', '30')),
    dest = 'cache_timeout',
    help = '[env: ROFI_SSH_AWS_CACHE_TIMEOUT] Specifies a timeout for the cache file, in minutes. Defaults to 30 minutes.',
    metavar = 'MIN',
    type = int
)
args = argparser.parse_args()

def rofi(cache_file):
    process = subprocess.Popen(
        "cat '{cf}' | /usr/bin/rofi -dmenu -markup-rows -i -no-custom -p 'ssh : '".format(
            cf = cache_file
        ),
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        shell = True
    )
    output = process.communicate()[0].decode('ascii', 'ignore')
    exit_code = process.returncode
    return (output, exit_code)

now = datetime.datetime.now()
if not os.path.isfile(args.cache_file) or (datetime.datetime.fromtimestamp(os.path.getmtime(args.cache_file)) < now - datetime.timedelta(minutes=args.cache_timeout)):
    data = []
    for profile in boto3.session.Session().available_profiles:
        if profile == 'default':
            continue
        session = boto3.session.Session(
            profile_name = profile
        )
        for region in REGIONS:
            try:
                ec2_reservations = session.client('ec2', region_name=region).describe_instances()['Reservations']
            except:
                continue
            if not ec2_reservations:
                continue
            ec2_instances = []
            for r in ec2_reservations:
                ec2_instances.extend(r['Instances'])
            for instance in ec2_instances:
                if not instance['State']['Name'].lower() in ['running', 'stopped', 'starting', 'stopping']:
                    continue
                data.append({
                    'application': next((i['Value'] for i in instance['Tags'] if i['Key'].lower() == 'application'), None),
                    'dns_name': instance['PrivateDnsName'],
                    'environment': next((i['Value'] for i in instance['Tags'] if i['Key'].lower() == 'environment'), None),
                    'ip_address': instance['PrivateIpAddress'],
                    'name': next((i['Value'] for i in instance['Tags'] if i['Key'].lower() == 'name'), None),
                    'profile': profile,
                    'region': region,
                    'requester': next((i['Value'] for i in instance['Tags'] if i['Key'].lower() == 'requester'), None),
                    'role': next((i['Value'] for i in instance['Tags'] if i['Key'].lower() == 'role'), None),
                    'service': 'ec2',
                    'size': instance['InstanceType'],
                    'state': instance['State']['Name'],
                })
    with open(args.cache_file, 'w') as f:
        for d in data:
            f.write(
                '<b>{state}</b>[{profile}/{region}] : {req}{env}/{name} <span weight="light" size="small"><i>({ip_address})</i></span>\n'.format(
                    profile = d['profile'],
                    region = d['region'],
                    service = d['service'],
                    state = {'running': '↑', 'stopped': '↓', 'stopping': '↘', 'starting': '↗'}[d['state'].lower()],
                    name = d['name'],
                    req = (d['requester'] + '/') if d['requester'] else '',
                    env = d['environment'],
                    ip_address = d['ip_address']
                )
            )

(rofi_out, rofi_ec) = rofi(args.cache_file)
if rofi_out and rofi_ec == 0:
    ip_address = rofi_out.split('(', 1)[1].split(')', 1)[0]
    prs = rofi_out.split('[', 1)[1].split(']', 1)[0]
    rev = rofi_out.split(':', 1)[1].split('<', 1)[0].strip()
    term = "/usr/bin/urxvtc +sb -letsp 1 -title 'SSH : [{prs}] : {rev}' -e $HOME/.config/scripts/ssh-wrapper.sh {ip}".format(
        prs = prs,
        rev = rev,
        ip = ip_address
    )
    subprocess.Popen(term, start_new_session=True, shell=True)

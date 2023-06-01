'''
AWS-related methods.
'''

from __future__ import annotations

import boto3

from typing import Optional

def clean_tag_value(value: Optional[str]) -> Optional[str]:
    '''
    Utility function for cleaning tag values.
    '''
    if value is None:
        return None
    elif not value:
        return None
    elif value.lower() in ['none', 'null']:
        return None
    else:
        return value

def get_instances(ignore_start: str) -> list[dict[str, str]]:
    '''
    Returns a list of AWS instances.
    '''
    res = []
    for profile in boto3.session.Session().available_profiles:
        if profile == 'default': continue
        session = boto3.session.Session(profile_name=profile)
        regions = [r for r in session.get_available_regions(service_name='ec2') if r.startswith('us-')]
        for region in regions:
            ec2 = session.client('ec2', region_name=region)
            reservations = ec2.describe_instances(
                Filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
            )['Reservations']
            for reservation in reservations:
                for data in reservation['Instances']:
                    if not 'Tags' in data: continue
                    tags = {t['Key']: clean_tag_value(t['Value']) for t in data['Tags']}
                    if ignore_start and tags.get('Name', '?').startswith(ignore_start):
                        continue
                    instance = {
                        'profile': profile,
                        'region': region,
                        'id': data['InstanceId'],
                        'name': tags.get('Name'),
                        'environment': tags.get('Environment'),
                        'class': tags.get('Class'),
                        'requester': tags.get('Requester'),
                        'application': tags.get('Application'),
                        'hostname': data['PrivateDnsName'],
                        'ip': data['PrivateIpAddress']
                    }
                    res.append(instance)
    return sorted(
        res,
        key=lambda i: i['profile'] + '/' + i['region'] + '/' + ('zzz' if i['environment'] is None else i['environment'].lower()) + '/' + ('zzz' if i['application'] is None else i['application'].lower()) + '/' + ('zzz' if i['name'] is None else i['name'].lower()) + '/' + i['id']
    )

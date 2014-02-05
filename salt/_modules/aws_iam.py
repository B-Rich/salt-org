# -*- coding: utf-8 -*-
'''
Support for the Amazon Identity and Access Management Service.
'''
import json
import salt.utils
import logging
log = logging.getLogger(__name__)

def __virtual__():
    if salt.utils.which('aws'):
        # awscli is installed, load the module
        return True
    return False


def _run_aws(cmd, **kwargs):
    '''
    Runs the given command against AWS.
    cmd
        Command to run
    kwargs
        Key-value arguments to pass to the command
    '''
    _formatted_args = [
        '--{0} "{1}"'.format(k, v) for k, v in kwargs.iteritems()]

    cmd = 'aws {cmd} {args} --output json'.format(
        cmd=cmd,
        args=' '.join(_formatted_args))
    rtn = __salt__['cmd.run'](cmd)
    try:
        rtn = json.loads(rtn)
    except:
        log.error(rtn)
        return None
    return rtn

### USERS ###
def list_users():
    '''
    List users.
    '''
    out = _run_aws('iam list-users')
    return out['Users']

def create_user(name):
    '''
    Create a user.
    '''
    return _run_aws('iam create-user', **{'user-name': name})['User']

def get_user(name):
    '''
    Get a user.
    '''
    user = _run_aws('iam get-user', **{'user-name': name})
    if not user:
       return user
    return user['User']

def delete_user(name):
    '''
    Delete a user.
    '''
    return _run_aws('iam delete-user', **{'user-name': name})


def update_user(name, **kwargs):
    '''
    Update a user.
    '''
    return _run_aws('iam update-user', **{'user-name': name}.update(kwargs))

### GROUPS ###
def list_groups():
    '''
    List groups.
    '''
    return _run_aws('iam list-groups')['Groups']

def create_group(name):
    '''
    Create a group.
    '''
    group = _run_aws('iam create-group', **{'group-name': name})
    if group == None: return group
    return group['Group']

def get_group(name):
    '''
    Get users in a group.
    '''
    return _run_aws('iam get-group', **{'group-name': name})

def delete_group(name):
    '''
    Delete a group.
    '''
    return _run_aws('iam delete-group', **{'group-name': name})

def update_group(name, new_name):
    '''
    Delete a group.
    '''
    return _run_aws('iam update-group', **{'group-name': name, 'new-group-name': new_name})

### GROUP MEMBERSHIP ###
def add_user_to_group(user, group):
    '''
    Add a user to a group.
    '''
    return _run_aws('iam add-user-to-group', **{'user-name': user, 'group-name': group})

def remove_user_from_group(user, group):
    '''
    Remove a user from a group.
    '''
    return _run_aws('iam remove-user-from-group', **{'user-name': user, 'group-name': group})

### ACCESS KEYS ###
def list_access_keys(user):
    '''
    List keys for a user.
    '''
    keys = _run_aws('iam list-access-keys', **{'user-name': user})
    if keys == None: return keys
    return keys['AccessKeyMetadata']

def create_access_key(user):
    '''
    Create an access key for a user.
    '''
    key = _run_aws('iam create-access-key', **{'user-name': user})
    if key == None: return key
    return key['AccessKey']

def delete_access_key(user, key_id):
    '''
    Delete an access key for a user.
    '''
    return _run_aws('iam delete-access-key', **{'user-name': user, 'access-key-id': key_id})

'''
Management of users in AWS
=============================

.. code-block:: yaml

    engineers:
      aws_iam_user.present:
        - name: rgarcia
        - keys: True
        - dry_run: False

      aws_iam_group.absent:
        - name: RemoveThisUser
'''

import sys


def present(name, keys=False, dry_run=False):
  '''
  Ensure that a user is present in AWS.

  name
      The name of the user to manage.

  keys
      If true, ensure the user has access keys.

  dry_run
      Don't actually make any changes in AWS. False by default.

  '''
  ret = {'name': name,
         'changes': {},
         'result': True,
         'comment': ''}
  user = __salt__['aws_iam.get_user'](name)
  if user is None:
    if dry_run or __salt__['aws_iam.create_user'](name) is not None:
      ret['changes']['create_user'] = {'name': name}
      if dry_run:
        return
    else:
      ret["result"] = False
      ret["comment"] = "Error creating user"
      return ret

  if keys == True:
    keys = __salt__['aws_iam.list_access_keys'](name)
    if len(keys) == 0:
      if dry_run:
        ret['changes']['create_access_key'] = {'name': name}
      else:
        ret['changes']['create_access_key'] = __salt__['aws_iam.create_access_key'](name)

  return ret


def absent(name, dry_run=False):
  '''
  Ensure that a user does not exist.

  name
      The name of the user to delete, if present.

  dry_run
      Don't actually make any changes in AWS.
  '''
  ret = {'name': name,
         'changes': {},
         'result': True,
         'comment': ''}
  user = __salt__['aws_iam.get_user'](name)
  if user is None:
    return ret

  # need to delete all access keys first
  for key in __salt__['aws_iam.list_access_keys'](name):
    if 'delete_access_key' not in ret['changes']:
      ret['changes']['delete_access_key'] = []
    ret['changes']['delete_access_key'].append(key['AccessKeyId'])
    if not dry_run:
      __salt__['aws_iam.delete_access_key'](name, key['AccessKeyId'])

  ret['changes']['delete_user'] = name
  if not dry_run:
    __salt__['aws_iam.delete_user'](name)
  return ret

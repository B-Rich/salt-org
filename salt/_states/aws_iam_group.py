'''
Management of groups in AWS
=============================

.. code-block:: yaml

    engineers:
      aws_iam_group.present:
        - name: Engineers
        - members:
          - rgarcia
        - strict: False

      aws_iam_group.absent:
        - name: RemoveThisTeam
'''

import sys


def present(name, members=None, strict=False, dry_run=False):
  '''
  Ensure that a group is present and has the correct members.

  name
      The name of the group to manage.

  members
      List of users that should be part of the group. Pass None to accept the existing state of membership in this team.

  strict
      Remove from the group any unlisted users. False by default.

  dry_run
      Don't actually make any changes in AWS. False by default.

  '''
  ret = {'name': name,
         'changes': {},
         'result': True,
         'comment': ''}
  group = __salt__['aws_iam.get_group'](name)
  if group is None:
    # Group doesn't exist
    if dry_run:
      ret['changes']['create_group'] = {'name': name, 'members': members}
      return
    __salt__['aws_iam.create_group'](name)
    for member in members:
      __salt__['aws_iam.add_user_to_group'](member, name)
    ret['changes']['create_group'] = {'name': name, 'members': members}
    return ret

  # ensure group membership is correct
  if members is not None:
    members_currently = set([u["UserName"] for u in group["Users"]])
    members_desired = set(members)
    members_to_add = members_desired - members_currently
    members_to_remove = (members_currently - members_desired) if strict else set()
    if len(members_to_add):
      ret['changes']['add_user_to_group'] = []
      for member_to_add in members_to_add:
        ret['changes']['add_user_to_group'].append((member_to_add, name))
        if not dry_run:
          __salt__['aws_iam.add_user_to_group'](member_to_add, name)
    if len(members_to_remove):
      ret['changes']['remove_user_from_group'] = []
      for member_to_remove in members_to_remove:
        ret['changes']['remove_user_from_group'].append((member_to_remove, name))
        if not dry_run:
          __salt__['aws_iam.remove_user_from_group'](member_to_remove, name)

  return ret


def absent(name, dry_run=False):
  '''
  Ensure that a team does not exist.

  name
      The name of the team to delete, if present.

  dry_run
      Don't actually make any changes in GitHub.
  '''
  ret = {'name': name,
         'changes': {},
         'result': True,
         'comment': ''}
  group = __salt__['aws_iam.get_group'](name)
  if group is None:
    # Team doesn't exist, success!
    return
  if not dry_run:
    __salt__['aws_iam.delete_group'](name)
  return ret

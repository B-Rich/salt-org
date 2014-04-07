'''
Management of collaborators on Heroku apps
==========================================

The hk_collaborators module is used to create and manage Heroku collaborator settings.
Collaborators can either be present or absent:

.. code-block:: yaml

    clever-website: # <- the name of the heroku app
      hk_collaborators.present:
        - token: xxxxx
        - members:
          - rafael.garcia@clever.com
        - strict: False
'''

import sys

def present(name, token, members, strict=False, dry_run=False):
    '''
    Ensure that an app is configured to have certain collaborators.

    name
        The name of the Heroku app.

    token
        Heroku OAuth token to use (can be found on account settings page under "API Key").

    members
        List of users that should be part of the team.

    strict
        Remove from the list of collaborators any unlisted members. False by default.

    dry_run
        Don't actually make any changes in Heroku. False by default.
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    members_currently_full = __salt__['hk_collaborator.list'](token, name)

    # ensure membership is correct
    members_currently = set([m["user"]["email"] for m in members_currently_full])
    members_desired = set(members)
    members_to_add = members_desired - members_currently
    members_to_remove = (members_currently - members_desired) if strict else set()
    if len(members_to_add):
        ret['changes']['add_member'] = []
        for member_to_add in members_to_add:
            if dry_run or __salt__['hk_collaborator.create'](token, name, member_to_add):
                ret['changes']['add_member'].append(member_to_add)
            else:
                ret["result"] = False
                ret["comment"] = "Error adding {} to team".format(member_to_add)
                return ret
    if len(members_to_remove):
        ret['changes']['remove_member'] = []
        for member_to_remove in members_to_remove:
            if dry_run or __salt__['hk_collaborator.delete'](token, name, member_to_remove):
                ret['changes']['remove_member'].append(member_to_remove)
            else:
                ret["result"] = False
                ret["comment"] = "Error removing {} from team".format(member_to_remove)
                return ret

    return ret

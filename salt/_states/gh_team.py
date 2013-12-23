'''
Management of teams in GitHub
=============================

The gh_team module is used to create and manage GitHub team settings. Teams
can be either present or absent:

.. code-block:: yaml

    engineers:
      gh_team.present:
        - token: xxxxx
        - org: Clever
        - name: Engineers
        - members:
          - rgarcia
        - permission: push
        - repos:
          - Clever/clever-js
          - Clever/clever-python
        - strict: False

      gh_team.absent:
        - token: xxxxx
        - org: Clever
        - name: RemoveThisTeam
'''

import sys

def present(name, token, org, members=None, permission=None, repos=None, strict=False, dry_run=False):
    '''
    Ensure that a team is present

    name
        The name of the team to manage.

    token
        OAuth token created by an admin for the organization.

    org
        The organization that this team belongs to.

    members
        List of users that should be part of the team. Pass None to accept the existing state of membership in this team.

    permission
        The permission to grant the team: pull, push, or admin. Pass None to accept existing or default permission.

    repos
        List of repos to give this team access to. Pass None to accept existing state of repos.

    strict
        Remove from the team any unlisted members or repos. False by default.

    dry_run
        Don't actually make any changes in GitHub. False by default.

    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    teams = __salt__['gh_team.list'](token, org)
    team = next((t for t in teams if t["name"] == name), None)
    if team == None:
        # Team doesn't exist
        if dry_run:
            ret['changes']['add'] = {'org':org, 'name': name, 'permission': permission, 'repos': repos}
            return
        team = __salt__['gh_team.add'](token, org, name, permission, repos)
        if team != None:
            ret['changes']['add'] = {'org':org, 'name': name, 'permission': permission, 'repos': repos}
        else:
            ret["result"] = False
            ret["comment"] = "Error adding GitHub team"
            return ret
    team = __salt__['gh_team.get'](token, team["id"]) # get more detail

    # ensure permission is correct
    if permission != None and team["permission"] != permission:
        if dry_run or __salt__['gh_team.edit'](token, team["id"], name, permission) != None:
            ret['changes']['edit'] = {'team':team["id"], 'name': name, 'permission': permission}
        else:
            ret["result"] = False
            ret["comment"] = "Error editing permission"
            return ret

    # ensure team membership is correct
    if members != None:
        member_objs = __salt__['gh_team.list_members'](token, team["id"])
        if member_objs == None:
            ret["result"] = False
            ret["comment"] = "Error fetching team members"
            return ret
        members_currently = set([m["login"] for m in member_objs]) # set of usernames
        members_desired = set(members)
        members_to_add = members_desired - members_currently
        members_to_remove = (members_currently - members_desired) if strict else set()
        if len(members_to_add):
            ret['changes']['add_member'] = []
            for member_to_add in members_to_add:
                if dry_run or __salt__['gh_team.add_member'](token, team["id"], member_to_add):
                    ret['changes']['add_member'].append(member_to_add)
                else:
                    ret["result"] = False
                    ret["comment"] = "Error adding {} to team".format(member_to_add)
                    return ret
        if len(members_to_remove):
            ret['changes']['remove_member'] = []
            for member_to_remove in members_to_remove:
                if dry_run or __salt__['gh_team.remove_member'](token, team["id"], member_to_remove):
                    ret['changes']['remove_member'].append(member_to_remove)
                else:
                    ret["result"] = False
                    ret["comment"] = "Error removing {} from team".format(member_to_remove)
                    return ret

    # ensure repo access is correct
    if repos != None:
        repo_objs = __salt__['gh_team.list_repos'](token, team["id"])
        if repo_objs == None:
            ret["result"] = False
            ret["comment"] = "Error fetching repos"
            return ret
        repos_currently = set([m["full_name"] for m in repo_objs]) # set of full "Org/repo" strings
        repos_desired = set(repos)
        repos_to_add = repos_desired - repos_currently
        repos_to_remove = repos_currently - repos_desired if strict else set()
        if len(repos_to_add):
            ret['changes']['add_repo'] = []
            for repo_to_add in repos_to_add:
                if dry_run or __salt__['gh_team.add_repo'](token, team["id"], repo_to_add):
                    ret['changes']['add_repo'].append(repo_to_add)
                else:
                    ret["result"] = False
                    ret["comment"] = "Error adding repo {} to team".format(repo_to_add)
                    return ret
        if len(repos_to_remove):
            ret['changes']['remove_repo'] = []
            for repo_to_remove in repos_to_remove:
                if dry_run or __salt__['gh_team.remove_repo'](token, team["id"], repo_to_remove):
                    ret['changes']['remove_repo'].append(repo_to_remove)
                else:
                    ret["result"] = False
                    ret["comment"] = "Error removing repo {} from team".format(repo_to_remove)
                    return ret

    return ret

def absent(name, token, org, dry_run=False):
    '''
    Ensure that a team does not exist.

    name
        The name of the team to delete, if present.

    token
        OAuth token created by an admin for the organization.

    org
        The organization that this team belongs to.

    dry_run
        Don't actually make any changes in GitHub.
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    teams = __salt__['gh_team.list'](token, org)
    team = next((t for t in teams if t["name"] == name), None)
    if team == None:
        # Team doesn't exist, success!
        return
    ret['result'] = dry_run or __salt__['gh_team.remove'](token, team["id"])
    return ret

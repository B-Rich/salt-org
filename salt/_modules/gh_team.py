'''
Module to manage teams in a Github org.

See http://developer.github.com/v3/orgs/teams/.
'''

import logging
log = logging.getLogger(__name__)
import requests
import json

def list(token, org):
    '''
    List all teams in a Github organization

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.list <token> <org>
    '''
    r = requests.get('https://api.github.com/orgs/{}/teams'.format(org), auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {}'.format(r))
        return False
    return json.loads(r.content)

def add(token, org, name, permission, repos=[]):
    '''
    Create a new team in a Github organization

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.add <token> <org> <team name> <permission>
    '''
    headers = {'Content-type': 'application/json'}
    payload = {"name": name, "permission": permission, "repo_names": repos}
    r = requests.post('https://api.github.com/orgs/{}/teams'.format(org),
                      auth=(token, ''),
                      data=json.dumps(payload),
                      headers=headers)
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return None
    return json.loads(r.content)

def get(token, team_id):
    '''
    Get information about a team

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.get <token> <team id>
    '''
    r = requests.get('https://api.github.com/teams/{}'.format(team_id), auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return None
    return json.loads(r.content)

def remove(token, team_id):
    '''
    Remove a team from a Github organization

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.remove <token> <team id>
    '''
    r = requests.delete('https://api.github.com/teams/{}'.format(team_id), auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return False
    return True

def edit(token, team_id, name, permission):
    '''
    Edit team settings in Github

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.edit <token> <team id> <new team name> <new team permission>
    '''
    headers = {'Content-type': 'application/json'}
    payload = {"name": name, "permission": permission}
    r = requests.patch('https://api.github.com/teams/{}'.format(team_id),
                       auth=(token, ''),
                       data=json.dumps(payload),
                       headers=headers)
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return None
    return json.loads(r.content)


def list_members(token, team_id):
    '''
    List Github team members

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.list_members <token> <team id>
    '''
    r = requests.get('https://api.github.com/teams/{}/members'.format(team_id),
                       auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return None
    return json.loads(r.content)

def get_member(token, team_id, user):
    '''
    Check if a user belongs to a team. Returns True/False.

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.get_member <token> <team id> <username>
    '''
    r = requests.get('https://api.github.com/teams/{}/members/{}'.format(team_id, user),
                     auth=(token, ''))
    return r.status_code == 204

def add_member(token, team_id, user):
    '''
    Add a user to a team

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.add_member <token> <team id> <username>
    '''
    r = requests.put('https://api.github.com/teams/{}/members/{}'.format(team_id, user),
                     auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return False
    return True

def remove_member(token, team_id, user):
    '''
    Add a user to a team

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.remove_member <token> <team id> <username>
    '''
    r = requests.delete('https://api.github.com/teams/{}/members/{}'.format(team_id, user),
                     auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return False
    return True


def list_repos(token, team_id):
    '''
    List Github team repos

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.list_repos <token> <team id>
    '''
    r = requests.get('https://api.github.com/teams/{}/repos'.format(team_id),
                       auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return None
    return json.loads(r.content)

def get_repo(token, team_id, repo):
    '''
    Find if a repo belongs to a team. Returns True/False.

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.get_repo <token> <team id> <Org/repo>
    '''
    r = requests.get('https://api.github.com/teams/{}/repos/{}'.format(team_id, repo),
                     auth=(token, ''))
    return r.status_code == 204

def add_repo(token, team_id, repo):
    '''
    Add a repo to a team

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.add_repo <token> <team id> <Org/repo>
    '''
    r = requests.put('https://api.github.com/teams/{}/repos/{}'.format(team_id, repo),
                     auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return False
    return True

def remove_repo(token, team_id, repo):
    '''
    Remove a repo from a team

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_team.remove_repo <token> <team id> <Org/repo>
    '''
    r = requests.delete('https://api.github.com/teams/{}/repos/{}'.format(team_id, repo),
                     auth=(token, ''))
    if not r.ok:
        log.error('Error making github api request: {} {}'.format(r, r.content))
        return False
    return True

'''
Module to manage repo hooks

See http://developer.github.com/v3/repos/hooks
'''

import logging
log = logging.getLogger(__name__)
import requests
import json
import ast


def list(token, repo):
  '''
  List all hooks for a repo

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local gh_hooks.list <token> <owner>/<repo>
  '''
  page = 0
  page_results = []
  results = []
  while page == 0 or len(page_results):
    page += 1
    r = requests.get('https://api.github.com/repos/{}/hooks'.format(repo), auth=(token, ''),
                     params={'page': page})
    if not r.ok:
      log.error('Error making github api request: {} {}'.format(r, r.content))
      return False
    page_results = json.loads(r.content)
    results = results + page_results
  return results


def get(token, repo, hook_id):
  '''
  Get a single hook from a repo

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local gh_hooks.get <token> <owner>/<repo> <hook_id>
  '''
  r = requests.get('https://api.github.com/repos/{}/hooks/{}'.format(repo, hook_id),
                   auth=(token, ''))
  if not r.ok:
    log.error('Error making github api request: {} {}'.format(r, r.content))
    return False
  return json.loads(r.content)


def remove(token, repo, hook_id):
  '''
  Remove a hook from a repo

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local gh_hooks.remove <token> <repo> <hook_id>
  '''
  r = requests.delete('https://api.github.com/repos/{}/hooks/{}'.format(repo, hook_id),
                      auth=(token, ''))
  if not r.ok:
    log.error('Error making github api request: {} {}'.format(r, r.content))
    return False
  return True


def add(token, repo, name, config, events, active=True):
  '''
  Add a hook to a GitHub repo

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local gh_hooks.add <token> <repo> hipchat '{"auth_token":"xxx"}' \
        '["commit_comment","download","fork","fork_apply","gollum","issues","issue_comment",
          "member","public","pull_request","pull_request_review_comment","push","watch"]'
  '''
  headers = {'Content-type': 'application/json'}
  log.info(type(events))
  payload = {"name": name, "config": config, "events": events, "active": active}
  log.info(json.dumps(payload))
  r = requests.post('https://api.github.com/repos/{}/hooks'.format(repo),
                    auth=(token, ''),
                    data=json.dumps(payload),
                    headers=headers)
  if not r.ok:
    log.error('Error making github api request: {} {}'.format(r, r.content))
    return None
  return json.loads(r.content)


def edit(token, repo, hook_id, patch):
  '''
  Edit a hook on a repo

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local gh_hooks.edit <token> <hook_id> '{"active":false}'
  '''
  headers = {'Content-type': 'application/json'}
  log.info(json.dumps(patch))
  r = requests.patch('https://api.github.com/repos/{}/hooks/{}'.format(repo, hook_id),
                     auth=(token, ''),
                     data=json.dumps(patch),
                     headers=headers)
  if not r.ok:
    log.error('Error making github api request: {} {}'.format(r, r.content))
    return None
  return json.loads(r.content)

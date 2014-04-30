'''
Module to manage collaborators on a Heroku app.

See https://devcenter.heroku.com/articles/platform-api-reference#collaborator
'''

import logging
log = logging.getLogger(__name__)
import requests
import json
import urllib


def list(token, app):
  '''
  List all collaborators for a Heroku app.
  See https://devcenter.heroku.com/articles/platform-api-reference#collaborator-list.

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local hk_collaborators.list <token> <app>
  '''
  r = requests.get('https://api.heroku.com/{}'.format(urllib.pathname2url(
      'apps/{}/collaborators'.format(app))),
      headers={'Authorization': 'Bearer ' + token,
               'Accept': 'application/vnd.heroku+json; version=3'})
  if not r.ok:
    raise CommandExecutionError('Error making Heroku API request: {}'.format(r))
  return json.loads(r.content)


def create(token, app, email):
  '''
  Create a new collaborator for a Heroku app.
  See https://devcenter.heroku.com/articles/platform-api-reference#collaborator-create.

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local hk_collaborators.add <token> <app> <email>
  '''
  headers = {'Content-type': 'application/json',
             'Authorization': 'Bearer ' + token,
             'Accept': 'application/vnd.heroku+json; version=3'}
  payload = {"user": email}
  r = requests.post('https://api.heroku.com/{}'.format(urllib.pathname2url(
      'apps/{}/collaborators'.format(app))),
      data=json.dumps(payload),
      headers=headers)
  if not r.ok:
    raise CommandExecutionError('Error making Heroku API request: {} {}'.format(r, r.content))
  return json.loads(r.content)


def delete(token, app, email):
  '''
  Remove a collaborator from a Heroku app.

  CLI Example:

  .. code-block:: bash

      sudo salt-call --local hk_collaborators.remove <token> <app> <email>
  '''
  r = requests.delete('https://api.heroku.com/{}'.format(urllib.pathname2url(
      'apps/{}/collaborators/{}'.format(app, email))),
      headers={'Authorization': 'Bearer ' + token,
               'Accept': 'application/vnd.heroku+json; version=3'})
  if not r.ok:
    raise CommandExecutionError('Error making Heroku API request: {} {}'.format(r, r.content))
  return json.loads(r.content)

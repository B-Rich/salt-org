'''
Module to manage repos on Github.

See http://developer.github.com/v3/repos/
'''

import logging
log = logging.getLogger(__name__)
import requests
import json

def list_org(token, org, type=all):
    '''
    List all repos in a Github organization

    CLI Example:

    .. code-block:: bash

        sudo salt-call --local gh_repos.list_org <token> <org> <type>
    '''
    page = 0
    page_results = []
    results = []
    while page == 0 or len(page_results):
        page += 1
        r = requests.get('https://api.github.com/orgs/{}/repos'.format(org), auth=(token, ''),
                         params={'page':page, 'type': type})
        if not r.ok:
            log.error('Error making github api request: {} {}'.format(r, r.content))
            return False
        page_results = json.loads(r.content)
        results = results + page_results
    return results

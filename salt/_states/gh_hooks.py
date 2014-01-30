'''
Management of repo hooks in GitHub
==================================

The gh_hooks module is used to create and manage GitHub repo hooks.

.. code-block:: yaml

    github-repo-hooks:
      gh_hooks.present:
        - token: xxxxx
        - name: Clever/clever-js
        - hooks:
          - name: hipchat
            config:
              auth_token: xxxx
              room: Clever-Dev
            events: ["commit_comment","download","fork"]
            active: True
        - strict: False
'''

import sys

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

def present(name, token, hooks, strict=False, dry_run=False):
    '''
    Ensure that a repo has certain hooks present

    name
        The name of the repo to manage hooks for.

    token
        OAuth token created by an admin for the organization.

    hooks
        List of hooks. Must contain required hook fields: `name`, `config` object, and `events` array.
        Config varies depending on the hook you're setting up.
        See http://developer.github.com/v3/repos/hooks/ for more information.

    strict
        Remove from the repo any hooks not enumerated in the state.

    dry_run
        Don't actually make any changes in GitHub. False by default.

    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    existing_hooks = __salt__['gh_hooks.list'](token, name)

    # If strict, remove existing hooks not enumerated in the state
    if strict:
        for existing_hook in existing_hooks:
            specified_hook = next((h for h in hooks if h["name"] == existing_hook["name"]), None)
            if specified_hook: continue
            if dry_run or __salt__['gh_hooks.remove'](token, name, existing_hook['id']):
                if 'remove' not in ret['changes']:
                    ret['changes']['remove'] = []
                ret['changes']['remove'].append(existing_hook)
            else:
                ret["result"] = False
                ret["comment"] = "Error removing hook: {}".format(existing_hook)
                return ret

    # Run through specified hooks, find/edit existing or create
    for specified_hook in hooks:
        existing_hook = next((h for h in existing_hooks if h["name"] == specified_hook["name"]), None)
        if existing_hook == None:
            if dry_run or __salt__['gh_hooks.add'](token, name, specified_hook["name"],
                                                   specified_hook["config"],
                                                   specified_hook["events"],
                                                   specified_hook["active"]):
                if 'add' not in ret['changes']:
                    ret['changes']['add'] = []
                ret['changes']['add'].append(specified_hook)
            else:
                ret["result"] = False
                ret["comment"] = "Error adding hook: {}".format(specified_hook)
                return ret
        else: # hook already exists, potentially patch
            patch = {}
            config_diff = DictDiffer(existing_hook['config'], specified_hook['config'])
            if len(config_diff.added()) > 0 or len(config_diff.removed()) > 0 or len(config_diff.changed()):
                patch['config'] = specified_hook['config']
            if existing_hook["active"] != specified_hook["active"]:
                patch["active"] = specified_hook["active"]
            if set(existing_hook["events"]) != set(specified_hook["events"]):
                patch["events"] = specified_hook["events"]
            if len(patch) == 0:
                continue
            if dry_run or __salt__['gh_hooks.edit'](token, name, existing_hook['id'], patch):
                if 'patch' not in ret['changes']:
                    ret['changes']['patch'] = []
                ret['changes']['patch'].append((name, patch))

    return ret

## salt-org

Use [Salt](http://www.saltstack.com) to manage accounts and settings for your organization.

## Why

You use config management to manage servers (user accounts, settings, etc.), so why not use it to manage your organization?

## How

Salt [execution modules](http://docs.saltstack.com/ref/modules/) are functions callable from the `salt` command-line utility.
You can string together lots of calls to different modules in an imperative fashion.
For example, here's how you'd use the [useradd](http://docs.saltstack.com/ref/modules/all/salt.modules.useradd.html#module-salt.modules.useradd) module to add a user to called "fred" to your local system:

```
sudo salt-call --local user.add fred <uid> <gid>
```

Salt [states](http://docs.saltstack.com/ref/states/) are a way to declaratively enforce configuration of software on machines.
For example, the following YAML config ensures that there's a `fred` user account on a server:

```
fred:
  user.present:
    - fullname: Fred Jones
    - shell: /bin/zsh
    - home: /home/fred
    - uid: 4000
    - gid: 4000
```

There are also states for managing [mongodb](http://docs.saltstack.com/ref/states/all/salt.states.mongodb_user.html), [mysql](http://docs.saltstack.com/ref/states/all/salt.states.mysql_user.html), [postgres](http://docs.saltstack.com/ref/states/all/salt.states.postgres_user.html), and [rabbitmq](http://docs.saltstack.com/ref/states/all/salt.states.rabbitmq_user.html) user accounts.

This repo aims to expose execution modules and states for managing users within

* Github teams
* AWS
* Google Apps
* Heroku
* Sentry

It also lets you manage other admin-level settings:

* Github repo hooks
* AWS IAM Group Policies

This opens up a lot of powerful patterns for managing these systems.

## Setup

Before any of these examples work you must install salt.
The salt [bootstrap](https://github.com/saltstack/salt-bootstrap) is an easy way to do this.
salt-org is currently tested against salt v0.17.4:

```
curl -L http://bootstrap.saltstack.org | sudo sh -s -- git v0.17.4
```

Test that it works by calling some builtin modules:

```
sudo salt-call --local test.ping
sudo salt-call --local user.list_users
```

Salt looks for configuration, custom modules, etc. in `/srv/salt` default.
If this directory don't exist, you can symlink this repo's `salt` directory to that location:

```
sudo ln -s `pwd`/salt /srv/salt
```

If you already have a `/srv/salt` directory, you should extend the contents of `/srv/salt` with the contents of this repo's `salt` directory.

Have salt load the custom modules/states in this repo:

```
sudo salt-call --local saltutil.sync_modules
sudo salt-call --local saltutil.sync_states
```

### Manage github teams (members, repos, permissions) declaratively V1

Create a file in this repo called `salt/github/init.sls`.
This file will describe the state of github you'd like to maintain.
Here's example content:

```yaml
github-Engineering:
  gh_team.present:
    - token: <generate and insert an oauth token from your admin account>
    - org: Clever
    - name: Engineers
    - members:
      - rgarcia
      ...
    - permission: push
    - repos:
      - Clever/clever-js
      ...
    - strict: True # remove any members/repos not specified above
```

Apply the state:

```
sudo salt-call --local state.sls github
```

This will run the state described in `salt/github/init.sls` and output what it changed.

### Manage github teams (members, repos, permissions) decalaritively V2

[Pillar](http://salt.readthedocs.org/en/latest/topics/pillar/) is salt's way of exposing structured data that can be used in state files.
Create a file in this repo called `pillar/github/init.sls`:

```yaml
github:
  token: <generate and insert an oauth token from your admin account>
  org: Clever
  teams:
    - name: Engineering
      permission: push
      members:
        - rgarcia
        ...
      repos:
        - Clever/clever-js
        ...
      strict: False
```

Create a pillar "top" file at `pillar/top.sls` that will load this data on any salt command:

```yaml
base:
  '*':
    - github
```

Salt lets you define states using jinja templates.
This means we can change the github state to iterate programatically over the data in pillar.
Create a templatized state file that `salt/github/init.sls`:

```yaml
{% for team in pillar.github.teams %}
github-{{ team.name }}:
  gh_team.present:
    - token: {{ pillar.github.token }}
    - org: {{ pillar.github.org }}
    - name: {{ team.name }}
    - members: {{ team.members }}
    - permission: {{ team.permission }}
    - repos: {{ team.repos }}
    - strict: {{ team.strict }}
{% endfor %}
```

Now run the state as usual:

```
sudo salt-call --local state.sls github
```

You can also templatize the data contained in pillar.
This is a useful technique to apply if, for example, you'd like to give a team push access to all public repos:

```yaml
github:
  token: <generate and insert an oauth token from your admin account>
  org: Clever
  teams:
    - name: Engineering
      permission: push
      members:
        - rgarcia
        ...
      repos:
        {% for repo in salt["gh_repos.list_org"]("<oauth token>", "Clever") %}
        - {{ repo.full_name }}
        {% endfor %}
      strict: False
```

Beyond calling salt modules to fill pillar data, you can also pull data from [external pillars](https://salt.readthedocs.org/en/latest/topics/development/external_pillars.html), including git, mongo, ldap, and others: http://docs.saltstack.com/ref/pillar/all/.

## TODO

- Github repo admin settings: hooks
- AWS IAM: users, their credentials, and groups
- Google Apps mgmt via the admin sdk: users, groups
- Heroku app collaborators
- Sentry

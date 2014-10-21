import unittest
import sys
import os
import responses

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../salt/_modules'))
import gh_team

# fake responses taken straight from github docs https://developer.github.com/v3/orgs/teams
FAKE_TEAMS = """[
  {
    "url": "https://api.github.com/teams/1",
    "name": "Owners",
    "id": 1
  }
]"""

FAKE_TEAM = """{
  "url": "https://api.github.com/teams/1",
  "name": "Owners",
  "id": 1,
  "permission": "admin",
  "members_count": 3,
  "repos_count": 10,
  "organization": {
    "login": "github",
    "id": 1,
    "url": "https://api.github.com/orgs/github",
    "avatar_url": "https://github.com/images/error/octocat_happy.gif"
  }
}"""

FAKE_TEAM_MEMBERS = """[
  {
    "login": "octocat",
    "id": 1,
    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
    "gravatar_id": "somehexcode",
    "url": "https://api.github.com/users/octocat",
    "html_url": "https://github.com/octocat",
    "followers_url": "https://api.github.com/users/octocat/followers",
    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
    "organizations_url": "https://api.github.com/users/octocat/orgs",
    "repos_url": "https://api.github.com/users/octocat/repos",
    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
    "received_events_url": "https://api.github.com/users/octocat/received_events",
    "type": "User",
    "site_admin": false
  }
]"""

FAKE_TEAM_REPOS = """[
  {
    "id": 1296269,
    "owner": {
      "login": "octocat",
      "id": 1,
      "avatar_url": "https://github.com/images/error/octocat_happy.gif",
      "gravatar_id": "somehexcode",
      "url": "https://api.github.com/users/octocat",
      "html_url": "https://github.com/octocat",
      "followers_url": "https://api.github.com/users/octocat/followers",
      "following_url": "https://api.github.com/users/octocat/following{/other_user}",
      "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
      "organizations_url": "https://api.github.com/users/octocat/orgs",
      "repos_url": "https://api.github.com/users/octocat/repos",
      "events_url": "https://api.github.com/users/octocat/events{/privacy}",
      "received_events_url": "https://api.github.com/users/octocat/received_events",
      "type": "User",
      "site_admin": false
    },
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "description": "This your first repo!",
    "private": false,
    "fork": false,
    "url": "https://api.github.com/repos/octocat/Hello-World",
    "html_url": "https://github.com/octocat/Hello-World",
    "clone_url": "https://github.com/octocat/Hello-World.git",
    "git_url": "git://github.com/octocat/Hello-World.git",
    "ssh_url": "git@github.com:octocat/Hello-World.git",
    "svn_url": "https://svn.github.com/octocat/Hello-World",
    "mirror_url": "git://git.example.com/octocat/Hello-World",
    "homepage": "https://github.com",
    "language": null,
    "forks_count": 9,
    "stargazers_count": 80,
    "watchers_count": 80,
    "size": 108,
    "default_branch": "master",
    "open_issues_count": 0,
    "has_issues": true,
    "has_wiki": true,
    "has_pages": false,
    "has_downloads": true,
    "pushed_at": "2011-01-26T19:06:43Z",
    "created_at": "2011-01-26T19:01:12Z",
    "updated_at": "2011-01-26T19:14:43Z",
    "permissions": {
      "admin": false,
      "push": false,
      "pull": true
    }
  }
]"""


class GHTeamTest(unittest.TestCase):

  @responses.activate
  def test_list(self):
    responses.add(responses.GET, 'https://api.github.com/orgs/:org/teams',
                  body=FAKE_TEAMS, status=200, content_type='application/json')
    resp = gh_team.list("token", ":org")
    self.assertEqual(resp[0]["name"], "Owners")

  @responses.activate
  def test_list_false(self):
    responses.add(responses.GET, 'https://api.github.com/orgs/:org/teams', status=400)
    resp = gh_team.list("token", ":org")
    self.assertEqual(resp, False)

  @responses.activate
  def test_add(self):
    responses.add(responses.POST, 'https://api.github.com/orgs/:org/teams',
                  body=FAKE_TEAM, status=200, content_type='application/json')
    resp = gh_team.add("token", ":org", "Owners", "admin")
    self.assertEqual(resp["name"], "Owners")

  @responses.activate
  def test_add_none(self):
    responses.add(responses.POST, 'https://api.github.com/orgs/:org/teams', status=400)
    resp = gh_team.add("token", ":org", "Owners", "admin")
    self.assertEqual(resp, None)

  @responses.activate
  def test_get(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1',
                  body=FAKE_TEAM, status=200, content_type='application/json')
    resp = gh_team.get("token", "1")
    self.assertEqual(resp["name"], "Owners")

  @responses.activate
  def test_get_none(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1', status=400)
    resp = gh_team.get("token", "1")
    self.assertEqual(resp, None)

  @responses.activate
  def test_remove_true(self):
    responses.add(responses.DELETE, 'https://api.github.com/teams/1', status=204)
    resp = gh_team.remove("token", "1")
    self.assertEqual(resp, True)

  @responses.activate
  def test_remove_false(self):
    responses.add(responses.DELETE, 'https://api.github.com/teams/1', status=400)
    resp = gh_team.remove("token", "1")
    self.assertEqual(resp, False)

  @responses.activate
  def test_edit(self):
    responses.add(responses.PATCH, 'https://api.github.com/teams/1',
                  body=FAKE_TEAM, status=200, content_type='application/json')
    resp = gh_team.edit("token", "1", "name", "permission")
    self.assertEqual(resp["name"], "Owners")

  @responses.activate
  def test_edit_none(self):
    responses.add(responses.PATCH, 'https://api.github.com/teams/1', status=400)
    resp = gh_team.edit("token", "1", "name", "permission")
    self.assertEqual(resp, None)

  @responses.activate
  def test_list_members(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1/members',
                  body=FAKE_TEAM_MEMBERS, status=200, content_type='application/json')
    resp = gh_team.list_members("token", "1")
    self.assertEqual(resp[0]["login"], "octocat")

  @responses.activate
  def test_list_members_none(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1/members', status=400)
    resp = gh_team.list_members("token", "1")
    self.assertEqual(resp, None)

  @responses.activate
  def test_list_repos(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1/repos', status=400)
    resp = gh_team.list_repos("token", "1")
    self.assertEqual(resp, None)

  @responses.activate
  def test_get_repo_true(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=204, content_type='application/json')
    resp = gh_team.get_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, True)

  @responses.activate
  def test_get_repo_false(self):
    responses.add(responses.GET, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=404, content_type='application/json')
    resp = gh_team.get_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, False)

  @responses.activate
  def test_add_repo_true(self):
    responses.add(responses.PUT, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=204, content_type='application/json')
    resp = gh_team.add_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, True)

  @responses.activate
  def test_add_repo_false(self):
    responses.add(responses.PUT, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=400, content_type='application/json')
    resp = gh_team.add_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, False)

  @responses.activate
  def test_remove_repo_true(self):
    responses.add(responses.DELETE, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=204, content_type='application/json')
    resp = gh_team.remove_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, True)

  @responses.activate
  def test_remove_repo_false(self):
    responses.add(responses.DELETE, 'https://api.github.com/teams/1/repos/:owner/:repo',
                  status=400, content_type='application/json')
    resp = gh_team.remove_repo("token", "1", ":owner/:repo")
    self.assertEqual(resp, False)

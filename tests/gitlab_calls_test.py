# python
import pytest
import requests
from types import SimpleNamespace

# Import function to test using relative import (package parent has __init__.py)
from gitlab_calls import grant_user_role


class MockResponse:
    def __init__(self, json_data=None, status_code=200, headers=None):
        self._json = json_data if json_data is not None else {}
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")


def test_invalid_role_raises_value_error():
    with pytest.raises(ValueError):
        grant_user_role('someuser', 'some/group', 'not_a_role')


def test_user_not_found_raises_exception(monkeypatch):
    def fake_get(url, headers=None, params=None):
        # Simulate users endpoint returning empty list
        if '/api/v4/users' in url:
            return MockResponse(json_data=[], status_code=200)
        return MockResponse(json_data={}, status_code=200)

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(Exception) as exc:
        grant_user_role('no_user', 'some/group', 'developer')

    assert "no_user" in str(exc.value)


def test_project_update_existing_member(monkeypatch):
    # Prepare responses for the sequence of requests
    def fake_get(url, headers=None, params=None):
        if '/api/v4/users' in url:
            return MockResponse(json_data=[{'id': 1}], status_code=200)
        if '/api/v4/projects/' in url:
            # return project info
            return MockResponse(json_data={'id': 2}, status_code=200)
        return MockResponse(json_data={}, status_code=200)

    def fake_put(url, headers=None, json=None):
        # Simulate updating existing member successfully
        if '/api/v4/projects/2/members/1' in url:
            return MockResponse(json_data={'member': 'updated'}, status_code=200)
        return MockResponse(json_data={}, status_code=200)

    def fake_post(url, headers=None, json=None):
        # Should not be called in this scenario, but return a default success
        return MockResponse(json_data={'member': 'created'}, status_code=201)

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.setattr(requests, 'put', fake_put)
    monkeypatch.setattr(requests, 'post', fake_post)

    result = grant_user_role('user1', 'group/repo', 'developer')
    assert result == {'member': 'updated'}


def test_project_add_member_on_404(monkeypatch):
    # Prepare responses for the sequence of requests
    def fake_get(url, headers=None, params=None):
        if '/api/v4/users' in url:
            return MockResponse(json_data=[{'id': 10}], status_code=200)
        if '/api/v4/projects/' in url:
            return MockResponse(json_data={'id': 20}, status_code=200)
        return MockResponse(json_data={}, status_code=200)

    def fake_put(url, headers=None, json=None):
        # Simulate member not found => 404
        if '/api/v4/projects/20/members/10' in url:
            return MockResponse(json_data={'message': 'Not Found'}, status_code=404)
        return MockResponse(json_data={}, status_code=200)

    def fake_post(url, headers=None, json=None):
        if '/api/v4/projects/20/members' in url:
            return MockResponse(json_data={'member': 'created'}, status_code=201)
        return MockResponse(json_data={}, status_code=200)

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.setattr(requests, 'put', fake_put)
    monkeypatch.setattr(requests, 'post', fake_post)

    result = grant_user_role('user10', 'group/repo', 'maintainer')
    assert result == {'member': 'created'}
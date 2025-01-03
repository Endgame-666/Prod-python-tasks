import pytest
import typing as tp
from itertools import count

from starlette.testclient import TestClient
from music import app

client = TestClient(app)

API_GET_URLS = [
    '/api/v1/tracks/all',
    '/api/v1/tracks/1',
    '/api/v1/tracks/search',
]

API_POST_URLS = [
    '/api/v1/tracks/add_track',
]

API_DELETE_URLS = [
    '/api/v1/tracks/1'
]

URL_AND_CALL_FUNC: list[tuple[str, tp.Any]] = [
    *[(item, client.get) for item in API_GET_URLS],
    *[(item, client.post) for item in API_POST_URLS],
    *[(item, client.delete) for item in API_DELETE_URLS],
]

@pytest.fixture(autouse=True)
def reset_state():
    """teardown"""
    global track_id_counter, tracks_by_id
    track_id_counter = count(start=1)
    tracks_by_id.clear()


track_id_counter = count(start=1)
tracks_by_id = {}


def register_user_and_obtain_token(name: str, age: int) -> str:
    response = client.post(
        '/api/v1/registration/register_user',
        json={
            'name': name,
            'age': age,
        }
    )

    return response.json()['token']


@pytest.fixture
def api_token() -> str:
    return register_user_and_obtain_token('Artur', 21)


class TestToken:
    @pytest.mark.parametrize(
        'url,call_func',
        URL_AND_CALL_FUNC,
    )
    def test_missing_token(self, url: str, call_func: tp.Any) -> None:
        response = call_func(url)
        assert response.status_code == 401
        assert response.json() == {'detail': 'Missing token'}

    @pytest.mark.parametrize(
        'url,call_func',
        URL_AND_CALL_FUNC
    )
    @pytest.mark.parametrize(
        'incorrect_token',
        ['some_fake_token', 'ab4f' * 10]
    )
    def test_incorrect_token(self, url: str, call_func: tp.Any, incorrect_token: str) -> None:
        response = call_func(url, headers={'x-token': incorrect_token})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Incorrect token'}


class TestBadArguments:
    def test_add_missing_required_fields(self, api_token: str) -> None:
        response = client.post(
            '/api/v1/tracks/add_track',
            headers={'x-token': api_token},
            json={
                'artist': 'Hirasawa Susumu',
            }
        )
        assert response.status_code == 422
        assert response.json().get('detail', None) is not None

        response = client.post(
            '/api/v1/tracks/add_track',
            headers={'x-token': api_token},
            json={
                'name': 'Imagine',
            }
        )
        assert response.status_code == 422
        assert response.json().get('detail', None) is not None

    def test_search_missing_params(self, api_token: str) -> None:
        response = client.get(
            '/api/v1/tracks/search',
            headers={'x-token': api_token}
        )
        assert response.status_code == 422
        assert response.json() == {'detail': 'You should specify at least one search argument'}

    def test_get_track_invalid_id(self, api_token: str) -> None:
        response = client.get(
            '/api/v1/tracks/1',
            headers={'x-token': api_token}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Invalid track_id'}

    def test_remove_track_invalid_id(self, api_token: str) -> None:
        response = client.delete(
            '/api/v1/tracks/1',
            headers={'x-token': api_token}
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Invalid track_id'}


class TestNormalBehavior:
    def test_registration(self) -> None:
        token1 = register_user_and_obtain_token('Max', 33)
        token2 = register_user_and_obtain_token('Daria', 5)
        assert len(token1) == 40
        assert len(token2) == 40
        assert token1 != token2

    def test_all_empty(self, api_token: str) -> None:
        response = client.get(
            '/api/v1/tracks/all',
            headers={'x-token': api_token}
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_search_empty(self, api_token: str) -> None:
        response = client.get(
            '/api/v1/tracks/search?name=Test',
            headers={'x-token': api_token}
        )
        assert response.status_code == 200
        assert response.json() == {'track_ids': []}

        response = client.get(
            '/api/v1/tracks/search?artist=Test',
            headers={'x-token': api_token}
        )
        assert response.status_code == 200
        assert response.json() == {'track_ids': []}

    def test_add_find_find_all(self, api_token: str) -> None:
        response = client.post(
            '/api/v1/tracks/add_track',
            headers={'x-token': api_token},
            json={
                'name': 'Clint Eastwood',
                'artist': 'Gorillaz'
            }
        )
        assert response.status_code == 201
        assert response.json() == {'track_id': 1}

        response = client.post(
            '/api/v1/tracks/add_track',
            headers={'x-token': api_token},
            json={
                'name': '2020',
                'artist': 'Suuns',
                'year': 2013,
                'genres': ['Krautrock', 'Art Punk']
            }
        )
        assert response.status_code == 201
        assert response.json() == {'track_id': 2}

        response = client.get('/api/v1/tracks/1', headers={'x-token': api_token})
        assert response.status_code == 200
        assert response.json() == {
            'name': 'Clint Eastwood',
            'artist': 'Gorillaz'
        }

        response = client.get('/api/v1/tracks/2', headers={'x-token': api_token})
        assert response.status_code == 200
        assert response.json() == {
            'name': '2020',
            'artist': 'Suuns'
        }
        response = client.get('/api/v1/tracks/all', headers={'x-token': api_token})
        assert response.status_code == 200
        assert response.json() == [
            {
                'name': 'Clint Eastwood',
                'artist': 'Gorillaz',
                'year': None,
                'genres': []
            },
            {
                'name': '2020',
                'artist': 'Suuns',
                'year': 2013,
                'genres': ['Krautrock', 'Art Punk']
            }
        ]

    def test_add_remove_get(self, api_token: str) -> None:
        response = client.post(
            '/api/v1/tracks/add_track',
            headers={'x-token': api_token},
            json={
                'name': 'This I Love',
                'artist': "Guns N'Roses"
            }
        )
        assert response.status_code == 201
        track_id = response.json().get('track_id')
        assert track_id is not None

        response = client.delete(f'/api/v1/tracks/{track_id}', headers={'x-token': api_token})
        assert response.status_code == 200
        assert response.json() == {'status': 'track removed'}

        response = client.get(f'/api/v1/tracks/{track_id}', headers={'x-token': api_token})
        assert response.status_code == 404
        assert response.json() == {'detail': 'Invalid track_id'}

    def test_add_search_delete(self, api_token: str) -> None:
        track_ids = []

        for name in ['Perfect', 'Cold Coffee', 'Photograph']:
            response = client.post(
                '/api/v1/tracks/add_track',
                headers={'x-token': api_token},
                json={
                    'name': name,
                    'artist': 'Ed Sheeran'
                }
            )
            assert response.status_code == 201
            track_id = response.json().get('track_id')
            assert track_id is not None
            track_ids.append(track_id)

        response = client.get(
            f'/api/v1/tracks/search?name=Photograph',
            headers={'x-token': api_token}
        )
        assert response.status_code == 200
        assert response.json() == {'track_ids': [track_ids[-1]]}

        response = client.get(
            f'/api/v1/tracks/search?artist=Ed%20Sheeran',
            headers={'x-token': api_token}
        )
        assert response.status_code == 200
        assert set(response.json()['track_ids']) == set(track_ids)

        response = client.delete(f'/api/v1/tracks/{track_ids[1]}', headers={'x-token': api_token})
        assert response.status_code == 200
        assert response.json() == {'status': 'track removed'}

        response = client.get(
            f'/api/v1/tracks/search?artist=Ed%20Sheeran',
            headers={'x-token': api_token}
        )
        remaining_track_ids = track_ids[:1] + track_ids[2:]
        assert set(response.json()['track_ids']) == set(remaining_track_ids)

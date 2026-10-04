import pytest
from fastapi.testclient import TestClient


def create_payload(client: TestClient, headers: dict) -> dict:
    players = []
    for name in ("Ana", "Rubén", "Zoe"):
        response = client.post("/api/admin/players", headers=headers, json={"display_name": name})
        assert response.status_code == 201
        players.append(response.json()["id"])
    return {
        "game_slug": "catan",
        "played_at": "2026-10-04T18:00:00Z",
        "results": [
            {
                "player_id": player_id, "score": 10 if index == 0 else 5,
                "position": index + 1, "is_winner": index == 0,
                "catan": {
                    "cities": 2, "settlements": 1, "roads": 7,
                    "longest_road": index == 0, "largest_army": index == 1,
                    "victory_point_cards": 3 if index == 0 else 0,
                },
            }
            for index, player_id in enumerate(players)
        ],
    }


def test_catan_details_create_read_update_and_game_change(
    authenticated_client: TestClient, csrf_token: str,
) -> None:
    client = authenticated_client
    headers = {"X-CSRF-Token": csrf_token}
    payload = create_payload(client, headers)
    response = client.post("/api/admin/matches", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    match_id = response.json()["id"]
    for result in response.json()["results"]:
        expected = next(r for r in payload["results"] if r["player_id"] == result["player"]["id"])
        assert result["catan"] == expected["catan"]
    assert client.get("/api/admin/matches?game=catan").json()[0]["results"][0]["catan"] is not None
    before = client.get("/api/games/catan/rankings").json()
    for result in payload["results"]:
        result["catan"].update(cities=0, roads=0, largest_army=False)
    response = client.put(f"/api/admin/matches/{match_id}", headers=headers, json=payload)
    assert response.status_code == 200, response.text
    stored = client.get(f"/api/admin/matches/{match_id}").json()
    assert all(r["catan"]["cities"] == 0 and r["catan"]["largest_army"] is False for r in stored["results"])
    after = client.get("/api/games/catan/rankings").json()
    assert after["ranking"][0]["catan"]["cities"]["total"] == 0
    assert after["ranking"][0]["catan"]["roads"]["total"] == 0
    for previous, current in zip(before["ranking"], after["ranking"], strict=True):
        assert {k: v for k, v in previous.items() if k != "catan"} == {
            k: v for k, v in current.items() if k != "catan"
        }
    payload["game_slug"] = "flipseven"
    for result in payload["results"]:
        result["catan"] = None
    response = client.put(f"/api/admin/matches/{match_id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert all(r["catan"] is None for r in response.json()["results"])


@pytest.mark.parametrize("field,value", [
    ("cities", -1), ("settlements", -1), ("roads", -1),
    ("victory_point_cards", -1), ("cities", 1.5),
    ("longest_road", "yes"), ("largest_army", 1),
])
def test_invalid_catan_details_are_rejected(
    authenticated_client: TestClient, csrf_token: str, field: str, value,
) -> None:
    client = authenticated_client
    headers = {"X-CSRF-Token": csrf_token}
    payload = create_payload(client, headers)
    payload["results"][0]["catan"][field] = value
    assert client.post("/api/admin/matches", headers=headers, json=payload).status_code == 422
    assert client.get("/api/admin/matches").json() == []


def test_catan_details_rejected_for_other_games(
    authenticated_client: TestClient, csrf_token: str,
) -> None:
    headers = {"X-CSRF-Token": csrf_token}
    payload = create_payload(authenticated_client, headers)
    payload["game_slug"] = "flipseven"
    response = authenticated_client.post("/api/admin/matches", headers=headers, json=payload)
    assert response.status_code == 422
    assert response.json()["detail"] == "Catán details are only allowed for Catán matches"


def test_catan_player_statistics_use_only_recorded_non_deleted_game_results(
    authenticated_client: TestClient, csrf_token: str,
) -> None:
    client = authenticated_client
    headers = {"X-CSRF-Token": csrf_token}
    payload = create_payload(client, headers)
    url = "/api/games/catan/rankings"
    empty = client.get(url).json()["ranking"][0]["catan"]
    assert empty["matches_with_details"] == 0
    assert empty["cities"] == {"recorded_matches": 0, "total": 0, "average": None, "best": None}
    assert empty["longest_road"]["rate"] is None
    first = client.post("/api/admin/matches", headers=headers, json=payload)
    assert first.status_code == 201
    for result in payload["results"]:
        result["catan"].update(cities=0, roads=None, longest_road=False, largest_army=None)
    second = client.post("/api/admin/matches", headers=headers, json=payload)
    assert second.status_code == 201
    for result in payload["results"]:
        result["catan"] = None
    assert client.post("/api/admin/matches", headers=headers, json=payload).status_code == 201
    data = client.get(url).json()
    leader = data["ranking"][0]
    stats = leader["catan"]
    assert leader["matches_played"] == 3
    assert stats["matches_with_details"] == 2
    assert stats["cities"] == {"recorded_matches": 2, "total": 2, "average": 1.0, "best": 2}
    assert stats["roads"] == {"recorded_matches": 1, "total": 7, "average": 7.0, "best": 7}
    assert stats["settlements"]["total"] == 2
    assert stats["victory_point_cards"]["total"] == 6
    assert stats["longest_road"] == {"recorded_matches": 2, "times_held": 1, "rate": 50.0}
    assert stats["largest_army"] == {"recorded_matches": 1, "times_held": 0, "rate": 0.0}
    payload["game_slug"] = "flipseven"
    assert client.post("/api/admin/matches", headers=headers, json=payload).status_code == 201
    assert client.get(url).json() == data
    assert all(row["catan"] is None for row in client.get("/api/games/flipseven/rankings").json()["ranking"])
    assert client.delete(f"/api/admin/matches/{first.json()['id']}", headers=headers).status_code == 204
    stats = client.get(url).json()["ranking"][0]["catan"]
    assert stats["matches_with_details"] == 1
    assert stats["cities"]["average"] == 0
    assert stats["roads"]["average"] is None
    assert stats["longest_road"]["times_held"] == 0

from fastapi.testclient import TestClient


def _create_player(client: TestClient, csrf_token: str, name: str) -> str:
    response = client.post(
        "/api/admin/players",
        headers={"X-CSRF-Token": csrf_token},
        json={"display_name": name, "nickname": None},
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def _create_players(client: TestClient, csrf_token: str, count: int) -> list[str]:
    return [
        _create_player(client, csrf_token, f"Player {index}")
        for index in range(1, count + 1)
    ]


def _catan_payload(player_ids: list[str]) -> dict:
    return {
        "game_slug": "catan",
        "played_at": "2026-05-23T20:30:00Z",
        "notes": "Catán night",
        "results": [
            {"player_id": player_ids[0], "score": 10, "position": 1, "is_winner": True},
            {"player_id": player_ids[1], "score": 8, "position": 2, "is_winner": False},
            {"player_id": player_ids[2], "score": 6, "position": 3, "is_winner": False},
        ],
    }


def test_matches_require_auth(client: TestClient) -> None:
    response = client.get("/api/admin/matches")

    assert response.status_code == 401


def test_create_match_requires_csrf(authenticated_client: TestClient) -> None:
    response = authenticated_client.post("/api/admin/matches", json={})

    assert response.status_code == 403


def test_admin_can_create_list_update_and_soft_delete_catan_match(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 4)

    create_response = authenticated_client.post(
        "/api/admin/matches",
        headers={"X-CSRF-Token": csrf_token},
        json=_catan_payload(player_ids[:3]),
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["game"]["slug"] == "catan"
    assert created["notes"] == "Catán night"
    assert len(created["results"]) == 3
    assert sum(1 for result in created["results"] if result["is_winner"]) == 1

    list_response = authenticated_client.get("/api/admin/matches?game=catan")
    assert list_response.status_code == 200
    assert [match["id"] for match in list_response.json()] == [created["id"]]

    update_payload = _catan_payload([player_ids[0], player_ids[2], player_ids[3]])
    update_payload["notes"] = "Updated Catán night"
    update_payload["results"][0]["score"] = 12
    update_response = authenticated_client.put(
        f"/api/admin/matches/{created['id']}",
        headers={"X-CSRF-Token": csrf_token},
        json=update_payload,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["notes"] == "Updated Catán night"
    assert len(updated["results"]) == 3
    assert max(result["score"] for result in updated["results"]) == 12

    delete_response = authenticated_client.delete(
        f"/api/admin/matches/{created['id']}", headers={"X-CSRF-Token": csrf_token}
    )
    assert delete_response.status_code == 204
    assert (
        authenticated_client.get(f"/api/admin/matches/{created['id']}").status_code
        == 404
    )
    assert authenticated_client.get("/api/admin/matches").json() == []


def test_create_catan_match_validates_minimum_players(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 2)
    payload = _catan_payload([player_ids[0], player_ids[1], player_ids[1]])
    payload["results"] = payload["results"][:2]

    response = authenticated_client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )

    assert response.status_code == 422
    assert "at least 3 players" in response.json()["detail"]


def test_create_match_rejects_repeated_players(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 3)
    payload = _catan_payload([player_ids[0], player_ids[1], player_ids[1]])

    response = authenticated_client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Players cannot be repeated"


def test_create_match_rejects_multiple_winners(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 3)
    payload = _catan_payload(player_ids)
    payload["results"][1]["is_winner"] = True

    response = authenticated_client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Exactly one winner is required"


def test_create_catan_match_requires_positions(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 3)
    payload = _catan_payload(player_ids)
    payload["results"][0]["position"] = None

    response = authenticated_client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"] == "Catán matches require positions for every player"
    )


def test_create_flipseven_match_allows_missing_positions(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    player_ids = _create_players(authenticated_client, csrf_token, 2)
    payload = {
        "game_slug": "flipseven",
        "played_at": "2026-05-23T21:30:00Z",
        "notes": None,
        "results": [
            {"player_id": player_ids[0], "score": 250, "is_winner": True},
            {"player_id": player_ids[1], "score": 175, "is_winner": False},
        ],
    }

    response = authenticated_client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )

    assert response.status_code == 201
    assert response.json()["game"]["slug"] == "flipseven"
    assert all(result["position"] is None for result in response.json()["results"])

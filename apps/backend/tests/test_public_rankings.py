from fastapi.testclient import TestClient


def _create_player(client: TestClient, csrf_token: str, name: str) -> str:
    response = client.post(
        "/api/admin/players",
        headers={"X-CSRF-Token": csrf_token},
        json={"display_name": name, "nickname": None},
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def _create_match(client: TestClient, csrf_token: str, payload: dict) -> dict:
    response = client.post(
        "/api/admin/matches", headers={"X-CSRF-Token": csrf_token}, json=payload
    )
    assert response.status_code == 201
    return dict(response.json())


def test_public_games_endpoints(client: TestClient) -> None:
    games_response = client.get("/api/games")
    assert games_response.status_code == 200
    assert [game["slug"] for game in games_response.json()] == ["catan", "flipseven"]

    catan_response = client.get("/api/games/catan")
    assert catan_response.status_code == 200
    assert catan_response.json()["display_name"] == "Catán"

    missing_response = client.get("/api/games/unknown")
    assert missing_response.status_code == 404


def test_catan_ranking_uses_catan_strategy(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    ruben = _create_player(authenticated_client, csrf_token, "Rubén")
    ana = _create_player(authenticated_client, csrf_token, "Ana")
    zoe = _create_player(authenticated_client, csrf_token, "Zoe")

    _create_match(
        authenticated_client,
        csrf_token,
        {
            "game_slug": "catan",
            "played_at": "2026-05-20T20:30:00Z",
            "notes": None,
            "results": [
                {"player_id": ruben, "score": 10, "position": 1, "is_winner": True},
                {"player_id": ana, "score": 8, "position": 2, "is_winner": False},
                {"player_id": zoe, "score": 6, "position": 3, "is_winner": False},
            ],
        },
    )
    _create_match(
        authenticated_client,
        csrf_token,
        {
            "game_slug": "catan",
            "played_at": "2026-05-21T20:30:00Z",
            "notes": None,
            "results": [
                {"player_id": ruben, "score": 6, "position": 3, "is_winner": False},
                {"player_id": ana, "score": 12, "position": 1, "is_winner": True},
                {"player_id": zoe, "score": 9, "position": 2, "is_winner": False},
            ],
        },
    )

    response = authenticated_client.get("/api/games/catan/rankings")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == {"total_players": 3, "total_matches": 2}
    assert [row["player_name"] for row in data["ranking"]] == ["Ana", "Rubén", "Zoe"]
    assert data["ranking"][0]["wins"] == 1
    assert data["ranking"][0]["average_points"] == 10.0
    assert data["ranking"][0]["win_rate"] == 50.0


def test_flipseven_ranking_uses_flipseven_strategy(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    ruben = _create_player(authenticated_client, csrf_token, "Rubén")
    ana = _create_player(authenticated_client, csrf_token, "Ana")

    _create_match(
        authenticated_client,
        csrf_token,
        {
            "game_slug": "flipseven",
            "played_at": "2026-05-20T20:30:00Z",
            "notes": None,
            "results": [
                {"player_id": ruben, "score": 100, "is_winner": True},
                {"player_id": ana, "score": 200, "is_winner": False},
            ],
        },
    )
    _create_match(
        authenticated_client,
        csrf_token,
        {
            "game_slug": "flipseven",
            "played_at": "2026-05-21T20:30:00Z",
            "notes": None,
            "results": [
                {"player_id": ruben, "score": 50, "is_winner": False},
                {"player_id": ana, "score": 75, "is_winner": True},
            ],
        },
    )

    response = authenticated_client.get("/api/games/flipseven/rankings")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == {"total_players": 2, "total_matches": 2}
    assert [row["player_name"] for row in data["ranking"]] == ["Ana", "Rubén"]
    assert data["ranking"][0]["wins"] == 1
    assert data["ranking"][0]["total_points"] == 275


def test_soft_deleted_matches_are_excluded_from_rankings(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    p1 = _create_player(authenticated_client, csrf_token, "Player 1")
    p2 = _create_player(authenticated_client, csrf_token, "Player 2")
    p3 = _create_player(authenticated_client, csrf_token, "Player 3")
    match = _create_match(
        authenticated_client,
        csrf_token,
        {
            "game_slug": "catan",
            "played_at": "2026-05-20T20:30:00Z",
            "notes": None,
            "results": [
                {"player_id": p1, "score": 10, "position": 1, "is_winner": True},
                {"player_id": p2, "score": 8, "position": 2, "is_winner": False},
                {"player_id": p3, "score": 6, "position": 3, "is_winner": False},
            ],
        },
    )

    delete_response = authenticated_client.delete(
        f"/api/admin/matches/{match['id']}", headers={"X-CSRF-Token": csrf_token}
    )
    assert delete_response.status_code == 204

    response = authenticated_client.get("/api/games/catan/rankings")
    assert response.status_code == 200
    assert response.json()["summary"] == {"total_players": 0, "total_matches": 0}
    assert response.json()["ranking"] == []

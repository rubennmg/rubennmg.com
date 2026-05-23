from fastapi.testclient import TestClient


def test_players_require_auth(client: TestClient) -> None:
    response = client.get("/api/admin/players")

    assert response.status_code == 401


def test_create_player_requires_csrf(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/admin/players",
        json={"display_name": "Rubén", "nickname": "Rubenmg"},
    )

    assert response.status_code == 403


def test_admin_can_create_list_update_and_disable_player(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    create_response = authenticated_client.post(
        "/api/admin/players",
        headers={"X-CSRF-Token": csrf_token},
        json={"display_name": "Rubén", "nickname": "Rubenmg"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["display_name"] == "Rubén"
    assert created["nickname"] == "Rubenmg"
    assert created["is_active"] is True

    list_response = authenticated_client.get("/api/admin/players")
    assert list_response.status_code == 200
    assert [player["display_name"] for player in list_response.json()] == ["Rubén"]

    update_response = authenticated_client.put(
        f"/api/admin/players/{created['id']}",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "display_name": "Rubén M.",
            "nickname": None,
            "avatar_url": "https://example.com/avatar.png",
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["display_name"] == "Rubén M."
    assert updated["nickname"] is None
    assert updated["avatar_url"] == "https://example.com/avatar.png"

    status_response = authenticated_client.patch(
        f"/api/admin/players/{created['id']}/status",
        headers={"X-CSRF-Token": csrf_token},
        json={"is_active": False},
    )
    assert status_response.status_code == 200
    assert status_response.json()["is_active"] is False


def test_create_player_rejects_duplicate_display_name(
    authenticated_client: TestClient, csrf_token: str
) -> None:
    payload = {"display_name": "Rubén", "nickname": None}
    first_response = authenticated_client.post(
        "/api/admin/players", headers={"X-CSRF-Token": csrf_token}, json=payload
    )
    assert first_response.status_code == 201

    duplicate_response = authenticated_client.post(
        "/api/admin/players", headers={"X-CSRF-Token": csrf_token}, json=payload
    )
    assert duplicate_response.status_code == 409

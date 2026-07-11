"""Integration tests for the Task HTTP API."""


async def test_create_and_fetch_task(api_client) -> None:
    resp = await api_client.post("/api/v1/tasks", json={"title": "write docs", "description": "d"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "write docs"
    assert body["status"] == "open"

    task_id = body["id"]
    got = await api_client.get(f"/api/v1/tasks/{task_id}")
    assert got.status_code == 200
    assert got.json()["id"] == task_id


async def test_list_tasks(api_client) -> None:
    await api_client.post("/api/v1/tasks", json={"title": "a"})
    await api_client.post("/api/v1/tasks", json={"title": "b"})
    resp = await api_client.get("/api/v1/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_transition_task(api_client) -> None:
    created = (await api_client.post("/api/v1/tasks", json={"title": "a"})).json()
    resp = await api_client.post(
        f"/api/v1/tasks/{created['id']}/transition",
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


async def test_illegal_transition_returns_400(api_client) -> None:
    created = (await api_client.post("/api/v1/tasks", json={"title": "a"})).json()
    resp = await api_client.post(
        f"/api/v1/tasks/{created['id']}/transition",
        json={"status": "done"},
    )
    assert resp.status_code == 400


async def test_get_missing_returns_404(api_client) -> None:
    resp = await api_client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404

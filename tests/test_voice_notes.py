import pytest

@pytest.mark.asyncio
async def test_voice_pipeline(client):
    r = await client.post("/api/jobs", json={"title": "Standup", "hint": "Deploy today. Fix bug 42."})
    jid = r.json()["id"]
    g = await client.get(f"/api/jobs/{jid}")
    assert g.status_code == 200
    body = g.json()
    assert body["transcript"]
    assert body["summary"]
    assert body["action_items"]

# tests/test_teacher_tasks.py
"""Tests for /api/v1/teacher-tasks/* — My Tasks (standalone teacher task manager)."""


def _signup(client, email="teacher@test.com"):
    r = client.post(
        "/auths/signup", json={"email": email, "name": "Teacher", "password": "pass1234!"}
    )
    assert r.status_code == 200
    return r.json()["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestCrud:
    def test_create_and_list_task(self, client):
        token = _signup(client)
        r = client.post(
            "/api/v1/teacher-tasks",
            json={"title": "Grade quizzes", "priority": "high", "category": "assessment"},
            headers=_auth(token),
        )
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Grade quizzes"
        assert data["priority"] == "high"
        assert data["category"] == "assessment"
        assert data["status"] == "todo"

        r = client.get("/api/v1/teacher-tasks", headers=_auth(token))
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_create_requires_auth(self, client):
        r = client.post("/api/v1/teacher-tasks", json={"title": "x"})
        assert r.status_code == 403

    def test_create_defaults(self, client):
        token = _signup(client, "defaults@test.com")
        r = client.post(
            "/api/v1/teacher-tasks", json={"title": "Untitled defaults"}, headers=_auth(token)
        )
        assert r.status_code == 200
        data = r.json()
        assert data["priority"] == "medium"
        assert data["category"] == "personal"
        assert data["status"] == "todo"

    def test_create_rejects_invalid_priority(self, client):
        token = _signup(client, "badpriority@test.com")
        r = client.post(
            "/api/v1/teacher-tasks",
            json={"title": "x", "priority": "urgent-ish"},
            headers=_auth(token),
        )
        assert r.status_code == 422

    def test_create_rejects_invalid_category(self, client):
        token = _signup(client, "badcategory@test.com")
        r = client.post(
            "/api/v1/teacher-tasks",
            json={"title": "x", "category": "hobbies"},
            headers=_auth(token),
        )
        assert r.status_code == 422

    def test_get_task_by_id(self, client):
        token = _signup(client, "get@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Prep lesson"}, headers=_auth(token)
        ).json()["id"]

        r = client.get(f"/api/v1/teacher-tasks/{task_id}", headers=_auth(token))
        assert r.status_code == 200
        assert r.json()["id"] == task_id

    def test_get_task_not_found(self, client):
        token = _signup(client, "notfound@test.com")
        r = client.get("/api/v1/teacher-tasks/does-not-exist", headers=_auth(token))
        assert r.status_code == 404

    def test_update_task(self, client):
        token = _signup(client, "update@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Prep lesson"}, headers=_auth(token)
        ).json()["id"]

        r = client.patch(
            f"/api/v1/teacher-tasks/{task_id}",
            json={"description": "bring markers", "status": "in_progress"},
            headers=_auth(token),
        )
        assert r.status_code == 200
        assert r.json()["description"] == "bring markers"
        assert r.json()["status"] == "in_progress"

    def test_update_rejects_invalid_status(self, client):
        token = _signup(client, "badstatus@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "x"}, headers=_auth(token)
        ).json()["id"]

        r = client.patch(
            f"/api/v1/teacher-tasks/{task_id}",
            json={"status": "blocked"},
            headers=_auth(token),
        )
        assert r.status_code == 422

    def test_update_not_found(self, client):
        token = _signup(client, "updatenf@test.com")
        r = client.patch(
            "/api/v1/teacher-tasks/does-not-exist",
            json={"title": "x"},
            headers=_auth(token),
        )
        assert r.status_code == 404

    def test_delete_task(self, client):
        token = _signup(client, "delete@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Admin task"}, headers=_auth(token)
        ).json()["id"]

        r = client.delete(f"/api/v1/teacher-tasks/{task_id}", headers=_auth(token))
        assert r.status_code == 200
        assert client.get("/api/v1/teacher-tasks", headers=_auth(token)).json() == []

    def test_delete_not_found(self, client):
        token = _signup(client, "deletenf@test.com")
        r = client.delete("/api/v1/teacher-tasks/does-not-exist", headers=_auth(token))
        assert r.status_code == 404


class TestOwnership:
    def test_cannot_view_other_teachers_task(self, client):
        token_a = _signup(client, "owna@test.com")
        token_b = _signup(client, "ownb@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Private task"}, headers=_auth(token_a)
        ).json()["id"]

        r = client.get(f"/api/v1/teacher-tasks/{task_id}", headers=_auth(token_b))
        assert r.status_code == 403

    def test_cannot_edit_other_teachers_task(self, client):
        token_a = _signup(client, "owna2@test.com")
        token_b = _signup(client, "ownb2@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Private task"}, headers=_auth(token_a)
        ).json()["id"]

        r = client.patch(
            f"/api/v1/teacher-tasks/{task_id}",
            json={"title": "hijacked"},
            headers=_auth(token_b),
        )
        assert r.status_code == 403

    def test_cannot_delete_other_teachers_task(self, client):
        token_a = _signup(client, "owna3@test.com")
        token_b = _signup(client, "ownb3@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Private task"}, headers=_auth(token_a)
        ).json()["id"]

        r = client.delete(f"/api/v1/teacher-tasks/{task_id}", headers=_auth(token_b))
        assert r.status_code == 403

    def test_list_only_shows_own_tasks(self, client):
        token_a = _signup(client, "lista@test.com")
        token_b = _signup(client, "listb@test.com")
        client.post("/api/v1/teacher-tasks", json={"title": "A's task"}, headers=_auth(token_a))
        client.post("/api/v1/teacher-tasks", json={"title": "B's task"}, headers=_auth(token_b))

        r = client.get("/api/v1/teacher-tasks", headers=_auth(token_a))
        assert len(r.json()) == 1
        assert r.json()[0]["title"] == "A's task"


class TestQuickComplete:
    def test_complete_and_reopen_task(self, client):
        token = _signup(client, "complete@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Parent meeting"}, headers=_auth(token)
        ).json()["id"]

        r = client.post(f"/api/v1/teacher-tasks/{task_id}/complete", headers=_auth(token))
        assert r.status_code == 200
        assert r.json()["status"] == "completed"

        r = client.post(f"/api/v1/teacher-tasks/{task_id}/reopen", headers=_auth(token))
        assert r.status_code == 200
        assert r.json()["status"] == "todo"

    def test_complete_not_found(self, client):
        token = _signup(client, "completenf@test.com")
        r = client.post(
            "/api/v1/teacher-tasks/does-not-exist/complete", headers=_auth(token)
        )
        assert r.status_code == 404

    def test_cannot_complete_other_teachers_task(self, client):
        token_a = _signup(client, "cowna@test.com")
        token_b = _signup(client, "cownb@test.com")
        task_id = client.post(
            "/api/v1/teacher-tasks", json={"title": "Private"}, headers=_auth(token_a)
        ).json()["id"]

        r = client.post(
            f"/api/v1/teacher-tasks/{task_id}/complete", headers=_auth(token_b)
        )
        assert r.status_code == 403


class TestSearchFilterSort:
    def _seed(self, client, token):
        client.post(
            "/api/v1/teacher-tasks",
            json={"title": "Grade essays", "priority": "high", "category": "assessment"},
            headers=_auth(token),
        )
        client.post(
            "/api/v1/teacher-tasks",
            json={"title": "Book field trip", "priority": "low", "category": "administration"},
            headers=_auth(token),
        )
        client.post(
            "/api/v1/teacher-tasks",
            json={"title": "Grade homework", "priority": "urgent", "category": "assessment"},
            headers=_auth(token),
        )

    def test_search_by_title(self, client):
        token = _signup(client, "search@test.com")
        self._seed(client, token)

        r = client.get("/api/v1/teacher-tasks?search=grade", headers=_auth(token))
        assert r.status_code == 200
        titles = {t["title"] for t in r.json()}
        assert titles == {"Grade essays", "Grade homework"}

    def test_filter_by_status(self, client):
        token = _signup(client, "filterstatus@test.com")
        self._seed(client, token)
        task_id = client.get("/api/v1/teacher-tasks", headers=_auth(token)).json()[0]["id"]
        client.post(f"/api/v1/teacher-tasks/{task_id}/complete", headers=_auth(token))

        r = client.get("/api/v1/teacher-tasks?status=completed", headers=_auth(token))
        assert len(r.json()) == 1
        r = client.get("/api/v1/teacher-tasks?status=todo", headers=_auth(token))
        assert len(r.json()) == 2

    def test_filter_by_priority(self, client):
        token = _signup(client, "filterpriority@test.com")
        self._seed(client, token)

        r = client.get("/api/v1/teacher-tasks?priority=urgent", headers=_auth(token))
        assert len(r.json()) == 1
        assert r.json()[0]["title"] == "Grade homework"

    def test_filter_by_category(self, client):
        token = _signup(client, "filtercategory@test.com")
        self._seed(client, token)

        r = client.get("/api/v1/teacher-tasks?category=assessment", headers=_auth(token))
        assert len(r.json()) == 2

    def test_sort_by_priority(self, client):
        token = _signup(client, "sortpriority@test.com")
        self._seed(client, token)

        r = client.get("/api/v1/teacher-tasks?sort_by=priority", headers=_auth(token))
        priorities = [t["priority"] for t in r.json()]
        assert priorities == ["urgent", "high", "low"]

    def test_sort_by_rejects_invalid_field(self, client):
        token = _signup(client, "sortinvalid@test.com")
        r = client.get("/api/v1/teacher-tasks?sort_by=title", headers=_auth(token))
        assert r.status_code == 422

import uuid
import pytest
from src.books.schemas import BookCreate
from src.books.service import BookService
from src.tags.schemas import TagCreate
from src.tags.service import TagService


class TestTagRoutes:
    @pytest.mark.asyncio
    async def test_get_all_tags(self, client, session, auth_headers):
        service = TagService()
        await service.add_tag(tag_data=TagCreate(name="fiction"), session=session)
        await service.add_tag(tag_data=TagCreate(name="non-fiction"), session=session)
        resp = await client.get("/api/v1/tags/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_create_tag(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/tags/",
            json={"name": "sci-fi"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "sci-fi"
        assert "uid" in data

    @pytest.mark.asyncio
    async def test_create_duplicate_tag(self, client, session, auth_headers):
        service = TagService()
        await service.add_tag(tag_data=TagCreate(name="fiction"), session=session)
        resp = await client.post(
            "/api/v1/tags/",
            json={"name": "fiction"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_add_tags_to_book(self, client, session, auth_headers, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Tagging Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        resp = await client.post(
            f"/api/v1/tags/book/{book.uid}/tags",
            json={"tags": [{"name": "fiction"}, {"name": "classic"}]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tags"]) == 2

    @pytest.mark.asyncio
    async def test_update_tag(self, client, session, auth_headers):
        service = TagService()
        created = await service.add_tag(tag_data=TagCreate(name="fiction"), session=session)
        resp = await client.put(
            f"/api/v1/tags/{created.uid}",
            json={"name": "sci-fi"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "sci-fi"

    @pytest.mark.asyncio
    async def test_update_tag_not_found(self, client, auth_headers):
        resp = await client.put(
            f"/api/v1/tags/{uuid.uuid4()}",
            json={"name": "sci-fi"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_tag(self, client, session, auth_headers):
        service = TagService()
        created = await service.add_tag(tag_data=TagCreate(name="fiction"), session=session)
        resp = await client.delete(
            f"/api/v1/tags/{created.uid}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_tag_not_found(self, client, auth_headers):
        resp = await client.delete(
            f"/api/v1/tags/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

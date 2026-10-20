import pytest
from app import Book, db, create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as c:
        yield c


def test_health(client):
    assert client.get("/health").json == {"status": "ok"}


def test_add_book(client):
    client.post("/books/add", data={"title": "Dune", "author": "Frank Herbert", "copies": 2})
    assert b"Dune" in client.get("/").data


def test_issue_and_return_changes_stock(client):
    client.post("/books/add", data={"title": "Dune", "author": "FH", "copies": 1})
    client.post("/members", data={"name": "Asha", "email": "a@x.com"})
    client.post("/issues", data={"book_id": 1, "member_id": 1})
    with client.application.app_context():
        assert db.session.get(Book, 1).copies == 0
    client.post("/issues/1/return")
    with client.application.app_context():
        assert db.session.get(Book, 1).copies == 1


def test_cannot_issue_when_out_of_stock(client):
    client.post("/books/add", data={"title": "Dune", "author": "FH", "copies": 1})
    client.post("/members", data={"name": "Asha", "email": "a@x.com"})
    client.post("/issues", data={"book_id": 1, "member_id": 1})
    client.post("/issues", data={"book_id": 1, "member_id": 1})
    with client.application.app_context():
        assert db.session.get(Book, 1).copies == 0

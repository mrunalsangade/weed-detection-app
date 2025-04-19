import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_login_page(client):
    res = client.get('/')
    assert res.status_code == 200

def test_protected_redirect(client):
    res = client.get('/home')
    # should redirect to login
    assert res.status_code in (301, 302)

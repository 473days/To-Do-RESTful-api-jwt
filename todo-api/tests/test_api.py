import pytest
import json
from app import app, db, User, Todo

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_page(client):
    """Test the home page returns successful response."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"To-Do API" in response.data

def test_api_docs(client):
    """Test the API documentation endpoint."""
    response = client.get('/api')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'endpoints' in data
    assert 'auth' in data['endpoints']

def test_register_user(client):
    """Test user registration."""
    data = {
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com'
    }
    
    response = client.post('/api/auth/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User created successfully'
    assert data['user']['username'] == 'testuser'

def test_register_duplicate_user(client):
    """Test registering duplicate user."""
    data = {'username': 'testuser', 'password': 'testpass123'}
    
    # First registration
    client.post('/api/auth/register',
               data=json.dumps(data),
               content_type='application/json')
    
    # Second registration (should fail)
    response = client.post('/api/auth/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'already exists' in data['error']

def test_login_success(client):
    """Test successful login."""
    # First register
    register_data = {'username': 'testuser', 'password': 'testpass123'}
    client.post('/api/auth/register',
               data=json.dumps(register_data),
               content_type='application/json')
    
    # Then login
    response = client.post('/api/auth/login',
                          data=json.dumps(register_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['message'] == 'Login successful'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    data = {'username': 'nonexistent', 'password': 'wrongpass'}
    
    response = client.post('/api/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Invalid credentials' in data['error']

def test_register_missing_fields(client):
    """Test registration with missing fields."""
    data = {'username': 'testuser'}  # Missing password
    
    response = client.post('/api/auth/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'required' in data['error']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
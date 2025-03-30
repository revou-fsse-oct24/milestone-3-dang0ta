from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from db.users import create_user
from auth_jwt.tokens import create_access_token
from models import UserCredential

class TestPostUsers:
    """Test suite for the user creation endpoint (POST /users/).
    
    This class contains tests for the user creation functionality, including:
    - Successful user creation
    - Input validation
    - Error handling
    - Integration with authentication flow
    """
    
    def test_create_new_user(self, client: Client):
        """Test successful creation of a new user.
        
        Verifies that:
        1. The endpoint returns 201 status code
        2. The response contains a valid user ID
        """
        response = client.post("/users/", json={"name": "foo", "email_address": "foo@bar.com", "password": "password"})
        assert response.status_code == 201, response.get_data()

        response_data = response.get_json()
        assert response_data["id"] is not None

    def test_create_new_user_missing_name(self, client: Client):
        """Test validation when username is missing.
        
        Verifies that:
        1. The endpoint returns 400 status code
        2. The error message indicates missing username
        """
        response = client.post("/users/", json={"email_address": "foo@bar.com", "password": "password"})
        assert response.status_code == 400, response.get_data()
        assert response.get_data() == b'{"error":"missing user name"}\n'

    def test_create_new_user_missing_email(self, client: Client):
        """Test validation when email address is missing.
        
        Verifies that:
        1. The endpoint returns 400 status code
        2. The error message indicates missing email address
        """
        response = client.post("/users/", json={"name": "foo", "password": "password"})
        assert response.status_code == 400, response.get_data()
        assert response.get_data() == b'{"error":"missing email address"}\n'

    def test_create_new_user_invalid_email(self, client: Client):
        """Test validation when email address format is invalid.
        
        Verifies that:
        1. The endpoint returns 400 status code
        2. The error message indicates invalid email format
        """
        response = client.post("/users/", json={"email_address": "foobarqux", "name": "foo", "password": "password"})
        assert response.status_code == 400, response.get_data()
        assert response.get_data() == b'{"error":"invalid email address"}\n'

    def test_create_new_user_missing_password(self, client: Client):
        """Test validation when password is missing.
        
        Verifies that:
        1. The endpoint returns 400 status code
        2. The error message indicates missing password
        """
        response = client.post("/users/", json={"name": "foo", "email_address": "foo@bar.com"})
        assert response.status_code == 400, response.get_data()
        assert response.get_data() == b'{"error":"missing password"}\n'

    def test_create_new_user_integration(self, client: Client):
        """Test the complete user creation and authentication flow.
        
        Tests the following sequence:
        1. User creation
        2. User login with created credentials
        3. Fetching user profile with authentication
        4. User logout
        5. Verifying token invalidation after logout
        
        Verifies:
        - Successful user creation (201)
        - Successful login with access and refresh tokens
        - Correct user profile data
        - Successful logout
        - Token invalidation after logout
        """
        response = client.post("/users/", json={"name": "foo", "email_address": "foo@bar.com", "password": "password"})
        assert response.status_code == 201, response.get_data()

        response_data = response.get_json()
        assert response_data["id"] is not None
        id = response_data["id"]

        response = client.post("/auth/login", json={"email": "foo@bar.com", "password": "password"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["access_token"] is not None
        assert response_data["refresh_token"] is not None

        access_token = response_data["access_token"]

        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["name"] == "foo"
        assert response_data["email_address"] == "foo@bar.com"

        response = client.get("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        assert response.get_data() == b'{"message":"Logged out successfully"}\n'

        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 401, response.get_data()

class TestGetCurrentUser:
    def test_get_authenticated_user(self, client: Client, access_token: str, test_user: UserCredential):
        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["name"] == test_user.name
        assert response_data["email_address"] == test_user.email_address

    def test_get_unauthenticated_user(self, client: Client):
        response = client.get("/users/me")
        assert response.status_code == 401, response.get_data()

    def test_get_authenticated_user_with_invalid_token(self, client: Client, access_token: str):
        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}123"})
        assert response.status_code == 401, response.get_data()

class TestUpdateCurrentUser:
    def test_update_current_user(self, client: Client, access_token: str):
        response = client.put("/users/me", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "bar", "email_address": "bar@qux.com"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["name"] == "bar"
        assert response_data["email_address"] == "bar@qux.com"
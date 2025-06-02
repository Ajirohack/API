"""
Tests for plugin system endpoints.
"""
import pytest
import os
import json
import zipfile
from fastapi import status
from io import BytesIO

@pytest.fixture
def test_plugin_zip():
    """Create a test plugin zip file"""
    manifest = {
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "Test plugin for unit tests",
        "entry_point": "main.py",
        "capabilities": ["test"],
        "settings": {}
    }
    
    # Create zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add manifest
        zip_file.writestr('manifest.json', json.dumps(manifest))
        # Add dummy main file
        zip_file.writestr('main.py', 'print("Hello from test plugin")')
    
    zip_buffer.seek(0)
    return zip_buffer

def test_list_plugins_empty(client, test_user):
    """Test listing plugins when none are installed"""
    # Login first
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/plugins", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_upload_plugin(client, test_user, test_plugin_zip):
    """Test uploading a plugin"""
    # Login first
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload plugin
    files = {
        'plugin_file': ('test-plugin.zip', test_plugin_zip, 'application/zip')
    }
    response = client.post(
        "/api/plugins/upload",
        headers=headers,
        files=files
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "test-plugin"
    assert data["version"] == "1.0.0"
    assert data["status"] == "enabled"

def test_list_plugins_after_upload(client, test_user, test_plugin_zip):
    """Test listing plugins after uploading one"""
    # Login and upload plugin first
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    files = {
        'plugin_file': ('test-plugin.zip', test_plugin_zip, 'application/zip')
    }
    client.post("/api/plugins/upload", headers=headers, files=files)
    
    # List plugins
    response = client.get("/api/plugins", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    plugin = data[0]
    assert plugin["name"] == "test-plugin"
    assert plugin["version"] == "1.0.0"

def test_disable_enable_plugin(client, test_user, test_plugin_zip):
    """Test disabling and enabling a plugin"""
    # Login and upload plugin first
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    files = {
        'plugin_file': ('test-plugin.zip', test_plugin_zip, 'application/zip')
    }
    client.post("/api/plugins/upload", headers=headers, files=files)
    
    # Disable plugin
    response = client.post(
        "/api/plugins/test-plugin/disable",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "disabled"
    
    # Enable plugin
    response = client.post(
        "/api/plugins/test-plugin/enable",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "enabled"

def test_uninstall_plugin(client, test_user, test_plugin_zip):
    """Test uninstalling a plugin"""
    # Login and upload plugin first
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    files = {
        'plugin_file': ('test-plugin.zip', test_plugin_zip, 'application/zip')
    }
    client.post("/api/plugins/upload", headers=headers, files=files)
    
    # Uninstall plugin
    response = client.delete(
        "/api/plugins/test-plugin",
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["plugin_id"] == "test-plugin"
    
    # Verify plugin is gone
    response = client.get("/api/plugins", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0

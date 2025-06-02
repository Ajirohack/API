"""
Tests for health check endpoints.
"""
import pytest
from fastapi import status

def test_basic_health_check(client):
    """Test basic health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Service is healthy"

def test_detailed_health_check(client):
    """Test detailed health check endpoint"""
    response = client.get("/api/health/details")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Check required sections
    assert "system" in data
    assert "resources" in data
    assert "database" in data
    
    # Check system info
    system = data["system"]
    assert "platform" in system
    assert "version" in system
    assert "python_version" in system
    
    # Check resource metrics
    resources = data["resources"]
    assert "cpu_percent" in resources
    assert "memory_used_percent" in resources
    assert "disk_used_percent" in resources
    
    # Check database status
    assert "status" in data["database"]

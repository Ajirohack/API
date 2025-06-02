"""
Tests for metrics endpoints.
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_usage_metrics(client, test_user):
    """Test getting usage metrics"""
    # Login first
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with default timeframe
    response = client.get("/api/metrics/usage", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    metrics = data["data"]
    assert "total_requests" in metrics
    assert "average_response_time" in metrics
    assert "error_rate" in metrics
    assert "endpoints" in metrics

def test_usage_metrics_with_timeframe(client, test_user):
    """Test getting usage metrics with custom timeframe"""
    # Login first
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with custom timeframe
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    response = client.get("/api/metrics/usage", headers=headers, params=params)
    assert response.status_code == status.HTTP_200_OK

def test_performance_metrics(client, test_user):
    """Test getting performance metrics"""
    # Login first
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/metrics/performance", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    metrics = data["data"]
    
    # Check CPU metrics
    assert "cpu" in metrics
    assert "overall" in metrics["cpu"]
    assert "per_cpu" in metrics["cpu"]
    
    # Check memory metrics
    assert "memory" in metrics
    assert "total" in metrics["memory"]
    assert "available" in metrics["memory"]
    assert "percent" in metrics["memory"]
    
    # Check disk metrics
    assert "disk" in metrics
    assert "total" in metrics["disk"]
    assert "used" in metrics["disk"]
    assert "free" in metrics["disk"]
    assert "percent" in metrics["disk"]

def test_error_metrics(client, test_user):
    """Test getting error metrics"""
    # Login first
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different timeframes
    timeframes = ["1h", "24h", "7d", "30d"]
    for timeframe in timeframes:
        response = client.get(
            "/api/metrics/errors",
            headers=headers,
            params={"timeframe": timeframe}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        metrics = data["data"]
        
        # Check error metrics structure
        assert "total_errors" in metrics
        assert "error_types" in metrics
        assert "most_common" in metrics
        
        # Check error types
        error_types = metrics["error_types"]
        assert "4xx" in error_types
        assert "5xx" in error_types
        
        # Check most common errors
        assert isinstance(metrics["most_common"], list)
        if metrics["most_common"]:
            error = metrics["most_common"][0]
            assert "status" in error
            assert "count" in error
            assert "endpoint" in error

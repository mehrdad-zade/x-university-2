"""
Test monitoring endpoints.

This module tests the monitoring system including system metrics,
Docker container information, health status, and logging functionality.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import json


@pytest.mark.asyncio
async def test_monitor_endpoint_basic(client: AsyncClient) -> None:
    """Test that the monitor endpoint returns expected structure."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required top-level keys
    required_keys = ["timestamp", "system", "docker", "services", "logs"]
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
    
    # Check system structure
    system = data["system"]
    assert "os" in system
    assert "python_version" in system
    assert "metrics" in system
    
    # Check metrics structure
    metrics = system["metrics"]
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "network" in metrics
    
    # Check services structure
    services = data["services"]
    assert "backend" in services
    
    # Check logs structure
    logs = data["logs"]
    assert "backend" in logs
    assert "frontend" in logs
    assert isinstance(logs["backend"], list)
    assert isinstance(logs["frontend"], list)


@pytest.mark.asyncio
async def test_monitor_health_endpoint(client: AsyncClient) -> None:
    """Test the monitor health endpoint."""
    response = await client.get("/api/v1/monitor/health")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required keys
    required_keys = ["timestamp", "backend", "containers", "system"]
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
    
    # Check backend health structure
    backend = data["backend"]
    assert "service" in backend
    assert "database" in backend
    assert "timestamp" in backend
    assert "uptime" in backend
    
    # Check system metrics
    system = data["system"]
    assert "cpu_percent" in system
    assert "memory_percent" in system
    assert "disk_percent" in system
    assert isinstance(system["cpu_percent"], (int, float))
    assert isinstance(system["memory_percent"], (int, float))
    assert isinstance(system["disk_percent"], (int, float))


@pytest.mark.asyncio
async def test_monitor_system_metrics_structure(client: AsyncClient) -> None:
    """Test system metrics have correct structure and types."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    metrics = data["system"]["metrics"]
    
    # Test CPU metrics
    cpu = metrics["cpu"]
    assert isinstance(cpu["usage_percent"], (int, float))
    assert isinstance(cpu["count"], int)
    assert cpu["count"] > 0
    assert "load_average" in cpu
    assert "1min" in cpu["load_average"]
    assert "5min" in cpu["load_average"]
    assert "15min" in cpu["load_average"]
    
    # Test memory metrics
    memory = metrics["memory"]
    assert isinstance(memory["total"], int)
    assert isinstance(memory["used"], int)
    assert isinstance(memory["available"], int)
    assert isinstance(memory["usage_percent"], (int, float))
    assert memory["total"] > 0
    assert 0 <= memory["usage_percent"] <= 100
    
    # Test disk metrics
    disk = metrics["disk"]
    assert isinstance(disk["total"], int)
    assert isinstance(disk["used"], int)
    assert isinstance(disk["free"], int)
    assert isinstance(disk["usage_percent"], (int, float))
    assert disk["total"] > 0
    assert 0 <= disk["usage_percent"] <= 100
    
    # Test network metrics
    network = metrics["network"]
    assert isinstance(network["bytes_sent"], int)
    assert isinstance(network["bytes_recv"], int)
    assert isinstance(network["packets_sent"], int)
    assert isinstance(network["packets_recv"], int)
    assert network["bytes_sent"] >= 0
    assert network["bytes_recv"] >= 0


@pytest.mark.asyncio
async def test_monitor_docker_structure(client: AsyncClient) -> None:
    """Test Docker information structure."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    docker = data["docker"]
    
    # Check required Docker keys
    required_keys = ["containers", "images", "system_info"]
    for key in required_keys:
        assert key in docker, f"Missing Docker key: {key}"
    
    # Check containers structure
    containers = docker["containers"]
    assert isinstance(containers, list)
    
    # If containers exist, check their structure
    if containers:
        container = containers[0]
        expected_keys = ["id", "name", "image", "status", "created", "stats"]
        for key in expected_keys:
            assert key in container, f"Missing container key: {key}"
        
        # Check stats structure
        stats = container["stats"]
        stats_keys = ["cpu_percent", "memory_usage", "memory_limit", "network_rx", "network_tx"]
        for key in stats_keys:
            assert key in stats, f"Missing stats key: {key}"
    
    # Check images structure
    images = docker["images"]
    assert isinstance(images, list)
    
    # Check system_info structure
    system_info = docker["system_info"]
    assert isinstance(system_info, dict)


@pytest.mark.asyncio
async def test_monitor_logs_structure(client: AsyncClient) -> None:
    """Test logs structure and content."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    logs = data["logs"]
    
    # Check backend logs
    backend_logs = logs["backend"]
    assert isinstance(backend_logs, list)
    
    if backend_logs:
        log_entry = backend_logs[0]
        required_keys = ["timestamp", "level", "message", "service"]
        for key in required_keys:
            assert key in log_entry, f"Missing log entry key: {key}"
        
        # Check log levels are valid
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert log_entry["level"] in valid_levels, f"Invalid log level: {log_entry['level']}"
        
        # Check timestamp format (should be ISO format)
        assert "T" in log_entry["timestamp"], "Timestamp should be in ISO format"
    
    # Check frontend logs
    frontend_logs = logs["frontend"]
    assert isinstance(frontend_logs, list)
    
    if frontend_logs:
        log_entry = frontend_logs[0]
        required_keys = ["timestamp", "level", "message", "service"]
        for key in required_keys:
            assert key in log_entry, f"Missing frontend log entry key: {key}"


@pytest.mark.asyncio
async def test_monitor_backend_service_health(client: AsyncClient) -> None:
    """Test backend service health reporting."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    backend_health = data["services"]["backend"]
    
    # Check backend health structure
    assert "service" in backend_health
    assert "database" in backend_health
    assert "timestamp" in backend_health
    assert "uptime" in backend_health
    
    # Check service status is valid
    valid_statuses = ["healthy", "unhealthy"]
    assert backend_health["service"] in valid_statuses
    
    # Check database health
    database = backend_health["database"]
    assert "status" in database
    assert database["status"] in ["healthy", "unhealthy", "unknown"]
    
    # Check uptime is a number
    assert isinstance(backend_health["uptime"], (int, float))
    assert backend_health["uptime"] >= 0


@pytest.mark.asyncio
async def test_monitor_caching(client: AsyncClient) -> None:
    """Test that monitor endpoint uses caching appropriately."""
    # Make two requests quickly
    response1 = await client.get("/api/v1/monitor")
    response2 = await client.get("/api/v1/monitor")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Timestamps should be the same or very close due to caching
    timestamp1 = data1["timestamp"]
    timestamp2 = data2["timestamp"]
    
    # Parse timestamps to compare (should be identical due to 5-second cache)
    assert timestamp1 == timestamp2, "Cache should provide identical responses within cache window"


@pytest.mark.asyncio
async def test_monitor_error_handling(client: AsyncClient) -> None:
    """Test monitor endpoint handles errors gracefully."""
    # The monitor endpoint should always return 200 even if some subsystems fail
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    
    # Even if Docker fails, we should get error information
    docker = data["docker"]
    if "error" in docker:
        # If there's a Docker error, it should be a string
        assert isinstance(docker["error"], str)
        assert len(docker["error"]) > 0
    
    # System metrics should always be available
    assert "metrics" in data["system"]
    assert data["system"]["metrics"]["cpu"]["usage_percent"] >= 0


@pytest.mark.asyncio
async def test_monitor_performance(client: AsyncClient) -> None:
    """Test that monitor endpoint responds within reasonable time."""
    import time
    
    start_time = time.time()
    response = await client.get("/api/v1/monitor")
    end_time = time.time()
    
    assert response.status_code == 200
    
    # Should respond within 5 seconds (generous for system metrics collection)
    response_time = end_time - start_time
    assert response_time < 5.0, f"Monitor endpoint too slow: {response_time}s"


@pytest.mark.asyncio
async def test_monitor_public_access(client: AsyncClient) -> None:
    """Test that monitor endpoints don't require authentication."""
    # Test without any authentication headers
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    response_health = await client.get("/api/v1/monitor/health")
    assert response_health.status_code == 200
    
    # Should not return 401 Unauthorized
    assert response.status_code != 401
    assert response_health.status_code != 401


@pytest.mark.asyncio
async def test_monitor_log_levels(client: AsyncClient) -> None:
    """Test that logs contain appropriate log levels for monitoring."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    all_logs = data["logs"]["backend"] + data["logs"]["frontend"]
    
    # Should have logs
    assert len(all_logs) > 0
    
    # Check for variety of log levels
    log_levels = {log["level"] for log in all_logs}
    
    # Should have at least INFO logs
    assert "INFO" in log_levels
    
    # Check that WARNING and ERROR logs are properly formatted for highlighting
    warning_logs = [log for log in all_logs if log["level"] == "WARNING"]
    error_logs = [log for log in all_logs if log["level"] == "ERROR"]
    
    # If there are warning/error logs, they should have proper structure
    for log in warning_logs + error_logs:
        assert isinstance(log["message"], str)
        assert len(log["message"]) > 0
        assert isinstance(log["service"], str)
        assert len(log["service"]) > 0


@pytest.mark.asyncio 
async def test_monitor_os_information(client: AsyncClient) -> None:
    """Test that OS information is properly collected."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    os_info = data["system"]["os"]
    
    # Should have OS information
    assert isinstance(os_info, dict)
    
    # Should have system name (at minimum)
    if "sysname" in os_info:
        assert isinstance(os_info["sysname"], str)
        assert len(os_info["sysname"]) > 0
    elif "system" in os_info:
        assert isinstance(os_info["system"], str)
        assert len(os_info["system"]) > 0
    else:
        # Should have at least one OS identifier
        assert len(os_info) > 0


@pytest.mark.asyncio
async def test_monitor_network_metrics(client: AsyncClient) -> None:
    """Test network metrics are properly collected and formatted."""
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    network = data["system"]["metrics"]["network"]
    
    # Check all network counters are non-negative integers
    network_fields = [
        "bytes_sent", "bytes_recv", "packets_sent", "packets_recv",
        "errin", "errout", "dropin", "dropout"
    ]
    
    for field in network_fields:
        assert field in network, f"Missing network field: {field}"
        assert isinstance(network[field], int), f"Network field {field} should be integer"
        assert network[field] >= 0, f"Network field {field} should be non-negative"


# Mock tests for Docker unavailable scenarios
@pytest.mark.asyncio
async def test_monitor_without_docker(client: AsyncClient) -> None:
    """Test monitor behavior when Docker is not available."""
    # This test verifies graceful degradation when Docker is unavailable
    # In the actual implementation, this would be mocked, but for integration
    # testing, we just verify the endpoint handles missing Docker gracefully
    
    response = await client.get("/api/v1/monitor")
    assert response.status_code == 200
    
    data = response.json()
    docker = data["docker"]
    
    # Should have Docker section even if unavailable
    assert "containers" in docker
    assert "images" in docker
    assert "system_info" in docker
    
    # If Docker is unavailable, should have appropriate error message
    if not docker["containers"] and not docker["images"]:
        assert "error" in docker
        assert isinstance(docker["error"], str)
        assert "not available" in docker["error"].lower() or "client" in docker["error"].lower()

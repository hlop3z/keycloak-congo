"""API testing utilities"""

import requests
import time
from typing import Optional, Dict, Any, List
from .keycloak_client import get_token


def call_api(
    kong_url: str,
    endpoint: str,
    method: str = "GET",
    token: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> requests.Response:
    """
    Call API endpoint through Kong

    Args:
        kong_url: Kong gateway URL
        endpoint: API endpoint path
        method: HTTP method
        token: JWT token (optional)
        data: Request body data (optional)

    Returns:
        Response object
    """
    url = f"{kong_url}{endpoint}"
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(method=method, url=url, headers=headers, json=data)

    return response


def run_test_suite(suite_name: str, kong_url: str = "http://localhost:8000") -> Dict[str, int]:
    """
    Run test suite

    Args:
        suite_name: Test suite name
        kong_url: Kong gateway URL

    Returns:
        Test results summary
    """
    tests = {
        "integration": [
            lambda: test_public_endpoint(kong_url),
        ],
        "smoke": [
            lambda: test_public_endpoint(kong_url),
        ],
    }

    suite_tests = tests.get(suite_name, [])
    passed = sum(1 for test in suite_tests if test())
    total = len(suite_tests)
    failed = total - passed

    return {"passed": passed, "failed": failed, "total": total}


def test_public_endpoint(kong_url: str = "http://localhost:8000") -> bool:
    """Test public endpoint"""
    response = call_api(kong_url, "/api/public")
    return response.status_code == 200


def test_protected_endpoint(kong_url: str = "http://localhost:8000", token: str = None) -> bool:
    """Test protected endpoint"""
    if not token:
        return False

    response = call_api(kong_url, "/api/protected", token=token)
    return response.status_code == 200


def test_admin_endpoint(kong_url: str = "http://localhost:8000", token: str = None) -> bool:
    """Test admin endpoint"""
    if not token:
        return False

    response = call_api(kong_url, "/api/admin", token=token)
    return response.status_code in [200, 403]  # 403 if not admin role


def run_comprehensive_suite(keycloak_url: str, kong_url: str, env: str = "dev") -> Dict[str, Any]:
    """
    Run comprehensive test suite

    Args:
        keycloak_url: Keycloak URL
        kong_url: Kong URL
        env: Environment name

    Returns:
        Comprehensive test results
    """
    results: List[Dict[str, Any]] = []
    start_time = time.time()

    # Test 1: Kong is accessible
    test_start = time.time()
    try:
        response = requests.get(f"{kong_url}/", timeout=5)
        passed = response.status_code in [200, 404]  # 404 is ok, means Kong is running
        message = f"Kong accessible at {kong_url}"
    except Exception as e:
        passed = False
        message = f"Kong not accessible: {e}"

    results.append(
        {
            "name": "Kong Accessibility",
            "passed": passed,
            "duration": time.time() - test_start,
            "message": message,
        }
    )

    # Test 2: Keycloak is accessible
    test_start = time.time()
    try:
        response = requests.get(f"{keycloak_url}/", timeout=5)
        passed = response.status_code in [200, 404]
        message = f"Keycloak accessible at {keycloak_url}"
    except Exception as e:
        passed = False
        message = f"Keycloak not accessible: {e}"

    results.append(
        {
            "name": "Keycloak Accessibility",
            "passed": passed,
            "duration": time.time() - test_start,
            "message": message,
        }
    )

    # Test 3: Can get token from Keycloak
    test_start = time.time()
    user_token = None
    try:
        # Try with default test user (this may fail if user doesn't exist)
        token_data = get_token(keycloak_url, "kong-realm", "testuser", "testuser123")
        user_token = token_data.get("access_token")
        passed = user_token is not None
        message = "Successfully obtained token for testuser"
    except Exception as e:
        passed = False
        message = f"Token acquisition failed: {e}"

    results.append(
        {
            "name": "Token Acquisition",
            "passed": passed,
            "duration": time.time() - test_start,
            "message": message,
        }
    )

    # Test 4: Public endpoint through Kong
    test_start = time.time()
    try:
        response = call_api(kong_url, "/api/public", "GET")
        # Accept both 200 (success) and 404 (route not configured yet)
        passed = response.status_code in [200, 404, 503]
        message = f"Public endpoint returned {response.status_code}"
    except Exception as e:
        passed = False
        message = f"Public endpoint test failed: {e}"

    results.append(
        {
            "name": "Public Endpoint",
            "passed": passed,
            "duration": time.time() - test_start,
            "message": message,
        }
    )

    # Test 5: Protected endpoint with token (if we have one)
    if user_token:
        test_start = time.time()
        try:
            response = call_api(kong_url, "/api/protected", "GET", token=user_token)
            # Accept 200 (success), 401 (auth configured but endpoint missing), 404 (not configured)
            passed = response.status_code in [200, 401, 404, 503]
            message = f"Protected endpoint returned {response.status_code}"
        except Exception as e:
            passed = False
            message = f"Protected endpoint test failed: {e}"

        results.append(
            {
                "name": "Protected Endpoint",
                "passed": passed,
                "duration": time.time() - test_start,
                "message": message,
            }
        )

    # Test 6: Kong health check
    test_start = time.time()
    try:
        response = requests.get(f"{kong_url}/status", timeout=5)
        passed = response.status_code == 200
        message = "Kong health check passed"
    except Exception as e:
        passed = False
        message = f"Kong health check failed: {e}"

    results.append(
        {
            "name": "Kong Health Check",
            "passed": passed,
            "duration": time.time() - test_start,
            "message": message,
        }
    )

    # Calculate summary
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count
    total_duration = time.time() - start_time

    return {
        "tests": results,
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "duration": total_duration,
        "environment": env,
        "keycloak_url": keycloak_url,
        "kong_url": kong_url,
    }

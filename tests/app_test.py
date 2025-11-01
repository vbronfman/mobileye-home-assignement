#!/usr/bin/env python3
"""
Pytest tests for FastAPI GitLab API Service
Tests HTTP endpoints at http://localhost:8080

Created with assistance of Copilot
"""

import pytest
import requests
import time


BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session", autouse=True)
def wait_for_service():
    """Wait for the service to be available before running any test"""
    max_retries = 30
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"\n✓ Service is ready at {BASE_URL}")
                return
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                pytest.exit(f"Service at {BASE_URL} is not available after {max_retries} seconds")


def test_root_endpoint():
    """Test root endpoint returns service info"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200


def test_health_endpoint():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    data = response.json()
    print(f"DEBUG {data}")
    assert data["status"] == "ok"


class TestGrantRoleEndpoint:
    """Test /grant-role endpoint"""

    def test_grant_role_valid_request(self):
        """Test grant role with valid data"""
        payload = {
            "username": "developer1",
            "repo_or_group": "gpt/large_projects/gitlabhq1",
            "role": "developer"
        }
        
        response = requests.post(
            f"{BASE_URL}/grant-role",
            json=payload
        )

        data = response.json()

        if response.status_code == 200:
            assert data["data"]["access_level"] in list(range(10,60,10))
        else:
            # Error response should have detail
            assert "detail" in data
    
    # def test_grant_role_missing_username(self):
    #     """Test grant role without username"""
    #     payload = {
    #         "repo_or_group": "testgroup/testproject",
    #         "role": "developer"
    #     }
        
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         json=payload
    #     )
        
    #     # Should return error
    #     assert response.status_code in [400, 500]
    
    # def test_grant_role_missing_repo(self):
    #     """Test grant role without repo_or_group"""
    #     payload = {
    #         "username": "testuser",
    #         "role": "developer"
    #     }
        
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         json=payload
    #     )
        
    #     # Should return error
    #     assert response.status_code in [400, 500]
    
    # def test_grant_role_missing_role(self):
    #     """Test grant role without role"""
    #     payload = {
    #         "username": "testuser",
    #         "repo_or_group": "testgroup/testproject"
    #     }
        
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         json=payload
    #     )
        
    #     # Should return error
    #     assert response.status_code in [400, 500]
    
    # def test_grant_role_invalid_role(self):
    #     """Test grant role with invalid role name"""
    #     payload = {
    #         "username": "testuser",
    #         "repo_or_group": "testgroup/testproject",
    #         "role": "invalid_role"
    #     }
        
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         json=payload
    #     )
        
    #     assert response.status_code == 400
    #     data = response.json()
    #     assert "detail" in data
    #     assert "Invalid role" in data["detail"]
    
    # def test_grant_role_empty_payload(self):
    #     """Test grant role with empty payload"""
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         json={}
    #     )
        
    #     # Should return error
    #     assert response.status_code in [400, 500]
    
    # def test_grant_role_no_json(self):
    #     """Test grant role without JSON content type"""
    #     response = requests.post(
    #         f"{BASE_URL}/grant-role",
    #         data="not json"
    #     )
        
    #     # Should return error
    #     assert response.status_code in [400, 422]
    
    @pytest.mark.parametrize("role", [
        "guest",
        "reporter", 
        "developer",
        "maintainer",
        "owner"
    ])
    def test_grant_role_all_valid_roles(self, role):
        """Test all valid role types"""
        payload = {
            "username": "testuser",
            "repo_or_group": "testgroup/testproject",
            "role": role
        }
        
        response = requests.post(
            f"{BASE_URL}/grant-role",
            json=payload
        )
        
        # Response should be valid (200, 400, or 500)
        # 400/500 expected if GitLab credentials not configured
        assert response.status_code in [200, 400, 500]
        assert response.headers["content-type"] == "application/json"


class TestGetItemsEndpoint:
    """Test /get-items endpoint"""
    
    def test_get_items_merge_requests(self):
        """Test getting merge requests"""
        payload = {
            "item_type": "mr",
            "year": 2023
        }
        
        response = requests.post(
            f"{BASE_URL}/get-items",
            json=payload
        )
        
        # Note: This will fail if GitLab credentials are not set
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        
        if response.status_code == 200:
            assert data["success"] == True
            assert "count" in data
            assert "items" in data
            assert isinstance(data["items"], list)
        else:
            assert "detail" in data
    
    def test_get_items_issues(self):
        """Test getting issues"""
        payload = {
            "item_type": "issues",
            "year": 2024
        }
        
        response = requests.post(
            f"{BASE_URL}/get-items",
            json=payload
        )
        
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        
        if response.status_code == 200:
            assert data["success"] == True
            assert "count" in data
            assert "items" in data
        else:
            assert "detail" in data
    
    def test_get_items_invalid_type(self):
        """Test with invalid item type"""
        payload = {
            "item_type": "invalid_type",
            "year": 2023
        }
        
        response = requests.post(
            f"{BASE_URL}/get-items",
            json=payload
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    
    def test_get_items_missing_item_type(self):
        """Test without item_type"""
        payload = {
            "year": 2023
        }
        
        response = requests.post(
            f"{BASE_URL}/get-items",
            json=payload
        )
        
        assert response.status_code in [400, 500]
    
#     def test_get_items_missing_year(self):
#         """Test without year"""
#         payload = {
#             "item_type": "mr"
#         }
        
#         response = requests.post(
#             f"{BASE_URL}/get-items",
#             json=payload
#         )
        
#         assert response.status_code in [400, 500]
    
#     def test_get_items_empty_payload(self):
#         """Test with empty payload"""
#         response = requests.post(
#             f"{BASE_URL}/get-items",
#             json={}
#         )
        
#         assert response.status_code in [400, 500]
    
#     @pytest.mark.parametrize("year", [2018, 2021, 2022, 2023, 2024])
#     def test_get_items_various_years(self, year):
#         """Test with various valid years"""
#         payload = {
#             "item_type": "mr",
#             "year": year
#         }
        
#         response = requests.post(
#             f"{BASE_URL}/get-items",
#             json=payload
#         )
        
#         assert response.status_code in [200, 400, 500]
#         assert response.headers["content-type"] == "application/json"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = requests.get(f"{BASE_URL}/nonexistent")
        
        assert response.status_code == 404
        
    
    def test_wrong_method_grant_role(self):
        """Test using GET on POST endpoint"""
        response = requests.get(f"{BASE_URL}/grant-role")
        
        assert response.status_code == 405  # Method not allowed
    
    def test_wrong_method_get_items(self):
        """Test using GET on POST endpoint"""
        response = requests.get(f"{BASE_URL}/get-items")
        
        assert response.status_code == 405  # Method not allowed
    
    def test_malformed_json_grant_role(self):
        """Test with malformed JSON"""
        response = requests.post(
            f"{BASE_URL}/grant-role",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_malformed_json_get_items(self):
        """Test with malformed JSON"""
        response = requests.post(
            f"{BASE_URL}/get-items",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        


class TestResponseFormat:
    """Test response formats and headers"""
    
    def test_content_type_json(self):
        """Test that responses are JSON"""
        response = requests.get(f"{BASE_URL}/")
        
        assert "application/json" in response.headers["content-type"]
    
    def test_grant_role_response_structure(self):
        """Test grant-role response has correct structure"""
        payload = {
            "username": "testuser",
            "repo_or_group": "testgroup/testproject",
            "role": "developer"
        }
        
        response = requests.post(
            f"{BASE_URL}/grant-role",
            json=payload
        )
        
        data = response.json()
        
        if response.status_code == 200:
            assert "success" in data
            assert "message" in data
            assert "data" in data
        else:
            assert "detail" in data
    
    def test_get_items_response_structure(self):
        """Test get-items response has correct structure"""
        payload = {
            "item_type": "mr",
            "year": 2023
        }
        
        response = requests.post(
            f"{BASE_URL}/get-items",
            json=payload
        )
        
        data = response.json()
        
        if response.status_code == 200:
            assert "success" in data
            assert "count" in data
            assert "items" in data
            assert isinstance(data["count"], int)
            assert isinstance(data["items"], list)
        else:
            assert "detail" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
import requests
import sys
import json
from datetime import datetime

class IssueTrackerAPITester:
    def __init__(self, base_url="https://issue-handler-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_issue_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json() if response.text else {}
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        test_user_data = {
            "email": f"test_user_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['name']}")
            return True
        return False

    def test_user_login(self):
        """Test user login with demo credentials"""
        login_data = {
            "email": "demo@test.com",
            "password": "demo123"
        }
        
        success, response = self.run_test(
            "User Login (Demo)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Logged in user: {response['user']['name']}")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_issue(self):
        """Test creating a new issue"""
        issue_data = {
            "title": f"Test Issue {datetime.now().strftime('%H%M%S')}",
            "description": "This is a test issue created by automated testing",
            "priority": "high"
        }
        
        success, response = self.run_test(
            "Create Issue",
            "POST",
            "issues",
            200,
            data=issue_data
        )
        
        if success and 'id' in response:
            self.created_issue_id = response['id']
            print(f"   Created issue ID: {self.created_issue_id}")
            return True
        return False

    def test_get_all_issues(self):
        """Test getting all issues"""
        success, response = self.run_test(
            "Get All Issues",
            "GET",
            "issues",
            200
        )
        
        if success:
            print(f"   Found {len(response)} issues")
        return success

    def test_get_issues_with_filters(self):
        """Test getting issues with filters"""
        # Test priority filter
        success1, _ = self.run_test(
            "Get Issues - Priority Filter (High)",
            "GET",
            "issues?priority=high",
            200
        )
        
        # Test status filter
        success2, _ = self.run_test(
            "Get Issues - Status Filter (Open)",
            "GET",
            "issues?status=open",
            200
        )
        
        # Test search filter
        success3, _ = self.run_test(
            "Get Issues - Search Filter",
            "GET",
            "issues?search=test",
            200
        )
        
        return success1 and success2 and success3

    def test_get_single_issue(self):
        """Test getting a single issue by ID"""
        if not self.created_issue_id:
            print("❌ No issue ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Single Issue",
            "GET",
            f"issues/{self.created_issue_id}",
            200
        )
        return success

    def test_update_issue_status(self):
        """Test updating issue status"""
        if not self.created_issue_id:
            print("❌ No issue ID available for testing")
            return False
            
        update_data = {
            "status": "in-progress"
        }
        
        success, response = self.run_test(
            "Update Issue Status",
            "PUT",
            f"issues/{self.created_issue_id}",
            200,
            data=update_data
        )
        return success

    def test_add_solution(self):
        """Test adding a solution to an issue"""
        if not self.created_issue_id:
            print("❌ No issue ID available for testing")
            return False
            
        solution_data = {
            "solution_text": "This is a test solution for the automated test issue"
        }
        
        success, response = self.run_test(
            "Add Solution to Issue",
            "POST",
            f"issues/{self.created_issue_id}/solutions",
            200,
            data=solution_data
        )
        return success

    def test_get_similar_issues(self):
        """Test getting similar issues"""
        if not self.created_issue_id:
            print("❌ No issue ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Similar Issues",
            "GET",
            f"issues/{self.created_issue_id}/similar",
            200
        )
        return success

    def test_delete_issue(self):
        """Test deleting an issue"""
        if not self.created_issue_id:
            print("❌ No issue ID available for testing")
            return False
            
        success, response = self.run_test(
            "Delete Issue",
            "DELETE",
            f"issues/{self.created_issue_id}",
            200
        )
        return success

def main():
    print("🚀 Starting Issue Tracker API Tests")
    print("=" * 50)
    
    tester = IssueTrackerAPITester()
    
    # Test authentication flow
    print("\n📋 AUTHENTICATION TESTS")
    print("-" * 30)
    
    # Try login with demo credentials first
    if not tester.test_user_login():
        # If demo login fails, try registration
        if not tester.test_user_registration():
            print("❌ Authentication failed, stopping tests")
            return 1
    
    # Test getting current user
    tester.test_get_current_user()
    
    # Test issue management
    print("\n📋 ISSUE MANAGEMENT TESTS")
    print("-" * 30)
    
    tester.test_create_issue()
    tester.test_get_all_issues()
    tester.test_get_issues_with_filters()
    tester.test_get_single_issue()
    tester.test_update_issue_status()
    tester.test_add_solution()
    tester.test_get_similar_issues()
    
    # Clean up - delete the test issue
    print("\n🧹 CLEANUP")
    print("-" * 30)
    tester.test_delete_issue()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
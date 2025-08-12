#!/usr/bin/env python3
"""
Simple test script for X University authentication API.
Run this to test the authentication endpoints manually.
"""
import asyncio
import json
import httpx
from typing import Optional

BASE_URL = "http://localhost:8000"


class AuthTester:
    """Simple authentication API tester."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def _get_auth_headers(self) -> dict[str, str]:
        """Get authorization headers."""
        if not self.access_token:
            raise ValueError("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def health_check(self) -> bool:
        """Check if the API is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    async def register(self, email: str, password: str, full_name: str, role: str = "student") -> bool:
        """Register a new user."""
        data = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/v1/auth/register", json=data)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Registration successful: {result['user']['email']}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
    
    async def login(self, email: str, password: str) -> bool:
        """Login and store tokens."""
        data = {
            "email": email,
            "password": password
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/v1/auth/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                self.refresh_token = result["refresh_token"]
                print(f"✅ Login successful")
                print(f"   Access token: {self.access_token[:50]}...")
                print(f"   Refresh token: {self.refresh_token[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
    
    async def get_profile(self) -> bool:
        """Get user profile."""
        try:
            headers = self._get_auth_headers()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Profile retrieved:")
                    print(f"   ID: {result['id']}")
                    print(f"   Email: {result['email']}")
                    print(f"   Name: {result['full_name']}")
                    print(f"   Role: {result['role']}")
                    print(f"   Active: {result['is_active']}")
                    print(f"   Sessions: {result.get('total_sessions', 'N/A')}")
                    return True
                else:
                    print(f"❌ Profile request failed: {response.status_code} - {response.text}")
                    return False
        except ValueError as e:
            print(f"❌ {e}")
            return False
    
    async def refresh_access_token(self) -> bool:
        """Refresh the access token."""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        data = {"refresh_token": self.refresh_token}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/v1/auth/refresh", json=data)
            
            if response.status_code == 200:
                result = response.json()
                old_token = self.access_token[:20] if self.access_token else "None"
                self.access_token = result["access_token"]
                print(f"✅ Token refreshed")
                print(f"   Old token: {old_token}...")
                print(f"   New token: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                return False
    
    async def logout(self, revoke_all: bool = False) -> bool:
        """Logout user."""
        try:
            headers = self._get_auth_headers()
            data = {"revoke_all_sessions": revoke_all}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/v1/auth/logout", headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Logout successful: {result['message']}")
                    self.access_token = None
                    self.refresh_token = None
                    return True
                else:
                    print(f"❌ Logout failed: {response.status_code} - {response.text}")
                    return False
        except ValueError as e:
            print(f"❌ {e}")
            return False
    
    async def validate_token(self) -> bool:
        """Validate current access token."""
        try:
            headers = self._get_auth_headers()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/auth/validate", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Token is valid for user: {result['email']}")
                    return True
                else:
                    print(f"❌ Token validation failed: {response.status_code} - {response.text}")
                    return False
        except ValueError as e:
            print(f"❌ {e}")
            return False


async def run_full_test():
    """Run a complete authentication flow test."""
    tester = AuthTester()
    
    print("🚀 Starting X University Authentication Test")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check")
    if not await tester.health_check():
        print("❌ API is not running. Please start the server first.")
        return
    print("✅ API is running")
    
    # Registration
    print("\n2. User Registration")
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
    
    await tester.register(email, password, full_name)
    
    # Login
    print("\n3. User Login")
    await tester.login(email, password)
    
    # Get profile
    print("\n4. Get Profile")
    await tester.get_profile()
    
    # Validate token
    print("\n5. Validate Token")
    await tester.validate_token()
    
    # Refresh token
    print("\n6. Refresh Token")
    await tester.refresh_access_token()
    
    # Test refreshed token
    print("\n7. Test Refreshed Token")
    await tester.validate_token()
    
    # Logout
    print("\n8. Logout")
    await tester.logout()
    
    # Try to access after logout (should fail)
    print("\n9. Test Access After Logout")
    await tester.get_profile()
    
    print("\n" + "=" * 50)
    print("🎉 Authentication test completed!")


async def interactive_test():
    """Run interactive authentication testing."""
    tester = AuthTester()
    
    print("🎮 Interactive X University Auth Tester")
    print("Available commands:")
    print("  health - Check API health")
    print("  register <email> <password> <name> - Register user")
    print("  login <email> <password> - Login user")
    print("  profile - Get user profile")
    print("  validate - Validate current token")
    print("  refresh - Refresh access token")
    print("  logout - Logout user")
    print("  quit - Exit")
    print("=" * 50)
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
            if not cmd:
                continue
            
            action = cmd[0].lower()
            
            if action == "quit":
                break
            elif action == "health":
                await tester.health_check()
            elif action == "register" and len(cmd) >= 4:
                await tester.register(cmd[1], cmd[2], " ".join(cmd[3:]))
            elif action == "login" and len(cmd) == 3:
                await tester.login(cmd[1], cmd[2])
            elif action == "profile":
                await tester.get_profile()
            elif action == "validate":
                await tester.validate_token()
            elif action == "refresh":
                await tester.refresh_access_token()
            elif action == "logout":
                await tester.logout()
            else:
                print("Invalid command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(run_full_test())

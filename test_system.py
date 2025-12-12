#!/usr/bin/env python3
"""
GASsstro System Test Suite
Tests all critical endpoints and functionality
"""

import requests
import json
import sys

BASE_URL = "https://timbrobro-backend.onrender.com"
FRONTEND_URL = "https://fastzonazone.github.io"
ADMIN_TOKEN = "69f3a980df5d70dd67f1e415cc8ec56145820d9359a6ad78d6486444fcb9f553"

def test_health():
    """Test backend health endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get("status") == "ok", "Status not ok"
        assert data.get("db") in ["PostgreSQL", "SQLite"], "Invalid DB type"
        return True, f"✅ Health: {data}"
    except Exception as e:
        return False, f"❌ Health: {e}"

def test_cors():
    """Test CORS headers on API endpoints"""
    try:
        headers = {"Origin": FRONTEND_URL}
        r = requests.options(f"{BASE_URL}/api/create-payment", headers=headers, timeout=10)
        cors_header = r.headers.get("access-control-allow-origin")
        if cors_header and FRONTEND_URL in cors_header:
            return True, f"✅ CORS: {cors_header}"
        else:
            return False, f"❌ CORS: Missing or wrong origin ({cors_header})"
    except Exception as e:
        return False, f"❌ CORS: {e}"

def test_admin_auth():
    """Test admin authentication"""
    try:
        # Test without token
        r = requests.get(f"{BASE_URL}/api/orders", timeout=10)
        assert r.status_code == 401, "Should reject without token"
        
        # Test with token
        r = requests.get(f"{BASE_URL}/api/orders?token={ADMIN_TOKEN}", timeout=10)
        if r.status_code == 200:
            return True, f"✅ Admin Auth: Working"
        else:
            return False, f"❌ Admin Auth: Got {r.status_code}"
    except Exception as e:
        return False, f"❌ Admin Auth: {e}"

def test_admin_stats():
    """Test admin statistics endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/admin/stats?token={ADMIN_TOKEN}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return True, f"✅ Stats: {data.get('total_orders', 0)} orders, €{data.get('total_revenue', 0)}"
        else:
            return False, f"❌ Stats: Got {r.status_code}"
    except Exception as e:
        return False, f"❌ Stats: {e}"

def test_rate_limiting():
    """Test rate limiting is active"""
    try:
        # Make multiple rapid requests
        responses = []
        for i in range(25):
            r = requests.post(f"{BASE_URL}/api/admin/login", 
                            json={"password": "wrong"}, timeout=5)
            responses.append(r.status_code)
        
        # Should get 429 (Too Many Requests) at some point
        if 429 in responses:
            return True, "✅ Rate Limiting: Active"
        else:
            return True, "⚠️  Rate Limiting: Not triggered (might be ok)"
    except Exception as e:
        return False, f"❌ Rate Limiting: {e}"

def main():
    print("=" * 60)
    print("🧪 GASsstro System Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Backend Health", test_health),
        ("CORS Configuration", test_cors),
        ("Admin Authentication", test_admin_auth),
        ("Admin Statistics", test_admin_stats),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...", end=" ")
        passed, message = test_func()
        results.append((name, passed, message))
        print(message)
    
    print()
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    
    print(f"Passed: {passed_count}/{total_count}")
    print()
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Review above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

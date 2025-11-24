"""
Test script for PsycheScore Backend API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_process_survey():
    """Test survey processing endpoint"""
    print("\nTesting survey processing...")
    
    # Mock survey data
    survey_data = {
        "wallet_address": "addr_test1qq9prvx8ufwutkwxx9cmmuuajaqmjqwujqlp9d8pvg6gupcvluken35ncjnu0puetf5jvttedkze02d5kfe890k0q9q9n0l9q",
        "survey_responses": [3, 4, 2, 5, 1, 4, 3, 2, 5, 4, 
                            3, 4, 2, 5, 1, 4, 3, 2, 5, 4,
                            3, 4, 2, 5, 1, 4, 3, 2, 5, 4,
                            3, 4, 2, 5, 1, 4, 3, 2, 5, 4,
                            3, 4, 2, 5, 1, 4, 3, 2, 5, 4],  # 50 responses
        "user_metadata": {
            "age": 25,
            "gender": "male",
            "education": "bachelor"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process_survey", json=survey_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"ML Score: {result['ml_score']}")
            print(f"ZK Proof: {'Generated' if result['zk_proof'] else 'Not generated'}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Survey processing failed: {e}")
        return False

def test_submit_to_blockchain():
    """Test blockchain submission endpoint"""
    print("\nTesting blockchain submission...")
    
    submission_data = {
        "wallet_address": "addr_test1qq9prvx8ufwutkwxx9cmmuuajaqmjqwujqlp9d8pvg6gupcvluken35ncjnu0puetf5jvttedkze02d5kfe890k0q9q9n0l9q",
        "ml_score": 75.5,
        "oracle_data": {
            "address": "addr_test1qq9prvx8ufwutkwxx9cmmuuajaqmjqwujqlp9d8pvg6gupcvluken35ncjnu0puetf5jvttedkze02d5kfe890k0q9q9n0l9q",
            "score": 75,
            "timestamp": int(time.time()),
            "oracle_vkey": "mock_oracle_vkey_hex",
            "signature": "mock_signature_hex"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit_to_blockchain", json=submission_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Transaction Hash: {result['transaction']['tx_hash']}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Blockchain submission failed: {e}")
        return False

def test_get_score():
    """Test score retrieval endpoint"""
    print("\nTesting score retrieval...")
    
    wallet_address = "addr_test1qq9prvx8ufwutkwxx9cmmuuajaqmjqwujqlp9d8pvg6gupcvluken35ncjnu0puetf5jvttedkze02d5kfe890k0q9q9n0l9q"
    
    try:
        response = requests.get(f"{BASE_URL}/get_score?wallet_address={wallet_address}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['score']:
                print(f"Score: {result['score']}")
            else:
                print("No score found for wallet")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Score retrieval failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("=== PsycheScore Backend API Tests ===")
    
    tests = [
        test_health_check,
        test_process_survey,
        test_submit_to_blockchain,
        test_get_score
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n=== Test Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Backend API is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend service.")

if __name__ == "__main__":
    run_all_tests()
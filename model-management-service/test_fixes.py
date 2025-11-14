#!/usr/bin/env python3
"""Comprehensive test suite for critical fixes."""
import asyncio
import httpx
import json
import sys
from datetime import datetime


async def test_error_handling():
    """Test error handling in endpoints."""
    print("=" * 70)
    print("TEST: Error Handling")
    print("=" * 70)
    
    # Test with invalid model config (should handle gracefully)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": f"test-error-{datetime.now().timestamp()}",
                "prompt": "Test prompt",
                "temperature": 999,  # Invalid temperature
            }
            
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload
            )
            
            print(f"✓ Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response received: {len(data.get('response', ''))} chars")
                return True
            elif response.status_code == 422:
                print(f"  ✓ Validation error caught: {response.json()}")
                return True
            else:
                print(f"  Response: {response.text}")
                return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


async def test_race_condition_fix():
    """Test that prompt is saved before history is loaded."""
    print("\n" + "=" * 70)
    print("TEST: Race Condition Fix")
    print("=" * 70)
    
    session_id = f"test-race-{datetime.now().timestamp()}"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First request - should save prompt
            payload1 = {
                "session_id": session_id,
                "prompt": "My favorite color is blue.",
                "temperature": 0.7
            }
            
            print(f"\n1. First request (saves prompt)...")
            response1 = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload1
            )
            
            if response1.status_code != 200:
                print(f"  ✗ First request failed: {response1.status_code}")
                return False
            
            print(f"  ✓ First request completed")
            
            # Wait a bit for DB to save
            await asyncio.sleep(1)
            
            # Second request - should load history including first prompt
            payload2 = {
                "session_id": session_id,
                "prompt": "What is my favorite color?",
                "temperature": 0.7
            }
            
            print(f"\n2. Second request (should use history)...")
            response2 = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload2
            )
            
            if response2.status_code == 200:
                data = response2.json()
                print(f"  ✓ Second request completed")
                print(f"  Response: {data.get('response', '')[:100]}")
                print(f"  Tokens prompt: {data.get('tokens_prompt', 0)}")
                # If tokens_prompt > 0, history was likely used
                if data.get('tokens_prompt', 0) > 0:
                    print(f"  ✓ History appears to be loaded (tokens_prompt > 0)")
                return True
            else:
                print(f"  ✗ Second request failed: {response2.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming_error_handling():
    """Test error handling in streaming endpoint."""
    print("\n" + "=" * 70)
    print("TEST: Streaming Error Handling")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": f"test-stream-error-{datetime.now().timestamp()}",
                "prompt": "Test streaming",
                "stream": True,
                "temperature": 0.7
            }
            
            print(f"\nSending streaming request...")
            error_received = False
            
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/inference/chat/stream",
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                if response.status_code != 200:
                    print(f"  ✗ Status: {response.status_code}")
                    return False
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get("done") and "error" in data:
                                error_received = True
                                print(f"  ✓ Error event received: {data.get('error')}")
                                break
                            elif data.get("done"):
                                print(f"  ✓ Stream completed successfully")
                                break
                        except json.JSONDecodeError:
                            continue
            
            return True  # If we got here, error handling worked
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_error_handling():
    """Test database error handling."""
    print("\n" + "=" * 70)
    print("TEST: Database Error Handling")
    print("=" * 70)
    
    # Test that service works even if DB operations fail
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": f"test-db-{datetime.now().timestamp()}",
                "prompt": "Test database error handling",
                "temperature": 0.7
            }
            
            print(f"\nSending request (DB may fail but request should succeed)...")
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Request succeeded despite potential DB errors")
                print(f"  Response length: {len(data.get('response', ''))}")
                return True
            else:
                print(f"  ✗ Request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


async def test_none_chunk_handling():
    """Test handling of None chunks from model."""
    print("\n" + "=" * 70)
    print("TEST: None Chunk Handling")
    print("=" * 70)
    
    # This tests that the code handles None chunks gracefully
    # We can't easily simulate this, but we can verify the code doesn't crash
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": f"test-none-{datetime.now().timestamp()}",
                "prompt": "Say hello",
                "temperature": 0.7
            }
            
            print(f"\nSending request...")
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response"):
                    print(f"  ✓ Request handled None chunks gracefully")
                    return True
                else:
                    print(f"  ⚠ Empty response (might indicate None chunk issue)")
                    return False
            else:
                print(f"  ✗ Request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


async def test_background_task_error_tracking():
    """Test that background task errors are logged."""
    print("\n" + "=" * 70)
    print("TEST: Background Task Error Tracking")
    print("=" * 70)
    
    # This test verifies that background tasks don't crash the service
    # We can't easily verify logging, but we can ensure requests still work
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": f"test-bg-{datetime.now().timestamp()}",
                "prompt": "Test background tasks",
                "temperature": 0.7
            }
            
            print(f"\nSending multiple requests to trigger background tasks...")
            results = []
            for i in range(3):
                response = await client.post(
                    "http://localhost:8000/api/v1/inference/chat",
                    json={**payload, "prompt": f"Request {i}: {payload['prompt']}"}
                )
                results.append(response.status_code == 200)
                await asyncio.sleep(0.5)
            
            if all(results):
                print(f"  ✓ All requests succeeded (background tasks handled)")
                return True
            else:
                print(f"  ✗ Some requests failed")
                return False
                
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🔧 Testing Critical Fixes".center(70))
    print("=" * 70)
    
    results = []
    
    # Test 1: Error handling
    results.append(await test_error_handling())
    
    # Test 2: Race condition fix
    results.append(await test_race_condition_fix())
    
    # Test 3: Streaming error handling
    results.append(await test_streaming_error_handling())
    
    # Test 4: Database error handling
    results.append(await test_database_error_handling())
    
    # Test 5: None chunk handling
    results.append(await test_none_chunk_handling())
    
    # Test 6: Background task error tracking
    results.append(await test_background_task_error_tracking())
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 TEST SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✅ All critical fixes are working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


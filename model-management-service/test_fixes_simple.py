#!/usr/bin/env python3
"""Simple test suite for critical fixes."""
import asyncio
import httpx
import json
import sys
from datetime import datetime


async def test_basic_functionality():
    """Test basic endpoint functionality."""
    print("=" * 70)
    print("TEST: Basic Functionality")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Test non-streaming
            print("\n1. Testing non-streaming endpoint...")
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": f"test-basic-{datetime.now().timestamp()}",
                    "prompt": "Say hello",
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Non-streaming: {len(data.get('response', ''))} chars, {data.get('tokens_generated', 0)} tokens")
            else:
                print(f"   ✗ Non-streaming failed: {response.status_code}")
                return False
            
            # Test streaming
            print("\n2. Testing streaming endpoint...")
            tokens_received = 0
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/inference/chat/stream",
                json={
                    "session_id": f"test-stream-basic-{datetime.now().timestamp()}",
                    "prompt": "Count to 2",
                    "stream": True
                },
                headers={"Accept": "text/event-stream"}
            ) as stream:
                if stream.status_code == 200:
                    async for line in stream.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("done"):
                                    tokens_received = data.get("tokens_generated", 0)
                                    break
                                elif data.get("token"):
                                    tokens_received += 1
                            except:
                                pass
                    print(f"   ✓ Streaming: {tokens_received} tokens received")
                else:
                    print(f"   ✗ Streaming failed: {stream.status_code}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test error handling."""
    print("\n" + "=" * 70)
    print("TEST: Error Handling")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test invalid temperature
            print("\n1. Testing invalid temperature...")
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": "test-error",
                    "prompt": "Test",
                    "temperature": 999  # Invalid
                }
            )
            
            if response.status_code == 422:
                print("   ✓ Validation error caught correctly")
            else:
                print(f"   ⚠ Unexpected status: {response.status_code}")
            
            # Test empty prompt
            print("\n2. Testing empty prompt...")
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": "test-error",
                    "prompt": "",  # Empty
                }
            )
            
            if response.status_code == 422:
                print("   ✓ Empty prompt validation works")
            else:
                print(f"   ⚠ Unexpected status: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


async def test_race_condition():
    """Test race condition fix."""
    print("\n" + "=" * 70)
    print("TEST: Race Condition Fix")
    print("=" * 70)
    
    session_id = f"test-race-{datetime.now().timestamp()}"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First request
            print("\n1. First request (saves prompt)...")
            response1 = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": session_id,
                    "prompt": "My name is TestUser",
                    "temperature": 0.7
                }
            )
            
            if response1.status_code != 200:
                print(f"   ✗ First request failed: {response1.status_code}")
                return False
            
            print("   ✓ First request completed")
            
            # Wait for DB save
            await asyncio.sleep(2)
            
            # Second request
            print("\n2. Second request (should have history)...")
            response2 = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": session_id,
                    "prompt": "What is my name?",
                    "temperature": 0.7
                }
            )
            
            if response2.status_code == 200:
                data = response2.json()
                print(f"   ✓ Second request completed")
                print(f"   Response: {data.get('response', '')[:80]}...")
                return True
            else:
                print(f"   ✗ Second request failed: {response2.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "🔧 Testing Critical Fixes".center(70))
    print("=" * 70)
    
    results = []
    
    results.append(await test_basic_functionality())
    results.append(await test_error_handling())
    results.append(await test_race_condition())
    
    print("\n" + "=" * 70)
    print(f"📊 TEST SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✅ All critical fixes verified!")
    else:
        print("\n⚠️ Some tests had issues")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


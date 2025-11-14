#!/usr/bin/env python3
"""Test both streaming and non-streaming endpoints."""
import asyncio
import httpx
import json
import sys
from datetime import datetime


async def test_non_streaming():
    """Test non-streaming endpoint."""
    print("=" * 70)
    print("TEST 1: Non-Streaming Endpoint")
    print("=" * 70)
    
    prompt = "Explain what Python is in 2 sentences."
    session_id = f"test-nonstream-{datetime.now().timestamp()}"
    
    print(f"\n📤 PROMPT:")
    print(f"   {prompt}")
    print(f"\n📋 Request Details:")
    print(f"   Session ID: {session_id}")
    print(f"   Temperature: 0.7")
    print(f"   Stream: false")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": session_id,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            }
            
            print(f"\n⏳ Sending request...")
            start_time = datetime.now()
            
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"⏱️  Response Time: {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ RESPONSE:")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Response Length: {len(data.get('response', ''))} characters")
                print(f"   Tokens Generated: {data.get('tokens_generated', 0)}")
                print(f"   Tokens Prompt: {data.get('tokens_prompt', 0)}")
                print(f"   Cache Hit: {data.get('cache_hit', False)}")
                print(f"   Cache Type: {data.get('cache_type', 'N/A')}")
                print(f"   Latency: {data.get('latency_ms', 0):.2f} ms")
                print(f"   Timestamp: {data.get('timestamp')}")
                print(f"\n📝 Full Response:")
                print(f"   {data.get('response', '')[:200]}...")
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming():
    """Test streaming endpoint."""
    print("\n" + "=" * 70)
    print("TEST 2: Streaming Endpoint")
    print("=" * 70)
    
    prompt = "Count from 1 to 5, saying each number on a new line."
    session_id = f"test-stream-{datetime.now().timestamp()}"
    
    print(f"\n📤 PROMPT:")
    print(f"   {prompt}")
    print(f"\n📋 Request Details:")
    print(f"   Session ID: {session_id}")
    print(f"   Temperature: 0.7")
    print(f"   Stream: true")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "session_id": session_id,
                "prompt": prompt,
                "stream": True,
                "temperature": 0.7
            }
            
            print(f"\n⏳ Sending streaming request...")
            print(f"\n📥 STREAMING RESPONSE (tokens as they arrive):")
            print(f"   ", end="", flush=True)
            
            start_time = datetime.now()
            full_response = ""
            tokens_received = 0
            first_token_time = None
            complete_received = False
            stream_error = None
            
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/inference/chat/stream",
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"\n❌ Error: {response.status_code}")
                    print(f"   {error_text.decode()}")
                    return False
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(data_str)
                            token = data.get("token", "")
                            done = data.get("done", False)
                            
                            if token:
                                if first_token_time is None:
                                    first_token_time = datetime.now()
                                    time_to_first_token = (first_token_time - start_time).total_seconds()
                                    print(f"\n   ⚡ First token received in {time_to_first_token:.2f}s\n   ", end="", flush=True)
                                
                                print(token, end="", flush=True)
                                full_response += token
                                tokens_received += 1
                            
                            if done:
                                complete_received = True
                                elapsed = (datetime.now() - start_time).total_seconds()
                                
                                print(f"\n\n✅ STREAM COMPLETE:")
                                print(f"   Total Tokens Received: {tokens_received}")
                                print(f"   Tokens Generated: {data.get('tokens_generated', 0)}")
                                print(f"   Tokens Prompt: {data.get('tokens_prompt', 0)}")
                                print(f"   Latency: {data.get('latency_ms', 0):.2f} ms")
                                print(f"   Total Time: {elapsed:.2f} seconds")
                                print(f"   Cache Hit: {data.get('cache_hit', False)}")
                                
                                if "error" in data:
                                    stream_error = data.get("error")
                                    print(f"   ⚠️  Error: {stream_error}")
                                
                                break
                        except json.JSONDecodeError:
                            continue
            
            if complete_received:
                print(f"\n📝 Full Response:")
                print(f"   {full_response[:200]}...")
                return stream_error is None
            else:
                print(f"\n⚠️ Stream ended without completion marker")
                return False
                
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_both_with_same_session():
    """Test both endpoints with the same session to verify history."""
    print("\n" + "=" * 70)
    print("TEST 3: Both Endpoints with Same Session")
    print("=" * 70)
    
    session_id = f"test-both-{datetime.now().timestamp()}"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First request - non-streaming
            print(f"\n1. Non-streaming request...")
            response1 = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json={
                    "session_id": session_id,
                    "prompt": "My favorite programming language is Python.",
                    "temperature": 0.7
                }
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                print(f"   ✓ Response: {data1.get('response', '')[:80]}...")
            else:
                print(f"   ✗ Failed: {response1.status_code}")
                return False
            
            await asyncio.sleep(1)
            
            # Second request - streaming
            print(f"\n2. Streaming request (should use history)...")
            tokens_received = 0
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/inference/chat/stream",
                json={
                    "session_id": session_id,
                    "prompt": "What is my favorite programming language?",
                    "stream": True
                },
                headers={"Accept": "text/event-stream"}
            ) as response2:
                if response2.status_code == 200:
                    async for line in response2.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if data.get("token"):
                                    tokens_received += 1
                                if data.get("done"):
                                    print(f"   ✓ Stream completed: {tokens_received} tokens")
                                    print(f"   Response: {data.get('tokens_prompt', 0)} prompt tokens (includes history)")
                                    return True
                            except:
                                pass
                else:
                    print(f"   ✗ Failed: {response2.status_code}")
                    return False
                    
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 Testing Model Management Endpoints".center(70))
    print("=" * 70)
    
    results = []
    
    # Test 1: Non-streaming
    results.append(await test_non_streaming())
    
    # Wait between tests
    await asyncio.sleep(2)
    
    # Test 2: Streaming
    results.append(await test_streaming())
    
    # Wait between tests
    await asyncio.sleep(2)
    
    # Test 3: Both with same session
    results.append(await test_both_with_same_session())
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 TEST SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✅ All endpoints are working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


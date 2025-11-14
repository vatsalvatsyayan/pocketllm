#!/usr/bin/env python3
"""Test script for streaming and non-streaming endpoints."""
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
            response = await client.post(
                "http://localhost:8000/api/v1/inference/chat",
                json=payload
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ RESPONSE:")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Response: {data.get('response')}")
                print(f"   Tokens Generated: {data.get('tokens_generated')}")
                print(f"   Tokens Prompt: {data.get('tokens_prompt')}")
                print(f"   Cache Hit: {data.get('cache_hit')}")
                print(f"   Latency: {data.get('latency_ms'):.2f} ms")
                print(f"   Timestamp: {data.get('timestamp')}")
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
            
            print(f"\n⏳ Sending request...")
            print(f"\n📥 STREAMING RESPONSE:")
            print(f"   ", end="", flush=True)
            
            full_response = ""
            tokens_received = 0
            
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
                                print(token, end="", flush=True)
                                full_response += token
                                tokens_received += 1
                            
                            if done:
                                print(f"\n\n✅ STREAM COMPLETE:")
                                print(f"   Total Tokens: {tokens_received}")
                                print(f"   Tokens Generated: {data.get('tokens_generated', 0)}")
                                print(f"   Tokens Prompt: {data.get('tokens_prompt', 0)}")
                                print(f"   Latency: {data.get('latency_ms', 0):.2f} ms")
                                print(f"   Cache Hit: {data.get('cache_hit', False)}")
                                print(f"\n📝 Full Response:")
                                print(f"   {full_response}")
                                return True
                        except json.JSONDecodeError:
                            continue
            
            print(f"\n⚠️ Stream ended without completion marker")
            return False
                
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 Starting Endpoint Tests".center(70))
    print("=" * 70)
    
    results = []
    
    # Test 1: Non-streaming
    results.append(await test_non_streaming())
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Test 2: Streaming
    results.append(await test_streaming())
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 TEST SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


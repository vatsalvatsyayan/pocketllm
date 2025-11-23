#!/usr/bin/env python3
"""
Create demo user in MongoDB.

Usage:
    python scripts/create_demo_user.py
    or
    docker compose exec backend python scripts/create_demo_user.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.utils.security import hash_password


async def create_demo_user():
    """Create demo user in MongoDB."""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
    users_collection = db[settings.users_collection]
    
    demo_email = "demo@pocketllm.com"
    demo_password = "demo123"
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": demo_email.lower()})
    if existing_user:
        print(f"✅ Demo user already exists: {demo_email}")
        client.close()
        return
    
    # Create demo user
    from datetime import datetime
    password_hash = hash_password(demo_password)
    
    user_doc = {
        "email": demo_email.lower(),
        "full_name": "Demo User",
        "avatar_url": None,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    result = await users_collection.insert_one(user_doc)
    print(f"✅ Demo user created successfully!")
    print(f"   Email: {demo_email}")
    print(f"   Password: {demo_password}")
    print(f"   User ID: {result.inserted_id}")
    
    # Ensure email index exists
    await users_collection.create_index("email", unique=True)
    print(f"✅ Email index ensured")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_demo_user())


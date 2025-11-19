"""
MongoDB connection manager with singleton pattern.
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Singleton database manager."""
    
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to MongoDB."""
        if self._client is None:
            mongodb_url = os.getenv("MONGODB_URL")
            db_name = os.getenv("MONGODB_DB_NAME", "sourcesage")
            
            if not mongodb_url:
                print("⚠️ WARNING: MONGODB_URL not set. Running without database.")
                return
            
            try:
                self._client = AsyncIOMotorClient(mongodb_url)
                self._db = self._client[db_name]
                
                # Test connection
                await self._client.admin.command('ping')
                print(f"✅ Connected to MongoDB: {db_name}")
            
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                self._client = None
                self._db = None
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("🔌 Disconnected from MongoDB")
    
    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance."""
        return self._db
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._db is not None


# Global instance
db_manager = DatabaseManager()


async def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Dependency for getting database."""
    return db_manager.get_database()

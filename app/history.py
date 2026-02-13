import redis
import json
import os
from typing import List, Dict

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

class ChatHistoryManager:
    def __init__(self):
        try:
            self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            self.client.ping()
            self.enabled = True
            print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"Redis not available: {e}. Chat history will be disabled.")
            self.enabled = False

    def get_history(self, session_id: str) -> List[Dict]:
        if not self.enabled: return []
        data = self.client.get(f"history:{session_id}")
        return json.loads(data) if data else []

    def save_message(self, session_id: str, role: str, content: str):
        if not self.enabled: return
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        # Keep only last 20 messages for context
        self.client.set(f"history:{session_id}", json.dumps(history[-20:]))

    def get_sessions(self) -> List[str]:
        if not self.enabled: return []
        keys = self.client.keys("history:*")
        return [k.split(":")[1] for k in keys]

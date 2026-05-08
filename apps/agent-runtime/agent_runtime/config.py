"""Configuration for the Architecture Agent Runtime."""
import os

# LLM
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Services
AGENT_RUNTIME_URL = os.getenv("AGENT_RUNTIME_HOST", "http://localhost:8003")
LLM_ROUTER_URL = os.getenv("LLM_ROUTER_HOST", "http://localhost:8002")

"""
Stemations - Test Gemma 4 Connectivity & Agent Skill Ingestion
Tests basic connectivity with Google GenAI SDK and the stem-animator skill.
"""
import os
import sys
from dotenv import load_dotenv

# Ensure utf-8 output on Windows terminal
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    print("[ERROR] GEMINI_API_KEY is not set!")
    print("Please create a .env file and add your GEMINI_API_KEY from https://aistudio.google.com/")
    sys.exit(1)

print("[KEY] GEMINI_API_KEY detected. Connecting to Google GenAI...")

try:
    from google import genai
    from harness.context import SkillContextLoader
    
    # 1. Test Context / Skill Loading
    loader = SkillContextLoader()
    skill_info = loader.load_skill()
    skill_name = skill_info['metadata'].get('name', 'stem-animator')
    skill_ver = skill_info['metadata'].get('version', '1.0.0')
    print(f"[OK] Loaded Agent Skill: {skill_name} (v{skill_ver})")
    
    # 2. Test Model API Call
    client = genai.Client(api_key=api_key)
    
    # Try Gemma 4 first, then fallback to gemini-2.5-flash
    test_model = "gemma-4-26b-a4b-it"
    print(f"[INFO] Sending test request to model: {test_model}...")
    
    try:
        response = client.models.generate_content(
            model=test_model,
            contents="Explain what an API is in two sentences."
        )
    except Exception as e:
        print(f"[NOTICE] {test_model} returned error ({e}). Testing fallback model 'gemini-2.5-flash'...")
        test_model = "gemini-2.5-flash"
        response = client.models.generate_content(
            model=test_model,
            contents="Explain what an API is in two sentences."
        )
        
    print(f"[SUCCESS] Response received from {test_model}:")
    print("-" * 50)
    print(response.text.strip())
    print("-" * 50)
    print("[OK] System connection test passed! You are ready to run Stemations.")

except ImportError as e:
    print(f"[ERROR] Missing package: {e}")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"[ERROR] API call failed: {e}")

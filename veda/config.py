import os
from dotenv import load_dotenv

# Load tactical environment variables
load_dotenv()

class VedaConfig:
    # System Identity
    NAME = "Veda"
    PERSONA = "Friday"
    VERSION = "1.2.0"

    # Security
    TACTICAL_KEY = os.getenv("VEDA_TACTICAL_KEY", "StarkSovereign77")

    # Neural Trinity (Cloud API Keys)
    DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
    GROK_KEY = os.getenv("GROK_API_KEY")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    # Models
    PRIMARY_MODEL = "llama3.2:3b"
    FALLBACK_MODEL = "tinyllama"

    # Storage
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    ETC_DIR = os.path.join(BASE_DIR, "etc")
    LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), "logs")

config = VedaConfig()

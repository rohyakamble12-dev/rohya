import subprocess
import sys

def install_dependencies():
    print("--- VEDA CORE TACTICAL INSTALLER ---")
    print("[SYSTEM]: Initiating dependency acquisition...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n[RESULT]: All tactical modules linked successfully.")
    except Exception as e:
        print(f"\n[ERROR]: Deployment failed: {e}")
        print("[ADVICE]: Please ensure you have an active internet link and administrator privileges.")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()

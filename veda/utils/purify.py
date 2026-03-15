import os
import shutil

def cleanup():
    print("[SYSTEM]: Initiating repository purification...")

    # 1. Remove binary artifacts
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"  - Purging cache: {path}")
                shutil.rmtree(path)
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                path = os.path.join(root, f)
                print(f"  - Removing artifact: {path}")
                os.remove(path)

    # 2. Verify Storage Structure
    storage = "veda/storage"
    if not os.path.exists(storage):
        os.makedirs(storage)
        print(f"  - Established tactical storage: {storage}")

    print("[RESULT]: Repository purified. Systems green.")

if __name__ == "__main__":
    cleanup()

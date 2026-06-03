import os
import subprocess
import sys
from pathlib import Path


def install_requirements():
    # 1. Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()

    # 2. Define the exact path to requirements.txt
    # This looks for the file in "/PDSP/Python_Scripts/Radioligand_Binding/requirements.txt"
    # relative to your project structure. Adjust the joins if this script sits elsewhere.
    requirements_path = (
        script_dir / "PDSP" / "Python_Scripts" / "Radioligand_Binding" / "requirements.txt"
    )

    # Fallback: If it's already running inside the Radioligand_Binding folder
    if not requirements_path.exists():
        requirements_path = script_dir / "requirements.txt"

    print(f"Looking for requirements file at: {requirements_path}")

    if not requirements_path.exists():
        print(
            f"Error: Could not find requirements.txt at {requirements_path}"
        )
        input("\nPress Enter to exit...")
        sys.exit(1)

    print("Starting package installation. Please wait...\n")

    # 3. Use sys.executable to ensure it uses the exact same Python environment
    # running this script, replacing the need for a hardcoded 'py' or 'python'
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        )
        print("\nSuccessfully installed all packages!")
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during installation: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    # Keep the terminal window open so non-technical users can see the success message
    input("\nPress Enter to close this window...")


if __name__ == "__main__":
    install_requirements()
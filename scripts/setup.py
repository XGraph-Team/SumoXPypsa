#!/usr/bin/env python3
"""
Manhattan Power Grid - Environment Setup Script
Automated setup for development and production environments.
"""

import os
import sys
import subprocess
import platform
import venv
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SetupManager:
    """Manages the setup process for Manhattan Power Grid."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.system = platform.system().lower()
        self.python_executable = sys.executable

    def print_status(self, message: str, level: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Colors.BLUE,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED
        }
        color = colors.get(level, Colors.BLUE)
        print(f"{color}{Colors.BOLD}[{level.upper()}]{Colors.END} {color}{message}{Colors.END}")

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> bool:
        """Run a command and return success status."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.print_status(f"Command failed: {' '.join(command)}", "error")
            self.print_status(f"Error: {e.stderr}", "error")
            return False

    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        self.print_status("Checking Python version...")

        version = sys.version_info
        if version.major != 3 or version.minor < 8:
            self.print_status(
                f"Python 3.8+ required. Current version: {version.major}.{version.minor}.{version.micro}",
                "error"
            )
            return False

        self.print_status(f"Python {version.major}.{version.minor}.{version.micro} checkmark", "success")
        return True

    def create_virtual_environment(self) -> bool:
        """Create and activate virtual environment."""
        self.print_status("Creating virtual environment...")

        if self.venv_path.exists():
            self.print_status("Virtual environment already exists", "warning")
            return True

        try:
            venv.create(self.venv_path, with_pip=True)
            self.print_status("Virtual environment created checkmark", "success")
            return True
        except Exception as e:
            self.print_status(f"Failed to create virtual environment: {e}", "error")
            return False

    def get_venv_python(self) -> Path:
        """Get the Python executable in the virtual environment."""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.print_status("Installing Python dependencies...")

        python_exe = self.get_venv_python()
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.print_status("requirements.txt not found", "error")
            return False

        return self.run_command([str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)])

    def check_sumo_installation(self) -> bool:
        """Check if SUMO is installed and configured."""
        self.print_status("Checking SUMO installation...")

        sumo_home = os.environ.get("SUMO_HOME")
        if not sumo_home:
            self.print_status("SUMO_HOME environment variable not set", "warning")
            self.provide_sumo_instructions()
            return False

        sumo_binary = "sumo.exe" if self.system == "windows" else "sumo"
        sumo_path = Path(sumo_home) / "bin" / sumo_binary

        if not sumo_path.exists():
            self.print_status(f"SUMO binary not found at {sumo_path}", "error")
            return False

        self.print_status("SUMO installation found checkmark", "success")
        return True

    def provide_sumo_instructions(self):
        """Provide instructions for installing SUMO."""
        self.print_status("SUMO Installation Instructions:", "info")
        print("\n1. Download SUMO from: https://eclipse.org/sumo/")
        print("2. Install SUMO following the platform-specific instructions")
        print("3. Set the SUMO_HOME environment variable to the installation directory")
        print("4. Add SUMO_HOME/bin to your PATH")

        if self.system == "windows":
            print("\nFor Windows:")
            print("- Download the Windows installer")
            print("- Set SUMO_HOME=C:\\Program Files (x86)\\Eclipse\\Sumo")
            print("- Add %SUMO_HOME%\\bin to PATH")
        elif self.system == "linux":
            print("\nFor Linux (Ubuntu/Debian):")
            print("- sudo apt-get install sumo sumo-tools sumo-doc")
            print("- export SUMO_HOME=/usr/share/sumo")
        elif self.system == "darwin":
            print("\nFor macOS:")
            print("- brew install sumo")
            print("- export SUMO_HOME=/opt/homebrew/share/sumo")

    def create_environment_file(self) -> bool:
        """Create .env file from template."""
        self.print_status("Creating environment configuration...")

        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if env_file.exists():
            self.print_status(".env file already exists", "warning")
            return True

        if not env_example.exists():
            # Create a basic .env file
            env_content = """# Manhattan Power Grid Configuration

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///manhattan_grid.db

# SUMO Configuration
SUMO_HOME=/path/to/sumo

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Mapbox Configuration (optional)
MAPBOX_ACCESS_TOKEN=your-mapbox-token-here

# Logging Level
LOG_LEVEL=INFO
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
        else:
            shutil.copy(env_example, env_file)

        self.print_status("Environment file created checkmark", "success")
        self.print_status("Please edit .env file with your configuration", "info")
        return True

    def create_data_directories(self) -> bool:
        """Create necessary data directories."""
        self.print_status("Creating data directories...")

        directories = [
            "data/cache",
            "data/output",
            "data/temp",
            "logs",
            "models"
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        self.print_status("Data directories created checkmark", "success")
        return True

    def test_installation(self) -> bool:
        """Test the installation by importing key modules."""
        self.print_status("Testing installation...")

        python_exe = self.get_venv_python()

        test_script = '''
import sys
try:
    import flask
    import numpy
    import pandas
    import sklearn
    import pypsa
    print("checkmark All core dependencies imported successfully")
except ImportError as e:
    print(f"x Import error: {e}")
    sys.exit(1)
'''

        try:
            result = subprocess.run(
                [str(python_exe), "-c", test_script],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_status("Installation test passed checkmark", "success")
            return True
        except subprocess.CalledProcessError as e:
            self.print_status("Installation test failed", "error")
            self.print_status(e.stdout + e.stderr, "error")
            return False

    def print_next_steps(self):
        """Print instructions for next steps."""
        print(f"\n{Colors.GREEN}{Colors.BOLD}Setup completed successfully!{Colors.END}\n")

        print("Next steps:")
        print("1. Activate the virtual environment:")

        if self.system == "windows":
            print(f"   {Colors.BLUE}venv\\Scripts\\activate{Colors.END}")
        else:
            print(f"   {Colors.BLUE}source venv/bin/activate{Colors.END}")

        print(f"2. Edit the .env file with your configuration")
        print(f"3. Run the application:")
        print(f"   {Colors.BLUE}python main_complete_integration.py{Colors.END}")
        print(f"4. Open your browser to: {Colors.BLUE}http://localhost:5000{Colors.END}")

        if not self.check_sumo_installation():
            print(f"\n{Colors.YELLOW}Note: SUMO is not properly configured. Vehicle simulation will not work.{Colors.END}")

    def setup(self) -> bool:
        """Run the complete setup process."""
        print(f"{Colors.GREEN}{Colors.BOLD}Manhattan Power Grid - Setup{Colors.END}")
        print("=" * 50)

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Creating environment file", self.create_environment_file),
            ("Creating data directories", self.create_data_directories),
            ("Testing installation", self.test_installation),
        ]

        for step_name, step_func in steps:
            if not step_func():
                self.print_status(f"Setup failed at: {step_name}", "error")
                return False

        # Check SUMO (non-critical)
        self.check_sumo_installation()

        self.print_next_steps()
        return True


def main():
    """Main setup function."""
    setup_manager = SetupManager()

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Manhattan Power Grid Setup Script")
        print("\nUsage:")
        print("  python scripts/setup.py        # Run full setup")
        print("  python scripts/setup.py --help # Show this help")
        return

    success = setup_manager.setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
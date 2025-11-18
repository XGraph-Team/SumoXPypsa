#!/usr/bin/env python3
"""
Manhattan Power Grid - Application Starter
Smart application starter with environment detection and validation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ApplicationStarter:
    """Manages the application startup process."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.system = platform.system().lower()
        self.main_script = self.project_root / "main_complete_integration.py"

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

    def get_venv_python(self) -> Path:
        """Get the Python executable in the virtual environment."""
        if self.system == "windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def check_virtual_environment(self) -> bool:
        """Check if virtual environment exists and is activated."""
        python_exe = self.get_venv_python()

        if not python_exe.exists():
            self.print_status("Virtual environment not found", "error")
            self.print_status("Please run the setup script first:", "info")
            self.print_status("  python scripts/setup.py", "info")
            return False

        # Check if we're in the virtual environment
        current_python = Path(sys.executable)
        if current_python != python_exe:
            self.print_status("Virtual environment not activated", "warning")
            self.print_status("Please activate the virtual environment:", "info")
            if self.system == "windows":
                self.print_status("  venv\\Scripts\\activate", "info")
            else:
                self.print_status("  source venv/bin/activate", "info")
            return False

        self.print_status("Virtual environment active checkmark", "success")
        return True

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        self.print_status("Checking dependencies...")

        required_packages = [
            "flask",
            "numpy",
            "pandas",
            "scikit-learn",
            "pypsa"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.print_status(f"Missing packages: {', '.join(missing_packages)}", "error")
            self.print_status("Please install dependencies:", "info")
            self.print_status("  pip install -r requirements.txt", "info")
            return False

        self.print_status("All dependencies available checkmark", "success")
        return True

    def check_configuration(self) -> bool:
        """Check if configuration files exist."""
        self.print_status("Checking configuration...")

        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.print_status(".env file not found", "warning")
            self.print_status("Creating default configuration...", "info")
            self.create_default_env()

        self.print_status("Configuration available checkmark", "success")
        return True

    def create_default_env(self):
        """Create a default .env file."""
        env_content = """# Manhattan Power Grid Configuration

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///manhattan_grid.db

# SUMO Configuration (update with your SUMO installation path)
SUMO_HOME=/path/to/sumo

# Optional: OpenAI API Key for AI features
# OPENAI_API_KEY=your-api-key-here

# Optional: Mapbox token for enhanced maps
# MAPBOX_ACCESS_TOKEN=your-token-here

# Logging Level
LOG_LEVEL=INFO
"""
        env_file = self.project_root / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)

    def check_sumo(self) -> bool:
        """Check SUMO installation (non-critical)."""
        sumo_home = os.environ.get("SUMO_HOME")
        if not sumo_home:
            self.print_status("SUMO_HOME not set - vehicle simulation will be limited", "warning")
            return False

        sumo_binary = "sumo.exe" if self.system == "windows" else "sumo"
        sumo_path = Path(sumo_home) / "bin" / sumo_binary

        if not sumo_path.exists():
            self.print_status("SUMO binary not found - vehicle simulation will be limited", "warning")
            return False

        self.print_status("SUMO available checkmark", "success")
        return True

    def start_application(self, debug: bool = False, port: int = 5000) -> bool:
        """Start the main application."""
        self.print_status("Starting Manhattan Power Grid...", "info")

        if not self.main_script.exists():
            self.print_status("Main application script not found", "error")
            return False

        try:
            # Set environment variables
            env = os.environ.copy()
            env["FLASK_ENV"] = "development" if debug else "production"
            env["FLASK_DEBUG"] = "1" if debug else "0"

            # Start the application
            args = [sys.executable, str(self.main_script)]
            if port != 5000:
                args.extend(["--port", str(port)])

            self.print_status("Application starting...", "info")
            self.print_status(f"Open your browser to: http://localhost:{port}", "success")
            print("")

            subprocess.run(args, env=env, cwd=self.project_root)
            return True

        except KeyboardInterrupt:
            self.print_status("Application stopped by user", "info")
            return True
        except Exception as e:
            self.print_status(f"Failed to start application: {e}", "error")
            return False

    def run_pre_flight_checks(self) -> bool:
        """Run all pre-flight checks."""
        print(f"{Colors.GREEN}{Colors.BOLD}Manhattan Power Grid - Startup{Colors.END}")
        print("=" * 50)

        checks = [
            ("Virtual environment", self.check_virtual_environment),
            ("Dependencies", self.check_dependencies),
            ("Configuration", self.check_configuration),
        ]

        for check_name, check_func in checks:
            if not check_func():
                self.print_status(f"Pre-flight check failed: {check_name}", "error")
                return False

        # Non-critical checks
        self.check_sumo()

        print("")
        return True

    def start(self, debug: bool = False, port: int = 5000) -> bool:
        """Main startup function."""
        if not self.run_pre_flight_checks():
            return False

        return self.start_application(debug=debug, port=port)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Manhattan Power Grid Application Starter")
    parser.add_argument("--debug", action="store_true", help="Start in debug mode")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--no-checks", action="store_true", help="Skip pre-flight checks")

    args = parser.parse_args()

    starter = ApplicationStarter()

    if args.no_checks:
        success = starter.start_application(debug=args.debug, port=args.port)
    else:
        success = starter.start(debug=args.debug, port=args.port)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
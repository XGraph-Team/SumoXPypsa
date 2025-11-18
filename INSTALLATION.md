# 📦 Installation Guide - Manhattan Power Grid Co-Simulation

Complete step-by-step installation instructions for all platforms.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Platform-Specific Notes](#platform-specific-notes)

---

## 💻 System Requirements

### Minimum Requirements:
- **CPU:** Quad-core processor (2.5 GHz+)
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **OS:** Windows 10/11, Ubuntu 20.04+, macOS 11+
- **Python:** 3.8 or higher
- **Internet:** Required for initial setup and API features

### Recommended Requirements:
- **CPU:** 8-core processor (3.0 GHz+)
- **RAM:** 16 GB or more
- **Storage:** 10 GB free space (SSD preferred)
- **GPU:** Not required, but helpful for large-scale simulations

---

## 🔧 Prerequisites

### 1. **Python 3.8+**

Check if Python is installed:
```bash
python --version
# OR
python3 --version
```

**If not installed:**
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv
  ```
- **macOS:**
  ```bash
  brew install python@3.11
  ```

### 2. **Eclipse SUMO (Traffic Simulator)**

**Required version:** SUMO 1.15.0 or higher

#### Windows Installation:
1. Download installer from [eclipse.org/sumo](https://eclipse.org/sumo/)
2. Run the `.msi` installer
3. Add SUMO to PATH:
   - Default location: `C:\Program Files (x86)\Eclipse\Sumo`
   - Add environment variable: `SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo`

#### Ubuntu/Debian Installation:
```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc
```

Set SUMO_HOME:
```bash
echo 'export SUMO_HOME="/usr/share/sumo"' >> ~/.bashrc
source ~/.bashrc
```

#### macOS Installation:
```bash
brew install sumo
echo 'export SUMO_HOME="/usr/local/opt/sumo/share/sumo"' >> ~/.zshrc
source ~/.zshrc
```

**Verify SUMO installation:**
```bash
sumo --version
echo $SUMO_HOME
```

### 3. **Git (Optional but Recommended)**

```bash
# Check if installed
git --version

# Install if needed:
# Windows: Download from git-scm.com
# Ubuntu: sudo apt install git
# macOS: brew install git
```

---

## 🚀 Installation Steps

### Step 1: Clone or Download Repository

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/XGraph-Team/SumoXPypsa.git
cd SumoXPypsa
```

**Option B: Download ZIP**
1. Go to [https://github.com/XGraph-Team/SumoXPypsa](https://github.com/XGraph-Team/SumoXPypsa)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### Step 2: Create Virtual Environment

**Highly recommended to avoid dependency conflicts**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment:
# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Linux/macOS:
source venv/bin/activate
```

**Your prompt should now show `(venv)` prefix**

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- PyPSA (power system analysis)
- NumPy, Pandas (data processing)
- Scikit-learn (machine learning)
- OpenAI (LLM integration)
- And all other dependencies

**Installation may take 5-10 minutes**

### Step 5: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
# Windows: notepad .env
# Linux/macOS: nano .env
```

**Required changes in `.env`:**

1. **SUMO_HOME:**
   ```bash
   # Windows:
   SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo

   # Linux:
   SUMO_HOME=/usr/share/sumo

   # macOS:
   SUMO_HOME=/usr/local/opt/sumo/share/sumo
   ```

2. **OpenAI API Key (Optional, for LLM features):**
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```
   Get a key from: https://platform.openai.com/api-keys

3. **Secret Key (Change for production):**
   ```bash
   SECRET_KEY=generate-a-random-secret-key-here
   ```

4. **Mapbox Token (Optional, for enhanced maps):**
   ```bash
   MAPBOX_TOKEN=your-mapbox-token-here
   ```
   Get a token from: https://account.mapbox.com/access-tokens/

**Save and close the `.env` file**

### Step 6: Create Required Directories

```bash
# Create log directory
mkdir -p logs

# Create monitoring directory (if not exists)
mkdir -p monitoring

# Create data cache directory
mkdir -p data/cache
```

### Step 7: Verify Installation

Run the verification script:

```bash
python -c "import pypsa, flask, numpy, pandas, sklearn; print('All core dependencies installed successfully!')"
```

Check SUMO:
```bash
python -c "import os; print(f'SUMO_HOME: {os.environ.get(\"SUMO_HOME\")}'); import traci; print('SUMO integration ready!')"
```

---

## ⚙️ Configuration

### Basic Configuration

Open `.env` and adjust these settings:

```bash
# Server Configuration
HOST=0.0.0.0  # Listen on all interfaces
PORT=5000     # Default port

# Simulation Defaults
DEFAULT_VEHICLE_COUNT=10
DEFAULT_EV_PERCENTAGE=0.7  # 70% EVs
DEFAULT_BATTERY_MIN_SOC=0.2  # 20% minimum charge
DEFAULT_BATTERY_MAX_SOC=0.9  # 90% maximum charge

# Logging
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

### Feature Flags

Enable/disable features:

```bash
ENABLE_ML_ENGINE=True  # Machine learning analytics
ENABLE_V2G=True  # Vehicle-to-Grid
ENABLE_AI_CHATBOT=True  # LLM chatbot (requires OpenAI API key)
ENABLE_SCENARIO_CONTROLLER=True  # Time-of-day scenarios
```

---

## ✅ Verification

### Run the Application

```bash
# Make sure virtual environment is activated
python main_complete_integration.py
```

**Expected output:**
```
 * Serving Flask app 'main_complete_integration'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

### Open Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

**You should see:**
- Interactive map of Manhattan
- Control panel on the left
- System status indicators
- No error messages in terminal

### Test Basic Functions

1. **Start Vehicle Simulation:**
   - Click "Start Vehicles" button
   - You should see vehicles appear on the map
   - Check terminal for SUMO connection logs

2. **Test Power Grid:**
   - Click on a substation marker
   - Select "Fail Substation"
   - Traffic lights should turn yellow
   - EV stations should show as offline

3. **Enable V2G:**
   - With a failed substation
   - Click "Enable V2G" for that substation
   - EVs with high SOC should route to provide power

**If all tests pass, installation is successful!** ✅

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **"Module 'traci' not found"**

**Cause:** SUMO_HOME not set correctly

**Solution:**
```bash
# Check SUMO_HOME
echo $SUMO_HOME  # Linux/macOS
echo %SUMO_HOME%  # Windows

# Add to system environment variables
# Windows: System Properties → Environment Variables
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
export SUMO_HOME="/usr/share/sumo"  # Adjust path
```

#### 2. **"Port 5000 already in use"**

**Solution:**
```bash
# Option 1: Change port in .env
PORT=5001

# Option 2: Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:5000 | xargs kill -9
```

#### 3. **"OpenAI API Key not found"**

**This is only needed for LLM chatbot features**

**Solution:**
```bash
# Option 1: Add key to .env
OPENAI_API_KEY=sk-your-key-here

# Option 2: Disable LLM features
ENABLE_AI_CHATBOT=False
```

#### 4. **"No module named 'pypsa'"**

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 5. **SUMO window opens and immediately closes**

**Cause:** SUMO network files not found

**Solution:**
```bash
# Check if network files exist
ls data/manhattan.net.xml
ls data/manhattan.sumocfg

# If missing, they should be in the repository
# Re-download or check docs/
```

#### 6. **Map not loading in web interface**

**Cause:** Mapbox token not set or network issue

**Solution:**
```bash
# Check browser console (F12) for errors
# Add Mapbox token to .env (optional for basic functionality)
MAPBOX_TOKEN=your-token-here
```

---

## 🖥️ Platform-Specific Notes

### Windows

1. **Use PowerShell or Command Prompt** (not Git Bash for SUMO)
2. **Antivirus:** May need to allow Python and SUMO through firewall
3. **Path separators:** Use `\` instead of `/` in .env file paths
4. **Long paths:** Enable long path support if installation fails:
   ```powershell
   # Run as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

### Linux (Ubuntu/Debian)

1. **Python development headers** may be needed:
   ```bash
   sudo apt install python3-dev build-essential
   ```

2. **Permissions:** May need to run with sudo for ports < 1024
   ```bash
   # Use port 5000+ (recommended) OR
   sudo python main_complete_integration.py
   ```

3. **Display issues:** If running headless, disable SUMO GUI:
   ```bash
   # In configuration
   SUMO_GUI_ENABLED=False
   ```

### macOS

1. **XCode command line tools** required:
   ```bash
   xcode-select --install
   ```

2. **Homebrew** recommended for dependencies:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **M1/M2 Macs:** Some packages may need Rosetta 2:
   ```bash
   softwareupdate --install-rosetta
   ```

---

## 🎓 Next Steps

After successful installation:

1. **Read the Usage Guide:**
   ```bash
   # See README.md for detailed usage
   cat README.md
   ```

2. **Try Example Scenarios:**
   - Morning rush hour
   - Substation failure + V2G restoration
   - Heatwave scenario

3. **Explore API Documentation:**
   ```
   http://localhost:5000/api/docs
   ```

4. **Join Development:**
   - See [CONTRIBUTING.md](CONTRIBUTING.md)
   - Check [GitHub Issues](https://github.com/XGraph-Team/SumoXPypsa/issues)

---

## 📞 Support

**Need help?**
- **Issues:** [GitHub Issues](https://github.com/XGraph-Team/SumoXPypsa/issues)
- **Discussions:** [GitHub Discussions](https://github.com/XGraph-Team/SumoXPypsa/discussions)
- **Email:** Check repository for contact information

---

## 📚 Additional Resources

- **SUMO Documentation:** https://sumo.dlr.de/docs/
- **PyPSA Documentation:** https://pypsa.readthedocs.io/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Project Documentation:** See `docs/` folder

---

**Installation complete! You're ready to simulate Manhattan's power grid!** 🎉

# Contributing to Manhattan Power Grid

Thank you for your interest in contributing to the Manhattan Power Grid simulation system! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/manhattan-power-grid.git
   cd manhattan-power-grid
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/XGraph-Team/manhattan-power-grid.git
   ```

4. **Set up the development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Install SUMO** (required for traffic simulation):
   
   **Windows:**
   - Download from [Eclipse SUMO](https://eclipse.org/sumo/)
   - Run installer and add to PATH
   
   **macOS:**
   ```bash
   brew install sumo
   ```
   
   **Linux:**
   ```bash
   sudo add-apt-repository ppa:sumo/stable
   sudo apt-get update
   sudo apt-get install sumo sumo-tools sumo-doc
   ```

6. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### 2. Development Workflow

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following our coding standards

4. **Test your changes**:
   ```bash
   # Run unit tests
   python -m pytest tests/unit/

   # Run integration tests
   python -m pytest tests/integration/

   # Run all tests with coverage
   python -m pytest --cov=. tests/

   # Test the application manually
   python main_complete_integration.py
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your descriptive commit message"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code formatting
- **Use type hints** where appropriate:
  ```python
  from typing import Dict, Any, List, Optional
  
  def calculate_power_flow(voltage: float, current: float) -> float:
      """Calculate power flow from voltage and current."""
      return voltage * current
  ```

- **Add comprehensive docstrings** for all functions, classes, and modules:
  ```python
  def process_vehicle_data(
      vehicle_id: str, 
      battery_soc: float,
      location: tuple[float, float]
  ) -> Dict[str, Any]:
      """
      Process vehicle data for V2G analysis.

      Args:
          vehicle_id: Unique identifier for the vehicle
          battery_soc: State of charge (0.0 to 1.0)
          location: (latitude, longitude) tuple

      Returns:
          Dictionary containing:
              - vehicle_id: str
              - battery_soc: float
              - location: tuple
              - v2g_eligible: bool
              - estimated_range: float

      Raises:
          ValueError: If battery_soc is not between 0 and 1
      """
  ```

- **Use meaningful variable names**:
  ```python
  # Good
  substation_load_percentage = calculate_load_percentage(substation)
  vehicle_battery_capacity = get_battery_capacity(vehicle_model)

  # Avoid
  x = calc_load(s)
  cap = get_cap(v_m)
  ```

### Frontend Code Style

- **Use consistent indentation** (2 spaces for HTML/CSS/JS)
- **Follow semantic HTML** structure
- **Use CSS classes** instead of inline styles
- **Comment complex JavaScript** functions:
  ```javascript
  /**
   * Calculate the optimal charging route for an EV
   * @param {Object} vehicle - Vehicle object with battery info
   * @param {Array} stations - Available charging stations
   * @returns {Object} Optimal route with charging stops
   */
  function calculateOptimalRoute(vehicle, stations) {
    // Implementation
  }
  ```

### Commit Message Format

Follow the conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```bash
feat(v2g): add emergency response activation

- Implemented automatic V2G activation during outages
- Added priority queue for high-SOC vehicles
- Updated UI to show V2G status indicators

Closes #123

---

fix(sumo): correct vehicle spawn rate calculation

Vehicle spawn rate was using incorrect time units,
causing too many vehicles to spawn simultaneously.

Fixes #456
```

### File Organization

```
manhattan-power-grid/
├── api/            # API endpoints
│   ├── grid/       # Power grid endpoints
│   ├── sumo/       # Vehicle simulation endpoints
│   └── v2g/        # V2G endpoints
├── core/           # Core system components
│   ├── power_system.py
│   ├── sumo_manager.py
│   └── ev_battery_model.py
├── config/         # Configuration files
├── data/           # Data files and datasets
├── docs/           # Documentation
├── static/         # Frontend assets
├── templates/      # HTML templates
├── tests/          # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── utils/          # Utility functions
```

## 🧪 Testing Guidelines

### Unit Tests

- **Write tests for all new functions** and classes
- **Use descriptive test names**:
  ```python
  def test_power_flow_calculation_with_valid_inputs():
      """Test power flow calculation returns correct values."""
      assert calculate_power_flow(120, 10) == 1200

  def test_power_flow_calculation_handles_zero_current():
      """Test power flow calculation with zero current."""
      assert calculate_power_flow(120, 0) == 0

  def test_battery_soc_validation_rejects_invalid_range():
      """Test battery SOC validation rejects values outside 0-1."""
      with pytest.raises(ValueError):
          validate_battery_soc(1.5)
  ```

- **Test edge cases** and error conditions
- **Mock external dependencies**:
  ```python
  from unittest.mock import Mock, patch

  @patch('core.sumo_manager.traci')
  def test_vehicle_spawning(mock_traci):
      mock_traci.simulation.getTime.return_value = 100
      # Test implementation
  ```

### Integration Tests

- **Test component interactions**
- **Verify API endpoint responses**:
  ```python
  def test_api_substation_failure():
      response = client.post('/api/fail/Times%20Square')
      assert response.status_code == 200
      assert response.json['success'] == True
  ```

### Performance Tests

- **Monitor simulation performance**
- **Test with varying vehicle counts** (10, 100, 1000)
- **Measure API response times**
- **Profile memory usage**

### Manual Testing Checklist

Before submitting a PR:

- [ ] Application starts without errors
- [ ] Map loads correctly with all substations
- [ ] Vehicle simulation works (spawn, movement, charging)
- [ ] Substation failures trigger appropriate responses
- [ ] V2G activation works during emergencies
- [ ] AI chatbot responds correctly
- [ ] ML dashboard displays accurate data
- [ ] All UI controls are responsive
- [ ] No console errors in browser

## 🎯 Areas for Contribution

### 🔴 High Priority

- **Performance Optimization**
  - Improve SUMO simulation speed
  - Optimize power flow calculations
  - Reduce API latency

- **Test Coverage**
  - Increase unit test coverage to 80%+
  - Add end-to-end test scenarios
  - Create performance benchmarks

- **Documentation**
  - API reference documentation
  - Video tutorials
  - Architecture deep-dives

### 🟡 Medium Priority

- **New Features**
  - Weather impact on grid demand
  - Solar/wind renewable integration
  - Multi-city simulation support
  - Historical data analysis

- **UI/UX Improvements**
  - Dark mode toggle
  - Mobile responsive design
  - Advanced data visualizations
  - Real-time notifications

- **DevOps**
  - Docker containerization
  - Kubernetes deployment configs
  - CI/CD pipeline improvements

### 🟢 Good First Issues

- **Code Quality**
  - Add type hints to existing functions
  - Improve error messages
  - Add logging statements
  - Fix linting warnings

- **Documentation**
  - Fix typos and grammar
  - Add code examples
  - Improve README sections
  - Create FAQ document

## 🐛 Bug Reports

### Template

```markdown
**Environment:**
- Python version: 3.x.x
- Operating System: Windows/Mac/Linux
- SUMO version: 1.x.x
- Browser: Chrome/Firefox/Safari

**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Start the application
2. Click on...
3. Observe...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Error Logs:**
```
Paste relevant error messages here
```

**Screenshots:**
If applicable, add screenshots

**Additional Context:**
Any other relevant information
```

## 💡 Feature Requests

### Template

```markdown
**Problem Statement:**
Describe the problem this feature would solve

**Proposed Solution:**
Describe your proposed implementation

**Alternatives Considered:**
What other solutions have you considered?

**Use Cases:**
1. Scenario where this would be useful
2. Another scenario

**Implementation Complexity:**
- [ ] Small (< 1 day)
- [ ] Medium (1-5 days)
- [ ] Large (> 5 days)

**Breaking Changes:**
Will this require breaking changes?
```

## 📋 Pull Request Checklist

### Before Submitting

- [ ] Code follows PEP 8 style guidelines
- [ ] Type hints added for new functions
- [ ] Docstrings added/updated
- [ ] Tests added for new functionality
- [ ] All tests pass locally (`pytest`)
- [ ] No linting errors (`flake8`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with main
- [ ] PR description explains changes clearly

### PR Description Template

```markdown
## Summary
Brief description of changes

## Motivation
Why are these changes needed?

## Changes Made
- List of specific changes
- Another change

## Testing
How has this been tested?

## Screenshots
If UI changes, add before/after screenshots

## Related Issues
Closes #XXX
```

## 🏗️ Architecture Guidelines

### Power System Components

When working on power system features:

```python
from core.power_system import ManhattanPowerGrid

class NewPowerFeature:
    def __init__(self, grid: ManhattanPowerGrid):
        self.grid = grid
    
    def calculate_metric(self):
        # Use PyPSA for calculations
        # Follow IEEE standards
        # Consider grid constraints
```

### Vehicle Simulation

When adding vehicle features:

```python
from core.sumo_manager import SUMOManager
from core.ev_battery_model import EVBatteryModel

class VehicleFeature:
    def __init__(self, sumo_manager: SUMOManager):
        self.sumo = sumo_manager
        self.battery_model = EVBatteryModel()
    
    def update_vehicle_state(self, vehicle_id: str):
        # Integrate with SUMO
        # Use realistic physics
        # Update battery state
```

### V2G Implementation

For V2G features:

```python
from v2g_manager import V2GManager

class V2GFeature:
    def __init__(self, v2g_manager: V2GManager):
        self.v2g = v2g_manager
    
    def calculate_v2g_potential(self):
        # Consider grid stability
        # Implement bidirectional flow
        # Use market pricing
        # Respect battery constraints
```

## 🔒 Security Guidelines

### Code Security

- **Never commit secrets**: Use environment variables
  ```python
  # Bad
  API_KEY = "sk-1234567890abcdef"
  
  # Good
  import os
  API_KEY = os.getenv('API_KEY')
  ```

- **Validate all inputs**:
  ```python
  def process_input(user_input: str):
      # Sanitize input
      cleaned = sanitize(user_input)
      # Validate format
      if not validate_format(cleaned):
          raise ValueError("Invalid input format")
  ```

- **Use parameterized queries** for any database operations
- **Follow OWASP guidelines** for web security
- **Keep dependencies updated**: Run `pip audit` regularly

### Reporting Security Issues

For security vulnerabilities, please DO NOT create a public issue. Instead:

1. Email: mb4194@msstate.edu
2. Include detailed description
3. Provide steps to reproduce
4. Allow time for patch before disclosure

## 📖 Documentation Standards

### Code Documentation

- **Module level**: Describe purpose and usage
- **Class level**: Explain responsibility and interactions
- **Function level**: Document parameters, returns, and exceptions
- **Inline comments**: Explain complex logic only

### API Documentation

```python
@app.route('/api/grid/status', methods=['GET'])
def get_grid_status():
    """
    Get current power grid status.
    
    Returns:
        JSON response containing:
        - substations: dict of substation states
        - total_load: float (MW)
        - v2g_active: bool
        - timestamp: ISO 8601 string
    
    Example:
        GET /api/grid/status
        
        Response:
        {
            "substations": {...},
            "total_load": 450.5,
            "v2g_active": true,
            "timestamp": "2024-01-01T12:00:00Z"
        }
    """
```

## 🤖 Automated Checks

Our GitHub Actions CI/CD pipeline runs:

- **Linting**: `flake8` for Python style
- **Type checking**: `mypy` for type hints
- **Testing**: `pytest` with coverage report
- **Security**: `pip audit` for vulnerabilities
- **Documentation**: Link validation

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create release branch
5. Tag release: `git tag -a v2.1.0 -m "Release v2.1.0"`
6. Push tags: `git push --tags`
7. Create GitHub release
8. Deploy to production

## 📞 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/XGraph-Team/manhattan-power-grid/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/XGraph-Team/manhattan-power-grid/discussions)
- **Wiki**: [Documentation and guides](https://github.com/XGraph-Team/manhattan-power-grid/wiki)
- **Email**: mb4194@msstate.edu

## 🏆 Recognition

Contributors are recognized in:

- **Contributors section** in README.md
- **Release notes** with feature attribution
- **Git history** with detailed commits
- **Annual contributor report**

### All Contributors

We use the [All Contributors](https://allcontributors.org/) specification. Contributions of all kinds are recognized:

- 💻 Code
- 📖 Documentation
- 🎨 Design
- 🤔 Ideas
- 🧪 Testing
- 🔧 Maintenance
- 📆 Project Management

## 📋 Code of Conduct

We are committed to providing a welcoming and inclusive environment.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behaviors:**
- Harassment of any kind
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations may be reported to mb4194@msstate.edu. All complaints will be reviewed and investigated promptly and fairly.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 2.1.

## 🎉 Thank You!

Every contribution, no matter how small, helps make Manhattan Power Grid better. Whether you're:

- 🐛 Fixing a bug
- ✨ Adding a feature
- 📝 Improving documentation
- 💡 Suggesting ideas
- 🧪 Testing changes
- 👥 Helping others

**Your efforts are valued and appreciated!**

---

<div align="center">

**Happy coding! ⚡🚗🏙️**

Join us in building the future of smart city infrastructure!

[Get Started](https://github.com/XGraph-Team/manhattan-power-grid) • [Report Issues](https://github.com/XGraph-Team/manhattan-power-grid/issues) • [Join Discussions](https://github.com/XGraph-Team/manhattan-power-grid/discussions)

</div>

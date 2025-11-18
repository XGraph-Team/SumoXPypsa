# Contributing to Manhattan Power Grid

Thank you for your interest in contributing to the Manhattan Power Grid simulation system! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/manhattan-power-grid.git
   cd manhattan-power-grid
   ```

3. **Set up the development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install SUMO** (required for traffic simulation):
   - Download from: https://eclipse.org/sumo/
   - Add SUMO_HOME to your environment variables

### 2. Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Run unit tests
   python -m pytest tests/unit/

   # Run integration tests
   python -m pytest tests/integration/

   # Test the application manually
   python main_complete_integration.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your descriptive commit message"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code formatting
- **Use type hints** where appropriate:
  ```python
  def calculate_power_flow(voltage: float, current: float) -> float:
      return voltage * current
  ```

- **Add docstrings** for all functions, classes, and modules:
  ```python
  def process_vehicle_data(vehicle_id: str, battery_soc: float) -> Dict[str, Any]:
      """
      Process vehicle data for V2G analysis.

      Args:
          vehicle_id: Unique identifier for the vehicle
          battery_soc: State of charge (0.0 to 1.0)

      Returns:
          Dictionary containing processed vehicle data
      """
  ```

- **Use meaningful variable names**:
  ```python
  # Good
  substation_load_percentage = calculate_load_percentage(substation)

  # Avoid
  x = calc_load(s)
  ```

### Frontend Code Style

- **Use consistent indentation** (2 spaces for HTML/CSS/JS)
- **Follow semantic HTML** structure
- **Use CSS classes** instead of inline styles
- **Comment complex JavaScript** functions

### File Organization

- **Core systems**: Place in `core/` directory
- **API endpoints**: Organize in `api/` directory
- **Configuration**: Use `config/` directory
- **Tests**: Mirror source structure in `tests/`
- **Documentation**: Use `docs/` directory

## 🧪 Testing Guidelines

### Unit Tests

- **Write tests for all new functions** and classes
- **Use descriptive test names**:
  ```python
  def test_power_flow_calculation_with_valid_inputs():
      # Test implementation
  ```

- **Test edge cases** and error conditions
- **Mock external dependencies** (SUMO, database, APIs)

### Integration Tests

- **Test component interactions**
- **Verify API endpoint responses**
- **Test database operations**

### Manual Testing

Before submitting a PR, manually test:

1. **Application startup**: `python main_complete_integration.py`
2. **Vehicle simulation**: Start/stop vehicles, verify map updates
3. **Power grid operations**: Test substation failures and V2G
4. **AI chatbot**: Test conversation functionality
5. **ML analytics**: Verify dashboard data and predictions

## 🎯 Areas for Contribution

### High Priority

- **Performance optimization**: Improve simulation speed
- **Test coverage**: Expand unit and integration tests
- **Documentation**: API documentation, tutorials
- **Error handling**: Robust error recovery
- **Monitoring**: System health dashboards

### Medium Priority

- **New features**: Weather integration, multi-city support
- **UI/UX improvements**: Enhanced visualizations
- **Mobile support**: Responsive design improvements
- **Accessibility**: WCAG compliance

### Low Priority

- **Code refactoring**: Improve code organization
- **Developer tools**: Setup scripts, debugging tools
- **Examples**: Sample configurations, tutorials

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details**:
   - Python version
   - Operating system
   - SUMO version
   - Package versions (`pip freeze`)

2. **Steps to reproduce**:
   - Exact commands run
   - Configuration used
   - Expected vs actual behavior

3. **Error logs**:
   - Full error traceback
   - Relevant log files
   - Browser console errors (for frontend issues)

4. **Screenshots** (if applicable)

## 💡 Feature Requests

For new features:

1. **Search existing issues** to avoid duplicates
2. **Describe the use case** and problem it solves
3. **Provide examples** of expected behavior
4. **Consider implementation complexity** and alternatives
5. **Discuss architectural impact** for major features

## 📋 Pull Request Checklist

Before submitting a PR:

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] Documentation updated (if needed)
- [ ] Commit messages are descriptive
- [ ] PR description explains changes
- [ ] No merge conflicts with main branch
- [ ] Application runs without errors

## 🏗️ Architecture Guidelines

### Power System Components

- **Extend ManhattanPowerGrid** for power-related features
- **Use PyPSA** for electrical calculations
- **Follow IEEE standards** for power system modeling

### Vehicle Simulation

- **Integrate with SUMO** for traffic simulation
- **Use EVBatteryModel** for battery calculations
- **Follow realistic charging curves** and behaviors

### V2G Implementation

- **Implement bidirectional power flow** correctly
- **Consider grid stability** constraints
- **Use market-based pricing** algorithms

### Machine Learning

- **Use scikit-learn** for standard ML algorithms
- **Implement proper data validation** and preprocessing
- **Add model versioning** and evaluation metrics

## 🔒 Security Guidelines

- **Never commit secrets** or API keys
- **Use environment variables** for configuration
- **Validate all user inputs** on both frontend and backend
- **Follow OWASP guidelines** for web security
- **Use HTTPS** in production deployments

## 📖 Documentation Standards

- **Update README.md** for significant changes
- **Add API documentation** for new endpoints
- **Include code examples** in documentation
- **Write clear installation instructions**
- **Document configuration options**

## 🤖 Automated Checks

Our CI/CD pipeline runs:

- **Linting**: Code style checks
- **Testing**: Unit and integration tests
- **Security**: Dependency vulnerability scanning
- **Documentation**: Link checking and spelling

## 🏷️ Release Process

1. **Version bumping**: Follow semantic versioning (SemVer)
2. **Changelog**: Update CHANGELOG.md with new features/fixes
3. **Testing**: Comprehensive testing before release
4. **Documentation**: Update version-specific documentation
5. **Tags**: Create git tags for releases

## 📞 Getting Help

- **GitHub Discussions**: For questions and brainstorming
- **Issues**: For bug reports and feature requests
- **Discord**: [Join our community](https://discord.gg/manhattan-power-grid)
- **Email**: development@manhattan-power-grid.com

## 🏆 Recognition

Contributors are recognized in:

- **README.md**: Contributors section
- **Release notes**: Feature attribution
- **Git history**: Detailed commit attribution
- **Community**: Discord contributor role

## 📋 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful** in all interactions
- **Use inclusive language** in code and documentation
- **Focus on constructive feedback** in reviews
- **Help others learn** and grow
- **Report inappropriate behavior** to maintainers

## 🎉 Thank You!

Every contribution, no matter how small, helps make Manhattan Power Grid better. Whether you're fixing a typo, adding a feature, or improving documentation, your efforts are appreciated!

---

**Happy coding! ⚡🚗🏙️**
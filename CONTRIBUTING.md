# Contributing to LilithOSi

Thank you for your interest in contributing to LilithOSi! We welcome contributions from the community to help improve this project.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git
- [pre-commit](https://pre-commit.com/)

### Setting Up for Development

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/LilithOSi.git
   cd LilithOSi
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🛠 Development Workflow

1. **Create a new branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run tests locally** before committing
   ```bash
   pytest
   ```

4. **Commit your changes** with a descriptive message
   ```bash
   git commit -m "feat: add new feature"
   ```

5. **Push your changes** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** against the `main` branch

## 📝 Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep lines under 88 characters (Black's default)
- Type hints are encouraged for better code quality

## 🧪 Testing

- Write tests for new features and bug fixes
- Run all tests with `pytest`
- Aim for high test coverage (check with `pytest --cov=src`)
- Update documentation when adding new features

## 📦 Dependencies

- Add new dependencies to `requirements.txt`
- Pin all production dependencies with exact versions
- Group development dependencies in `requirements-dev.txt`

## 🚨 Reporting Issues

When reporting issues, please include:

1. Steps to reproduce the issue
2. Expected vs. actual behavior
3. Environment details (OS, Python version, etc.)
4. Any relevant error messages or logs

## 📜 Code of Conduct

Please note that this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🙏 Thank You!

Your contributions help make LilithOSi better for everyone. Thank you for your time and effort!

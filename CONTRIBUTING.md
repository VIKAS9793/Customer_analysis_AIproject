# Contributing to FinConnectAI

Thank you for your interest in contributing to FinConnectAI! We appreciate your time and effort in helping us improve this project.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your forked repository
   ```bash
   git clone https://github.com/VIKAS9793/FinConnectAI.git
   cd FinConnectAI
   ```
3. **Set up** the development environment
   ```bash
   make install
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them with a descriptive message
   ```bash
   git add .
   git commit -m "Add your commit message here"
   ```
3. Push your changes to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
4. Create a Pull Request (PR) to the main repository

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for static type checking

Run the following command to ensure your code follows our style guide:

```bash
make format  # Auto-format code
make lint    # Check code style
make typecheck  # Run type checking
```

## Testing

We use `pytest` for testing. To run the test suite:

```bash
make test  # Run all tests
make test-cov  # Run tests with coverage report
```

## Pull Request Guidelines

- Keep PRs focused on a single feature or bugfix
- Write clear, descriptive commit messages
- Update documentation as needed
- Ensure all tests pass before submitting a PR
- Add tests for new features or bug fixes

## Reporting Issues

When reporting issues, please include:

1. A clear description of the issue
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Any relevant error messages or logs

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing to FinConnectAI, you agree that your contributions will be licensed under the [MIT License](LICENSE).

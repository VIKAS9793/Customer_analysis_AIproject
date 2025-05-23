# FinConnectAI Documentation

Welcome to the documentation for FinConnectAI, a financial connection and analysis platform.

## Project Structure

The project is organized into the following main directories:

- ``app/``: Main application code
- ``tests/``: Test files and test data generator
- ``docs/``: Documentation source files
- ``examples/``: Example usage and demonstrations

## Development Setup

To set up the development environment:

1. Create a virtual environment:

   ```bash
   conda create -n finconnectai python=3.9 -y
   conda activate finconnectai
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Run tests:

   ```bash
   poetry run pytest tests/ -v
   ```

## Testing

The project uses pytest for testing with the following features:

- Automated model comparison
- Comprehensive test suite
- Edge case testing
- Performance benchmarks

## Documentation

To build the documentation:

```bash
poetry run sphinx-build -b html docs/ docs/_build/html
```

The documentation will be available in ``docs/_build/html``.

## Contributing

Please see ``CONTRIBUTING.md`` for details on how to contribute to this project.

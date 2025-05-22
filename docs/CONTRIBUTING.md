# Contributing to FinConnectAI

## Development Guidelines

### Code Style

1. **Python Standards**
   - Follow PEP 8 guidelines
   - Use type hints
   - Document all functions and classes
   - Maximum line length: 88 characters

2. **Documentation**
   - Docstrings for all public functions
   - Include usage examples
   - Update README for new features
   - Keep API docs current

3. **Testing**
   - Write unit tests for new code
   - Maintain 80% coverage minimum
   - Include integration tests
   - Document test cases

### Git Workflow

1. **Branches**
   ```
   main           # Production-ready code
   ├── develop    # Development branch
   ├── feature/*  # New features
   ├── bugfix/*   # Bug fixes
   └── release/*  # Release preparation
   ```

2. **Commit Messages**
   ```
   type(scope): description

   [optional body]

   [optional footer]
   ```
   Types: feat, fix, docs, style, refactor, test, chore

3. **Pull Requests**
   - Create from feature branch to develop
   - Include tests and documentation
   - Request review from team members
   - Link related issues

### Testing Guidelines

1. **Unit Tests**
   ```python
   def test_function_name():
       # Arrange
       input_data = ...
       
       # Act
       result = function_to_test(input_data)
       
       # Assert
       assert result == expected_output
   ```

2. **Integration Tests**
   ```python
   @pytest.mark.asyncio
   async def test_api_endpoint():
       async with AsyncClient() as client:
           response = await client.post("/api/endpoint", json={...})
           assert response.status_code == 200
   ```

3. **Test Coverage**
   ```bash
   # Run coverage
   pytest --cov=app tests/
   
   # Generate report
   coverage html
   ```

### Code Review Guidelines

1. **Review Checklist**
   - Code follows style guide
   - Tests are included and pass
   - Documentation is updated
   - No security vulnerabilities
   - Performance considerations
   - Error handling is proper

2. **Review Comments**
   - Be constructive and specific
   - Suggest improvements
   - Reference documentation/examples
   - Use inline code suggestions

### Development Setup

1. **Local Environment**
   ```bash
   # Clone repository
   git clone https://github.com/VIKAS9793/FinConnectAI.git
   cd FinConnectAI

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

2. **Pre-commit Hooks**
   ```bash
   # Install pre-commit
   pip install pre-commit
   pre-commit install

   # Run hooks
   pre-commit run --all-files
   ```

### Dependency Management

1. **Adding Dependencies**
   - Add to requirements.txt or setup.py
   - Document purpose in PR
   - Check license compatibility
   - Consider security implications

2. **Updating Dependencies**
   ```bash
   # Update all
   pip-compile --upgrade requirements.in
   
   # Update specific package
   pip-compile --upgrade-package package-name
   ```

### Release Process

1. **Version Numbering**
   - Follow semantic versioning
   - Update CHANGELOG.md
   - Tag releases in git

2. **Release Checklist**
   - All tests pass
   - Documentation updated
   - CHANGELOG updated
   - Version bumped
   - Release notes prepared

### Troubleshooting

1. **Common Issues**
   - Database connection errors
   - API rate limits
   - Test failures
   - Import errors

2. **Debug Tools**
   ```python
   # Debug logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Interactive debugger
   import pdb; pdb.set_trace()
   ```

### Support

- GitHub Issues for bug reports
- Discussions for questions
- Wiki for documentation
- Team chat for quick help

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional conduct

### Reporting Issues
- Use GitHub issues
- Include reproduction steps
- Provide system information
- Be patient and helpful

## License

This project is licensed under the MIT License. See LICENSE file for details.

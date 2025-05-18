Contributing to PlainSpeak
=======================

Thank you for your interest in contributing to PlainSpeak! This guide will help you get started with contributing to the project.

Setting Up Your Development Environment
-------------------------------------

1. **Fork the Repository**

   Start by forking the PlainSpeak repository on GitHub.

2. **Clone Your Fork**

   .. code-block:: bash

      git clone https://github.com/your-username/plainspeak.git
      cd plainspeak

3. **Set Up Poetry**

   PlainSpeak uses Poetry for dependency management:

   .. code-block:: bash

      # Install Poetry if you don't have it
      pip install poetry

      # Install dependencies
      poetry install

4. **Install Pre-commit Hooks**

   .. code-block:: bash

      poetry run pre-commit install

Development Workflow
------------------

1. **Create a Branch**

   Create a branch for your changes:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make Changes**

   Make your changes to the codebase.

3. **Run Tests**

   Make sure your changes pass all tests:

   .. code-block:: bash

      poetry run pytest

4. **Check Code Quality**

   Ensure your code meets the project's quality standards:

   .. code-block:: bash

      poetry run black .
      poetry run flake8
      poetry run mypy plainspeak

5. **Commit Changes**

   Commit your changes with a descriptive message:

   .. code-block:: bash

      git add .
      git commit -m "Add feature: your feature description"

6. **Push Changes**

   Push your changes to your fork:

   .. code-block:: bash

      git push origin feature/your-feature-name

7. **Create a Pull Request**

   Create a pull request from your fork to the main PlainSpeak repository.

Contribution Guidelines
---------------------

Code Style
~~~~~~~~~

PlainSpeak follows these code style guidelines:

- **Black**: For code formatting
- **Flake8**: For linting
- **MyPy**: For type checking
- **Docstrings**: Google style docstrings

Documentation
~~~~~~~~~~~

All new features should include documentation:

- **User Documentation**: If your feature is user-facing, add documentation to the appropriate user guide
- **Developer Documentation**: If your feature is for developers, add documentation to the developer guide
- **Docstrings**: All public functions, classes, and methods should have docstrings

Testing
~~~~~~

All new features should include tests:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test how components work together
- **End-to-End Tests**: Test the feature from a user's perspective

Pull Request Process
------------------

1. **Create a Pull Request**

   Create a pull request from your fork to the main PlainSpeak repository.

2. **CI Checks**

   The CI system will run tests and code quality checks on your pull request.

3. **Code Review**

   A maintainer will review your pull request and provide feedback.

4. **Address Feedback**

   Address any feedback from the code review.

5. **Merge**

   Once your pull request is approved, a maintainer will merge it.

Types of Contributions
--------------------

There are many ways to contribute to PlainSpeak:

- **Code**: Implement new features or fix bugs
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve tests
- **Bug Reports**: Report bugs or issues
- **Feature Requests**: Suggest new features
- **Plugins**: Create new plugins to extend PlainSpeak's functionality

Community Guidelines
------------------

- **Be Respectful**: Treat all contributors with respect
- **Be Patient**: Not all contributors have the same level of experience
- **Be Constructive**: Provide constructive feedback
- **Be Inclusive**: Welcome contributors of all backgrounds and experience levels

Thank you for contributing to PlainSpeak!

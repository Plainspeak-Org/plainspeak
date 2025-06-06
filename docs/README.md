# PlainSpeak Documentation

This directory contains the documentation for the PlainSpeak project, a century masterpiece open source repository that will be read and taught by generations.

## Documentation Structure

```mermaid
graph TD
    A[Documentation] --> B[User Docs]
    A --> C[Dev Docs]
    A --> D[Sphinx]
    A --> E[Website]
    A --> F[Release]
    A --> G[Store]
    A --> H[Legal]

    B --> B1[Installation]
    B --> B2[Getting Started]
    B --> B3[Guides]
    B --> B4[Plugins]
    B --> B5[FAQ]

    C --> C1[API]
    C --> C2[Architecture]
    C --> C3[Plugins]
    C --> C4[Contributing]
    C --> C5[Roadmap]

    D --> D1[Source]
    D --> D2[Build]

    E --> E1[CSS]
    E --> E2[JS]
    E --> E3[Templates]
    E --> E4[API]
    E --> E5[Contest]
```

The documentation is organized as follows:

- `user_docs/`: Documentation for users of PlainSpeak
  - `installation/`: Installation guides for different platforms
  - `getting_started/`: Guides for getting started with PlainSpeak
  - `guides/`: User guides for various features
  - `plugins/`: Information about available plugins
  - `faq/`: Frequently asked questions

- `dev_docs/`: Documentation for developers
  - `api/`: API reference documentation
  - `architecture/`: Architecture overview and design documents
  - `plugins/`: Plugin development guides
  - `contributing/`: Contribution guidelines
  - `roadmap/`: Development roadmap

- `sphinx/`: Sphinx configuration for building the documentation
  - `source/`: Source files for Sphinx
  - `build/`: Built documentation (generated)

- `website/`: Website-related files
  - `css/`: CSS stylesheets
  - `js/`: JavaScript files
  - `templates/`: HTML templates
  - `api/`: API endpoints for the website
  - `contest/`: Plugin development contest pages

- `release/`: Release-related documentation
  - Distribution strategies
  - Developer accounts
  - Release checklists

- `store/`: Store listings and related documentation

- `legal/`: Legal documents

## Building the Documentation

The documentation is built using [Sphinx](https://www.sphinx-doc.org/), a powerful documentation generator.

```mermaid
graph LR
    A[Source Files] --> B[Sphinx]
    B --> C[HTML]
    B --> D[PDF]
    B --> E[EPUB]

    F[Code Docstrings] --> G[autodoc]
    G --> B

    H[Markdown] --> I[myst-parser]
    I --> B
```

### Prerequisites

- Python 3.11 or higher (required for sphinx-autodoc-typehints)
- Poetry (for dependency management)

### Building Locally

To build the documentation locally:

```bash
# Install dependencies
poetry install
poetry add sphinx sphinx-rtd-theme "sphinx-autodoc-typehints>=3.2.0"

# Build the documentation
cd docs/sphinx
poetry run make html
```

The built documentation will be available in `docs/sphinx/build/html/`.

## Deployment

```mermaid
graph TD
    A[Git Push to main] --> B[GitHub Actions]
    B --> C[Build Docs]
    C --> D[Deploy to GitHub Pages]

    E[Manual Trigger] --> B
```

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The deployment is handled by the GitHub Actions workflow defined in `.github/workflows/deploy-docs.yml`.

### Manual Deployment

To manually trigger a deployment, you can run the GitHub Actions workflow from the Actions tab in the GitHub repository.

## Future Features

### DataSpeak Integration

Future documentation will include information about DataSpeak, a feature that will allow users to:

- Query data using natural language
- Generate SQL queries from plain English
- Visualize data with simple commands
- Perform data analysis without SQL knowledge

DataSpeak will be integrated into PlainSpeak as a core feature, enabling users to interact with their data using the same natural language interface they use for other computing tasks.

## Contributing to Documentation

Contributions to the documentation are welcome! Please see the [Contribution Guidelines](dev_docs/contributing/guide.md) for more information on how to contribute.

When contributing to documentation, please follow these guidelines:

1. Use clear, concise language
2. Include examples where appropriate
3. Follow the existing structure
4. Test any code examples
5. Update the table of contents if necessary

## License

The documentation is licensed under the same license as the PlainSpeak project.

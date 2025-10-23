# Nova - ML Project

This is a Machine Learning project for molecule analysis.

## Description

This project aims to process and analyze molecule data from different sources. It includes scripts for cleaning, structuring, and analyzing the data.

## Installation

This project uses `uv` for Python environment and package management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RenatoJVA/Nova.git
    ```

2.  **Create a virtual environment:**
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Sync the environment:**
    This will install all the dependencies from the `uv.lock` file.
    ```bash
    uv sync
    ```

## Development

If you add or update dependencies in `pyproject.toml`, you need to update the lock file:

```bash
uv lock
```

## Usage

To run the project, execute the main script:

```bash
python main.py
```

## Data

The project uses the following data sources:

*   COCONUT_DB
*   LOTUS_DB
*   TTD_DB

The data is located in the `data/base` directory. The processed data is saved in the `data/pre_processed` directory.
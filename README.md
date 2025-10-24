# Nova Project

Welcome to Nova, a molecule analysis project with an interactive web interface. This repository is structured as a monorepo to manage the project's different services.

## Monorepo Structure

This project uses a monorepo structure with the main packages located in the `packages` directory:

-   `packages/frontend`: A React application (using Vite) that consumes data from the backend and visualizes it.
-   `packages/backend`: An API server built with FastAPI that exposes the processed data.
-   `packages/machine-learning`: A Python project for data processing, analysis, and future machine learning model training.

## Prerequisites

Ensure you have the following tools installed before you begin:

-   **Python** (version `>=3.13`)
-   **[uv](https://github.com/astral-sh/uv)**: For Python package and virtual environment management.
-   **[nvm](https://github.com/coreybutler/nvm-windows)**: To manage Node.js versions.
-   **Node.js**: The required version is specified in the frontend's `.nvmrc` file (currently `v20`).
-   **[Bun](https://bun.sh/)**: Used for frontend package management and script execution.

## Project Setup

Follow these steps to install all project dependencies.

1.  **Install Python Dependencies:**
    From the project's root directory, run:
    ```bash
    # Install all dependencies from pyproject.toml using the lockfile
    uv sync
    ```

2.  **Install Frontend Dependencies:**
    ```bash
    # 1. Navigate to the frontend directory
    cd packages/frontend

    # 2. Install the required Node.js version with nvm
    nvm install

    # 3. Install frontend dependencies with Bun
    bun install

    # 4. Return to the root directory
    cd ../..
    ```

## Running the Application

To run the application, you will need **two separate terminals**, both opened at the **project's root directory**.

#### Terminal 1: Start the Backend

In your first terminal, run the following command to start the FastAPI server:
```bash
uv run uvicorn packages.backend.main:app --reload
```
The backend will be available at `http://127.0.0.1:8000`.

#### Terminal 2: Start the Frontend

In your second terminal, run the following commands to start the React application:
```bash
# 1. Navigate to the frontend directory
cd packages/frontend

# 2. Activate the correct Node.js version
nvm use

# 3. Run the Vite development server with Bun
bun run dev
```
The frontend will be available at `http://localhost:5173` (or the port specified by Vite).

## Running the Machine Learning Pipeline

If you need to run the data processing pipeline separately, you can do so with the following command from the project root:
```bash
uv run python packages/machine-learning/main.py
```
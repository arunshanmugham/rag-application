# README.md

# RAG Application

A comprehensive Retrieval-Augmented Generation (RAG) application designed to provide accurate, contextually relevant, and production-grade responses by integrating external knowledge bases via Google Cloud Vertex AI.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Setup & Installation](#setup--installation)
    - [3.1 Backend Setup](#31-backend-setup)
    - [3.2 Frontend Setup](#32-frontend-setup)
4. [Environment Variables](#environment-variables)
5. [Google Cloud Vertex AI Setup (Critical)](#google-cloud-vertex-ai-setup-critical)
    - [5.1 Vertex AI Configuration](#51-vertex-ai-configuration)
    - [5.2 Loading Stanford Sample Corpus](#52-loading-stanford-sample-corpus)
6. [Running the Application](#running-the-application)
7. [Usage](#usage)
8. [Contributing](#contributing)
9. [License](#license)


---

## Project Overview

This repository contains a full-stack RAG application.
*   **Backend (`backend/`):** A FastAPI service that handles the core logic, vector similarity search, and interaction with the Language Model (LLM), primarily utilizing Google Vertex AI.
*   **Frontend (`frontend/`):** A user interface (e.g., React/Vue) for end-users to input queries and view responses.
*   **Core Logic (`src/`):** Contains underlying source code, data processing utilities, and service definitions.

## Prerequisites

Before starting, ensure you have the following installed:
1.  **Python:** 3.10+
2.  **Node.js & npm:** For the frontend application.
3.  **Google Cloud SDK:** Must be installed and authenticated (`gcloud auth login`).
4.  **Google Cloud Project:** A project with billing enabled and necessary APIs enabled (Vertex AI, Storage).

## Setup & Installation

Follow these steps to get the entire stack running.

### 3.1 Backend Setup

1.  **Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Use .venv\Scripts\activate on Windows
    ```
2.  **Install Dependencies:**
    The backend dependencies are managed in `pyproject.toml`.
    ```bash
    pip install -r requirements.txt
    # OR if using uv:
    uv sync
    ```

### 3.2 Frontend Setup

1.  **Install Dependencies:**
    Navigate to the frontend directory and install its node packages.
    ```bash
    cd frontend
    npm install
    # or yarn install
    ```
2.  **Build (for production):**
    ```bash
    npm run build
    # or yarn build
    ```

## Environment Variables

All sensitive keys and configuration settings *must* be set in a `.env` file placed in the **root directory** of the project.

**Example `.env` Structure:**
```env
# --- GENERAL SETTINGS ---
PORT=8000
DEBUG=True

# --- BACKEND/LLM SETTINGS ---
# Use Vertex AI as the primary LLM provider
LLM_PROVIDER=VERTEX_AI 
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
SERVICE_ACCOUNT_KEY_FILE=/path/to/your/service-account.json

# --- DATABASE SETTINGS ---
# Example: Using ChromaDB locally or Postgres in GCP
DATABASE_URL=chroma://localhost:8000
VECTOR_COLLECTION_NAME=stanford_course_data
```

## Google Cloud Vertex AI Setup (Critical)

To leverage the advanced capabilities of Google Cloud, you must perform these steps.

### 5.1 Vertex AI Configuration

1.  **Enable APIs:** Ensure the Vertex AI API and Cloud Storage API are enabled in your GCP project.
2.  **Service Account:** Create a dedicated service account with the following IAM roles:
    *   `Vertex AI User`
    *   `Storage Object Creator`
3.  **Authentication:** Download the JSON key file and set the path in your `.env` file (`SERVICE_ACCOUNT_KEY_FILE`).
4.  **Authentication Command:** Authenticate your local environment (if not using the key file):
    ```bash
    gcloud auth activate-service-account --key-file=/path/to/key.json
    ```

### 5.2 Loading Stanford Sample Corpus

We will use the official Stanford course materials as our initial knowledge corpus.

1.  **Data Source:** Ensure the raw documents (PDFs, TXT) for the Stanford course are uploaded to a designated Google Cloud Storage bucket (e.g., `gs://your-stanford-corpus-bucket/`).
2.  **Data Ingestion:** Run the dedicated ingestion script (located in `src/data_loader.py` or similar) pointing to the GCS bucket. This process handles document chunking, embedding generation using Vertex AI Embeddings, and storing the vectors in your specified vector store.
    ```bash
    # Example command to trigger ingestion (adjust path as necessary)
    python src/data_loader.py --gcs-uri gs://your-stanford-corpus-bucket/ --collection-name stanford_course_data
    ```

## Running the Application

### Development Mode

1.  **Start Backend:** (Ensure environment variables are loaded first)
    ```bash
    # Activate venv and set env vars in shell, then run
    uvicorn backend.rag_backend:app --reload --host 0.0.0.0 --port 8000
    ```
2.  **Start Frontend:** (In a separate terminal)
    ```bash
    cd frontend
    npm run dev
    ```

### Production Mode

Use a process manager like **Supervisor** or **Docker Compose** to run both services simultaneously.

## Usage

The main endpoint is `/query`. The frontend communicates with the backend via the exposed FastAPI port (`:8000`).

## Contributing

Please refer to the `CONTRIBUTING.md` file (if available) for guidelines.


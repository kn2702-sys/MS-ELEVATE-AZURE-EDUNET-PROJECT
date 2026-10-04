# MS Elevate — Personalized Doubt Solver

An AI-powered Streamlit web application that acts as a personalized doubt
solver, built on OpenRouter and Hugging Face APIs.

## Features

- AI-powered doubt-solving responses
- Interactive Streamlit frontend
- OpenRouter + Hugging Face API integration

## Tech Stack

- **Python**, **Streamlit**
- **OpenRouter API** — LLM responses
- **Hugging Face API** — auxiliary models

## Prerequisites

- Python 3.9+
- API keys for OpenRouter and Hugging Face

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):

```env
OPENROUTER_API_KEY=<your-key>
HUGGINGFACE_API_KEY=<your-key>
```

## Run the Project

```bash
streamlit run app.py
```

## Live Demo

https://ms-elevate-azure-edunet-project-gxpqnxtkvnuamvxfwthecd.streamlit.app/

## Project Structure

```
app.py             # Streamlit application
config.toml        # Streamlit configuration
requirements.txt
.env.example       # environment template (copy to .env)
```

## Author

Kazi Nafis Nawaz

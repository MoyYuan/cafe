# Cafe

A modular forecasting platform integrating LLMs, time-series forecasting, and live news data, strictly following the Model-Context-Protocol (MCP) architecture.

## Features
- Modular, package-centric architecture
- Integrates LLMs (vLLM, Gemini) and time-series models
- Pluggable news/data retrieval (API or local)
- Evaluation and experiment tracking modules
- FastAPI-based API layer
- File-based caching for Metaculus questions and comments (with force-refresh option)
- Extensible and easy to onboard

## Architecture
- **Model**: Forecasting logic (vLLM, Gemini, time-series)
- **Tools**: News retrieval utilities (local and API)
- **Context**: State, data, config, storage abstraction
- **Protocol**: API endpoints, schemas, validation

## Quickstart
1. Create and activate the virtual environment using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set your Gemini API key
4. Run the API server:
   ```bash
   uvicorn main:app --reload
   ```

## Directory Structure
```
cafe/
├── cafe/
│   ├── __init__.py
│   ├── main.py                  # Entrypoint (FastAPI app)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── vllm.py
│   │   │   └── gemini.py
│   │   ├── timeseries/
│   │   │   ├── __init__.py
│   │   │   ├── local.py
│   │   │   └── api.py
│   ├── news/
│   │   ├── __init__.py
│   │   ├── local.py
│   │   └── api.py
│   ├── context/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── memory.py
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── schemas.py
│   ├── utils/
│   │   └── __init__.py
│   ├── forecast/
│   │   ├── forecast_question.py
│   │   ├── source_base.py
│   │   ├── source_metaculus.py
│   │   └── source_local.py
├── tests/
│   └── test_protocol.py
├── scripts/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── .gitignore
├── .roadmap.md
├── .progress.md
├── README.md
├── requirements.txt
```

## Roadmap & Progress
See `.roadmap.md` and `.progress.md`.

## Time-Series Models, News Retrieval, & Forecast Data
- **LLMs**
  - `llm/vllm`: Local vLLM model (stub) — import from `cafe.models.llm.vllm`
  - `llm/gemini`: Gemini API model (stub) — import from `cafe.models.llm.gemini`
- **Time-Series Models**
  - `timeseries/local`: Local forecasting model (stub) — import from `cafe.models.timeseries.local`
  - `timeseries/api`: API-based forecasting model (stub) — import from `cafe.models.timeseries.api`
- **News Retrieval Tools**
  - `news/local`: Local news retriever (stub) — import from `cafe.news.local`
  - `news/api`: API-based news retriever (stub) — import from `cafe.news.api`
- **Forecast Data**
  - `forecast/forecast_question.py`: The `ForecastQuestion` class captures all attributes of a forecast/event question (id, title, description, resolution criteria, dates, status, predictions, tags, etc).
  - `forecast/source_metaculus.py`: Fetches questions from the Metaculus API, with file-based caching for questions and comments. The API allows a `force_refresh` flag to fetch fresh data and update the cache.
  - `forecast/source_local.py`: Loads questions from local files (JSON).

All models are accessible via the `/forecast` endpoint by specifying the `model` field as one of: `llm/vllm`, `llm/gemini`, `timeseries/local`, `timeseries/api`.

**Forecast data** can be loaded from API or local sources, and is always represented as `ForecastQuestion` objects. To add new sources, subclass `ForecastSourceBase` in `forecast/source_base.py`.

_News and forecast data tools are currently utilities and not yet exposed in the API; integrate as needed._

## Testing
`pytest`

## CI/CD
See `.github/workflows/ci.yml`.

---
_This project is under active development._

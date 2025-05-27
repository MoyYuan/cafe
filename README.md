# Cafe

A modular forecasting platform integrating LLMs, time-series forecasting, and live news data, strictly following the Model-Context-Protocol (MCP) architecture.

## Features
- Modular, package-centric architecture
- Integrates LLMs (vLLM, Gemini) and time-series models
- Pluggable news/data retrieval (API or local)
- Evaluation and experiment tracking modules
- FastAPI-based API layer
- File-based caching for Metaculus questions and comments (with force-refresh and robust incremental cache writes for long fetches)
- Extensible and easy to onboard

## Architecture
- **Model**: Forecasting logic (vLLM, Gemini, time-series)
- **Tools**: News retrieval utilities (local and API)
- **Context**: State, data, config, storage abstraction
- **Protocol**: API endpoints, schemas, validation

## Quickstart
1. Create and activate the virtual environment using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies from `pyproject.toml`:
   ```bash
   uv pip install .
   ```
3. Copy `.env.example` to `.env` and set your Gemini API key and Metaculus API key if needed
4. Run the API server:
   ```bash
   uvicorn main:app --reload
   ```

## Metaculus Data Fetching & Caching

Scripts for Metaculus data are organized by domain/task for clarity and maintainability. For example:
- `scripts/metaculus/fetch_metaculus_questions.py`: Fetches and caches questions/comments
- `scripts/metaculus/process_metaculus_timeseries.py`: Processes Metaculus time-series data

All Metaculus scripts are now located in `scripts/metaculus/` for better organization and maintainability.

**Recommendation:** Continue organizing scripts into subfolders (e.g. `scripts/news/`, `scripts/utils/`) by data source or function. Avoid placing all scripts in a single flat folder.

### Metaculus Data Structure
Fetched and processed Metaculus data is saved in a structured directory:

- `data/forecasts/metaculus/`
  - `questions_YYYY-MM-DD.json`: All questions as a single JSON file (timestamped)
  - `comments_YYYY-MM-DD.json`: All comments as a single JSON file (timestamped, all-in-one mode)
  - `questions_cache.json`: Incremental cache for questions (updated after every page)
  - `fetch_checkpoint.json`: Track fetch progress for safe resumption
  - `comments_by_question/`: Directory with one JSON file per question (e.g. `37827.json`)

This structure enables both bulk and per-question access, robust resumption, and efficient incremental updates.

### Key Features
- **Incremental Caching**: The questions cache (`questions_cache.json`) is written after every page of results. If the script is interrupted, progress is saved and fetching will resume from the cache on next run.
- **Checkpointing**: Progress is also tracked in `fetch_checkpoint.json` for safe resumption.
- **Flexible Refresh**: Use `--refresh`, `--refresh-questions`, or `--refresh-comments` to force re-fetching of questions, comments, or both, ignoring the cache as needed.
- **Resume Logic**: Use `--resume`, `--resume-questions`, or `--resume-comments` to resume from the last checkpoint for questions or comments.
- **No-Cache Mode**: Use `--no-cache` to disable reading/writing cache files entirely (not recommended for large fetches).

### Usage Example
```bash
PYTHONPATH=. .venv/bin/python scripts/metaculus/fetch_metaculus_questions.py \
  --after 2023-10-01 \
  --output-dir data/forecasts/metaculus \
  --comments-mode all-in-one
```

- On first run, all questions will be fetched from Metaculus, and the cache will be written after every page.
- If interrupted, simply re-run the command: fetching will resume using the cache, saving time and bandwidth.
- To force a full refresh, add `--refresh` or `--refresh-questions`/`--refresh-comments` as needed.

### Best Practices
- **First run may take a long time** if you are fetching thousands of questions. Let the script complete, or safely interrupt and resume later.
- **Cache files** are always written unless you use `--no-cache`.
- **Always check the cache and checkpoint files** in your `output-dir` to monitor progress or debug issues.


## Directory Structure
```
cafe/
├── cafe/
│   ├── models/
│   │   ├── llm/
│   │   ├── timeseries/
│   ├── news/
│   ├── context/
│   ├── protocols/
│   ├── utils/
│   ├── forecast/
├── tests/
├── scripts/
│   ├── metaculus/
│   ├── news/         # (suggested for future organization)
│   ├── utils/        # (suggested for future organization)
├── data/
│   ├── forecasts/
│   │   ├── metaculus/
├── .github/
│   └── workflows/
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

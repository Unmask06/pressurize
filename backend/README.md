# Pressurize Backend

Gas blowdown simulation API for pressure vessel depressurization analysis.

## Installation

```bash
# Install dependencies
uv sync
```

## Usage

### As a CLI command

```bash
pressurize
```

### As a Python module

```bash
uv run python -m pressurize
```

### Using uvicorn directly

```bash
# Using python -m to avoid execution policy issues
uv run python -m uvicorn pressurize.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

When running standalone with `PRESSURIZE_STANDALONE=true`, all endpoints are prefixed with `/pressurize`.

- `GET /` - Health check
- `POST /simulate/stream` - Stream simulation results (SSE) and KPIs
- `GET /units/config` - Get available unit systems and dimension mappings
- `GET /components` - List available composition components
- `GET /presets` - List preset compositions
- `GET /presets/{preset_id}` - Fetch a preset composition map
- `POST /properties` - Calculate Z, k, and M from composition and conditions

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=pressurize
```

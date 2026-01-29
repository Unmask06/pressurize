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
python -m pressurize.main
```

### Using uvicorn directly

```bash
uv run uvicorn pressurize.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

When running standalone with `PRESSURIZE_STANDALONE=true`, all endpoints are prefixed with `/pressurize`.

- `GET /` - Health check
- `POST /simulate` - Run simulation and return full results
- `POST /simulate/stream` - Stream simulation results (SSE) and KPIs
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

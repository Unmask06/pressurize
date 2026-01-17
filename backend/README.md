# Pressurize Backend

Gas blowdown simulation API for pressure vessel depressurization analysis.

## Installation

```bash
# Install from source
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Usage

### As a CLI command

```bash
pressurize
```

### As a Python module

```bash
python -m backend.main
```

### Using uvicorn directly

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check
- `POST /api/simulate/stream` - Run blowdown simulation with streaming results

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=backend
```

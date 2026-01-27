# Copilot Instructions for Pressurize

Generic instructions for AI coding agents working on the Pressurize project.

## Project Overview

Pressurize is a gas blowdown and valve pressurization simulator. It calculates gas flow from an upstream source into a downstream vessel through a dynamic valve.

- **Backend**: FastAPI (Python 3.12+), SciPy, NumPy, Thermo.
- **Frontend**: Vue 3 (Vite), ECharts for visualization, Tailwind CSS for styling.

## Architecture & Data Flow

- **Simulation Engine**: Located in [backend/pressurize/core/](backend/pressurize/core/).
  - [physics.py](backend/pressurize/core/physics.py) contains pure physics formulas (SI units).
  - [simulation.py](backend/pressurize/core/simulation.py) handles the time-stepping loop and state management.
- **API**: Defined in [backend/pressurize/api/routes.py](backend/pressurize/api/routes.py).
  - Supports both standard JSON responses and SSE (Server-Sent Events) for real-time streaming of simulation rows.
- **Frontend-Backend Bridge**: [frontend/src/api/client.ts](frontend/src/api/client.ts) handles axios requests and SSE parsing.

## Key Conventions

### Unit Consistency

- **Internal Backend**: Use SI units (Pascal, Kelvin, kg/s, meters, m³).
- **External API/UI**: Use Imperial units (psig, °F, lb/hr, inches, ft³).
- **Converters**: Always use utilities in [backend/pressurize/utils/converters.py](backend/pressurize/utils/converters.py) for transformations.

### Backend Patterns

- **Pydantic Models**: All API request/response schemas should be in [backend/pressurize/api/schemas.py](backend/pressurize/api/schemas.py).
- **Error Handling**: Use standard `HTTPException` in routes. Physics errors should be caught and raised as meaningful simulation errors.
- **Tests**: Use `pytest`. Test files are in [backend/tests/](backend/tests/).

### Frontend Patterns

- **Vue 3 SFC**: Use `<script setup>` with TypeScript where possible.
- **State Management**: Local state in components (e.g., [SimulationForm.vue](frontend/src/components/SimulationForm.vue)) or emitted events.
- **Styling**: Mixture of Tailwind utility classes and scoped CSS. Global styles in [frontend/src/styles/common.css](frontend/src/styles/common.css).

## Developer Workflow

### Environment Setup

- **Backend**: Uses `uv`. Run `uv sync` to install dependencies. no pip.
- **Frontend**: Uses `npm`. Run `npm install` in the [frontend/](frontend/) directory.

### Running the App

- **Full Stack**: Run `./launch.ps1` from the root to start both servers and open the browser.
- **Backend Only**: `uv run uvicorn pressurize.main:app --reload` (from `backend/`).
- **Frontend Only**: `npm run dev` (from `frontend/`).

### Testing

- **Backend**: `pytest` from the `backend/` directory.
- **Coverage**: `pytest --cov=pressurize`.

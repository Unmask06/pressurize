# Dynamic Valve Pressurization Simulator

A modern web application for simulating gas flow through a valve into a vessel. Built with **Vue 3** (Frontend) and **FastAPI** (Backend).

## Features

- **Real Gas Law Calculations**: Uses PV = ZnRT for accurate pressure calculations
- **Dual Flow Regimes**: Automatically handles both choked (sonic) and subsonic flow conditions
- **Multiple Valve Opening Modes**: Linear, exponential, fixed, and quick-opening profiles
- **Composition-Based Properties**: Define gas mixtures with 20+ components (Natural Gas, H2, CO2, etc.)
- **Interactive Dashboard**: Premium Vue 3 UI with dark mode components
- **Multi-Axis Visualization**: ECharts visualization of Pressure, Flow Rate, and Valve Opening

## Architecture

- **Frontend**: Vue 3, Vite, ECharts (in `frontend/`)
- **Backend**: FastAPI, SciPy, Thermo (in `backend/`)

## Installation

### Backend
1. Install Python dependencies:
   ```bash
   uv sync
   # OR
   pip install -r requirements.txt
   ```

### Frontend
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```

## Usage

1. **Start the Backend API**:
   ```bash
   # From root directory
   uv run uvicorn backend.main:app --reload
   ```
   API will run at `http://localhost:8000`.

2. **Start the Frontend Development Server**:
   ```bash
   # From frontend/ directory
   npm run dev
   ```
   UI will be available at `http://localhost:5173`.

## Legacy Version
The original Dash application has been moved to the `legacy_dash/` directory.

## License
MIT License

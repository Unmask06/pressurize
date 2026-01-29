# Pressurize - Dynamic Valve Pressurization Simulator

An open-source engineering application for simulating gas flow dynamics through valves into pressure vessels. This tool enables engineers to analyze and predict pressure vessel filling behavior, flow rates, and valve performance under various operating conditions.

## 🎯 Domain & Application

**Pressurize** is designed for process engineers, mechanical engineers, and safety analysts working with pressurized gas systems. The simulator models the transient behavior of gas flowing from a high-pressure source through a control valve into a downstream vessel.

### Key Applications:

- **Pressure Vessel Filling Analysis**: Calculate filling times and pressure profiles for gas storage vessels
- **Valve Sizing & Selection**: Evaluate valve performance under different opening modes and discharge coefficients
- **Flow Regime Analysis**: Understand the transition between sonic (choked) and subsonic flow conditions
- **Safety Studies**: Assess pressure rise rates and peak flow conditions for process safety analysis
- **Gas Composition Effects**: Analyze how different gas mixtures affect pressurization dynamics

### Technical Approach:

The simulator uses rigorous thermodynamic calculations based on:

- **Real Gas Law (PV = ZnRT)**: Accounts for gas non-ideality using compressibility factors
- **ISO 5167-2 Flow Standards**: Industry-standard orifice flow calculations
- **Dual Flow Regimes**: Automatic handling of choked (sonic) and subsonic flow based on pressure ratios
- **Dynamic Compressibility**: Real-time Z-factor calculations for composition-defined gas mixtures

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Modern Python web framework for high-performance APIs
- **Thermo** - Thermodynamic and chemical property calculations
- **SciPy** - Scientific computing and numerical integration
- **Fluids** - Fluid dynamics calculations (custom fork)
- **NumPy & Pandas** - Numerical computing and data manipulation
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment

### Frontend

- **Vue 3** - Progressive JavaScript framework with Composition API
- **Vite** - Next-generation frontend build tool
- **ECharts** - Professional data visualization library
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **jsPDF** - Client-side PDF generation for reports

### Development Tools

- **Python 3.12+** - Backend runtime
- **Node.js** - Frontend build tools
- **uv** - Fast Python package installer and resolver
- **pytest** - Testing framework with coverage support

## ✨ Features

- **Real Gas Law Calculations**: Uses PV = ZnRT for accurate pressure calculations
- **Dual Flow Regimes**: Automatically handles both choked (sonic) and subsonic flow conditions
- **Multiple Valve Opening Modes**: Linear, exponential, fixed, and quick-opening profiles
- **Composition-Based Properties**: Define gas mixtures with 20+ components (Natural Gas, H₂, CO₂, etc.)
- **Interactive Dashboard**: Modern Vue 3 UI with dark mode components
- **Multi-Axis Visualization**: ECharts visualization of Pressure, Flow Rate, and Valve Opening
- **Real-time Simulation**: Stream simulation results as they are calculated
- **Export Capabilities**: Generate PDF reports of simulation results

## Installation

### Backend

1. Install Python dependencies:
   ```bash
   uv sync
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

### Quick Start (Recommended)

For a streamlined setup, use the provided PowerShell script to launch both servers simultaneously:

1. **Run the Launch Script**:
   ```powershell
   # From root directory (Windows PowerShell)
   .\launch.ps1
   ```
   This will automatically start the backend API at `http://localhost:8000` and the frontend at `http://localhost:5173`, then open your browser to the application.

### Manual Setup

If you prefer to start services individually:

1. **Start the Backend API**:

   ```bash
   # From root directory
   uv run uvicorn pressurize.main:app --reload
   ```

   API will run at `http://localhost:8000`.

2. **Start the Frontend Development Server**:
   ```bash
   # From frontend/ directory
   npm run dev
   ```
   UI will be available at `http://localhost:5173`.

## 📚 Documentation

### End-User Documentation

The full user guide is available in the application. To view it locally during development:

```bash
cd frontend
npm run docs:dev
```

Access it at: `http://localhost:5173/products/pressurize/docs/`

### API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! This is an open-source project, and we appreciate your help in making it better.

### How to Contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works (`pytest` for backend)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines:

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

This means you are free to:

- ✅ Use this software for commercial purposes
- ✅ Modify and distribute the software
- ✅ Use this software privately
- ✅ Sublicense the software

## 🙏 Acknowledgments

- Built with open-source tools and libraries from the Python and Vue.js ecosystems
- Thermodynamic calculations powered by the [Thermo](https://github.com/CalebBell/thermo) library
- Flow calculations based on ISO 5167-2 standards

## 📧 Contact & Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/Unmask06/pressurize/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/Unmask06/pressurize/discussions)
- **Author**: [@Unmask06](https://github.com/Unmask06)

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

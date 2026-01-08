# Testing Documentation

This document describes the test suite for the Pressurize application.

## Overview

The test suite provides comprehensive coverage of the core physics and simulation functionality with 99 tests achieving 95% code coverage.

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── test_converters.py      # Unit conversion tests (25 tests)
├── test_physics.py          # Physics calculations tests (24 tests)
├── test_properties.py       # Gas property tests (23 tests)
└── test_simulation.py       # Simulation engine tests (27 tests)
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_physics.py -v
```

### Run specific test class
```bash
pytest tests/test_physics.py::TestCriticalPressureRatio -v
```

## Test Coverage

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| `src/utils/converters.py` | 100% | None |
| `src/core/properties.py` | 97% | 88-89 |
| `src/core/physics.py` | 96% | 114 |
| `src/core/simulation.py` | 92% | 162, 164-174 |
| **Overall** | **95%** | |

## Test Categories

### 1. Unit Conversion Tests (test_converters.py)

**25 tests covering:**
- Temperature conversions (Fahrenheit ↔ Kelvin)
- Pressure conversions (psig ↔ Pa)
- Round-trip conversions
- Edge cases (absolute zero, vacuum, high pressures)
- Consistency and monotonicity

**Key test classes:**
- `TestTemperatureConversion`
- `TestPressureConversionPsigToPa`
- `TestPressureConversionPaToPsig`
- `TestRoundTripConversions`
- `TestEdgeCases`
- `TestConsistency`

### 2. Physics Calculations Tests (test_physics.py)

**24 tests covering:**
- Critical pressure ratio calculations
- Choked (sonic) flow calculations
- Subsonic flow calculations
- Mass flow rate with automatic regime detection
- Pressure change rate calculations
- Integration tests with realistic scenarios

**Key test classes:**
- `TestCriticalPressureRatio`
- `TestChokedFlow`
- `TestSubsonicFlow`
- `TestMassFlowRate`
- `TestPressureChangeRate`
- `TestIntegration`

### 3. Gas Properties Tests (test_properties.py)

**23 tests covering:**
- Composition string parsing
- Gas state initialization
- Thermodynamic property calculations
- Default component handling
- Consistency checks
- Error handling

**Key test classes:**
- `TestGasStateInitialization`
- `TestGasProperties`
- `TestDefaultComponents`
- `TestConvenienceFunction`
- `TestPropertyConsistency`
- `TestErrorHandling`

### 4. Simulation Engine Tests (test_simulation.py)

**27 tests covering:**
- Basic simulation execution
- Multiple valve opening modes (linear, exponential, fixed, quick-opening)
- Pressure behavior (monotonicity, equilibrium, bounds)
- Flow rate behavior (peaks, equilibrium)
- Flow regime detection
- Parameter sensitivity
- Composition mode
- Edge cases
- Unit consistency

**Key test classes:**
- `TestSimulationBasics`
- `TestValveOpeningModes`
- `TestPressureBehavior`
- `TestFlowRateBehavior`
- `TestFlowRegimeDetection`
- `TestParameterSensitivity`
- `TestCompositionMode`
- `TestEdgeCases`
- `TestUnitConsistency`

## Test Design Principles

### 1. Comprehensive Coverage
- Each function has multiple test cases
- Both typical and edge cases are tested
- Integration tests verify components work together

### 2. Physics Validation
- Tests verify correct physical behavior
- Conservation laws are validated
- Regime transitions are checked

### 3. Numerical Accuracy
- Tests use appropriate tolerances (`pytest.approx`)
- Relative and absolute error bounds are specified
- Rounding effects are considered

### 4. Robustness
- Edge cases are explicitly tested
- Boundary conditions are validated
- Error handling is verified

### 5. Maintainability
- Tests are organized by functionality
- Descriptive test names
- Helper functions reduce duplication
- Clear assertions with meaningful messages

## Example Test Output

```
tests/test_converters.py .........................       [ 25%]
tests/test_physics.py ........................           [ 49%]
tests/test_properties.py .......................         [ 72%]
tests/test_simulation.py ...........................     [100%]

================================ tests coverage ================================
Name                      Stmts   Miss  Cover
---------------------------------------------
src/core/physics.py          28      1    96%
src/core/properties.py       62      2    97%
src/core/simulation.py       87      7    92%
src/utils/converters.py       9      0   100%
---------------------------------------------
TOTAL                       186     10    95%

============================== 99 passed in 5.17s ==============================
```

## Adding New Tests

When adding new functionality, ensure:

1. **Unit tests** for individual functions
2. **Integration tests** for component interactions
3. **Edge case tests** for boundary conditions
4. **Validation tests** for physical correctness
5. **Coverage** remains above 90%

### Test Template

```python
class TestNewFeature:
    """Tests for new feature description."""
    
    def test_basic_functionality(self):
        """Test basic behavior."""
        # Arrange
        input_data = ...
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case behavior."""
        # Test edge cases
        pass
```

## Continuous Integration

These tests should be run:
- Before every commit
- In CI/CD pipeline
- Before releasing new versions
- After dependency updates

## Dependencies

Test dependencies are specified in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

Install with:
```bash
pip install -e ".[dev]"
```

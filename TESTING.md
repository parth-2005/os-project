# Testing Guide

This document provides comprehensive testing information for the distributed processing system.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_master.py          # Master service unit tests
├── test_slave.py           # Slave service unit tests  
├── test_integration.py     # Integration tests
├── test_performance.py     # Performance and load tests
├── generate_test_data.py   # Test data generation script
└── test_data/              # Sample test files
    ├── sample_text.txt
    ├── sample_image.png
    ├── sample_audio.wav
    ├── embedding_text_*.txt
    ├── positive_sentiment.txt
    └── negative_sentiment.txt
```

## Running Tests

### Quick Setup
```powershell
# Install test dependencies
python -m pip install pytest pytest-cov

# Generate test data
python tests/generate_test_data.py

# Run all tests
python run_tests.py

# Run only quick tests
python run_tests.py --quick

# Check dependencies
python run_tests.py --check-deps
```

### Test Categories

#### Unit Tests
```powershell
# Master service tests
python -m pytest tests/test_master.py -v

# Slave service tests  
python -m pytest tests/test_slave.py -v
```

#### Integration Tests
```powershell
# Master-slave communication
python -m pytest tests/test_integration.py -v
```

#### Performance Tests
```powershell
# Load and stress tests (slow)
python -m pytest tests/test_performance.py -v -m slow
```

#### Coverage Report
```powershell
# Generate coverage report
python -m pytest tests/ --cov=master_service --cov=slave_service --cov-report=html --cov-report=term
```

## Test Descriptions

### Master Service Tests (`test_master.py`)

- **Route Testing**
  - Home endpoint health check
  - Slave registration with valid/invalid data
  - Task assignment with various scenarios
  - Error handling for missing files/slaves

- **Worker Function Testing**
  - Slave health checking and cleanup
  - Task distribution among multiple slaves
  - File processing and result aggregation
  - Different processing types (image, text, etc.)

### Slave Service Tests (`test_slave.py`)

- **Route Testing**
  - Health check endpoints
  - Multi-type task processing
  - File upload handling
  - Error responses for invalid requests

- **Processing Module Testing**
  - **Image Processing**: Grayscale conversion, format handling
  - **Text Analysis**: Sentiment analysis, word counting, statistics
  - **Embedding Generation**: TF-IDF vectorization, feature extraction
  - **OCR Processing**: Text extraction, confidence scoring
  - **Audio Processing**: WAV analysis, feature extraction
  - **Document Processing**: PDF/DOCX parsing, metadata extraction

### Integration Tests (`test_integration.py`)

- **Master-Slave Communication**
  - End-to-end workflow testing
  - Slave registration and task assignment
  - Multi-type processing pipelines
  - Error handling and recovery

- **Client Integration**
  - File upload workflows
  - Multiple task type handling
  - Response validation

- **System Reliability**
  - Concurrent request handling
  - Slave failure scenarios
  - Malformed request handling

### Performance Tests (`test_performance.py`)

- **Throughput Testing**
  - Single slave performance
  - Multi-slave scalability
  - Request latency distribution

- **Load Testing**
  - Concurrent task processing
  - Memory usage stability
  - System limits and stress scenarios

- **Stress Testing**
  - Large file processing
  - High file count handling
  - Failure recovery performance

## Test Fixtures and Utilities

### Available Fixtures (`conftest.py`)

- `temp_dir`: Temporary directory for test outputs
- `sample_text_file`: Generated text file with known content
- `sample_image_file`: Test image file (PNG format)
- `sample_audio_data`: Generated WAV audio file
- `mock_file_storage`: Mock Werkzeug FileStorage objects
- `sample_processing_results`: Expected results for each processing type

### Mock Data Generation

The test suite includes comprehensive mock data generators:

- **Image Files**: RGB test images with shapes and text
- **Audio Files**: Generated sine wave audio in WAV format
- **Text Files**: Sentiment-labeled text for analysis testing
- **Document Content**: Sample PDF/DOCX content for parsing tests

## Running Specific Test Categories

### By Test Type
```powershell
# Unit tests only
python -m pytest -m unit

# Integration tests only  
python -m pytest -m integration

# Slow tests (performance)
python -m pytest -m slow
```

### By Processing Type
```powershell
# Image processing tests
python -m pytest tests/test_slave.py::TestImageProcessing -v

# Text processing tests
python -m pytest tests/test_slave.py::TestTextProcessing -v

# All processing modules
python -m pytest tests/test_slave.py -k "Processing" -v
```

### By Component
```powershell
# Master service only
python -m pytest tests/test_master.py -v

# Slave service only
python -m pytest tests/test_slave.py -v

# Integration only
python -m pytest tests/test_integration.py -v
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - run: pip install -r requirements.txt
    - run: pip install pytest pytest-cov
    - run: python tests/generate_test_data.py
    - run: python run_tests.py --quick
```

## Test Coverage Goals

- **Unit Tests**: >90% line coverage
- **Integration Tests**: All major workflows covered
- **Error Handling**: All error paths tested
- **Performance**: Baseline performance benchmarks established

## Adding New Tests

### For New Processing Types
1. Add processing module tests in `test_slave.py`
2. Add integration tests in `test_integration.py`  
3. Update fixtures in `conftest.py`
4. Add test data generation in `generate_test_data.py`

### For New Features
1. Write unit tests first (TDD approach)
2. Add integration tests for end-to-end workflows
3. Include performance tests if applicable
4. Update documentation

## Debugging Failed Tests

### Common Issues
- **Import Errors**: Check if all dependencies are installed
- **File Permissions**: Ensure test directories are writable
- **Mock Failures**: Verify mock data matches expected formats
- **Timing Issues**: Use appropriate timeouts for async operations

### Debug Commands
```powershell
# Verbose output with full tracebacks
python -m pytest tests/test_name.py -v -s --tb=long

# Stop on first failure
python -m pytest tests/ -x

# Run specific test method
python -m pytest tests/test_slave.py::TestClass::test_method -v
```

## Performance Benchmarks

Expected performance baselines (on typical development machine):

- **Single File Processing**: <100ms average latency
- **10 Concurrent Requests**: >80% success rate
- **100 Small Files**: <30 seconds total processing
- **Memory Growth**: <50% increase under load

## Contributing Test Improvements

When contributing new tests:

1. Follow existing test patterns and naming conventions
2. Include both positive and negative test cases
3. Use appropriate fixtures and mocks
4. Add performance tests for new features
5. Update this documentation for significant changes

## Troubleshooting

### Common Test Failures

**ImportError for processing modules**
```powershell
# Install missing dependencies
python -m pip install scikit-learn pytesseract PyPDF2 python-docx
```

**Test data not found**
```powershell
# Regenerate test data
python tests/generate_test_data.py
```

**Mock failures in integration tests**  
```powershell
# Check that mock patches match actual function signatures
# Update mocks when refactoring code
```
"""Pytest configuration and shared fixtures for the test suite."""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock
from PIL import Image
import io
import json

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    content = """This is a sample text document for testing.
    It contains multiple sentences with different sentiments.
    Some words are positive like great, excellent, and wonderful.
    Other words might be negative like bad, terrible, or awful.
    This text has exactly fifty-seven words for testing purposes.
    """
    
    text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    text_file.write(content)
    text_file.close()
    
    yield text_file.name
    os.unlink(text_file.name)

@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    # Create a simple 100x100 RGB image
    img = Image.new('RGB', (100, 100), color='red')
    
    image_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(image_file.name, 'PNG')
    
    yield image_file.name
    os.unlink(image_file.name)

@pytest.fixture
def sample_audio_data():
    """Create sample WAV audio data for testing."""
    import wave
    import numpy as np
    
    # Generate a simple sine wave
    sample_rate = 44100
    duration = 1  # 1 second
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file
    audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    with wave.open(audio_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    yield audio_file.name
    os.unlink(audio_file.name)

@pytest.fixture
def mock_file_storage():
    """Create a mock Werkzeug FileStorage object."""
    def _create_mock_file(filename, content, content_type='text/plain'):
        mock_file = Mock()
        mock_file.filename = filename
        mock_file.mimetype = content_type
        
        if isinstance(content, str):
            mock_file.stream = io.StringIO(content)
        else:
            mock_file.stream = io.BytesIO(content)
        
        return mock_file
    
    return _create_mock_file

@pytest.fixture
def sample_processing_results():
    """Sample processing results for different task types."""
    return {
        'image': {
            'filename': 'test.png',
            'image_data': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        },
        'text': {
            'filename': 'test.txt',
            'analysis_data': 'eyJ3b3JkX2NvdW50IjogMTAsICJzZW50aW1lbnRfc2NvcmUiOiAyfQ=='
        },
        'embedding': {
            'filename': 'test.txt',
            'embedding_data': 'eyJ2ZWN0b3IiOiBbMC4xLCAwLjIsIDAuM10sICJ2ZWN0b3Jfc2l6ZSI6IDN9'
        },
        'ocr': {
            'filename': 'test.png',
            'ocr_data': 'eyJleHRyYWN0ZWRfdGV4dCI6ICJTYW1wbGUgdGV4dCIsICJjb25maWRlbmNlIjogOTV9'
        },
        'audio': {
            'filename': 'test.wav',
            'audio_data': 'eyJkdXJhdGlvbl9zZWNvbmRzIjogMS4wLCAic2FtcGxlX3JhdGUiOiA0NDEwMH0='
        },
        'document': {
            'filename': 'test.pdf',
            'document_data': 'eyJkb2N1bWVudF90eXBlIjogIlBERiIsICJwYWdlX2NvdW50IjogMX0='
        }
    }
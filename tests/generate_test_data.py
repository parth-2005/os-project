"""Generate test data files for the test suite."""
import os
from pathlib import Path
from PIL import Image
import wave
import numpy as np

def create_sample_image():
    """Create a sample test image."""
    # Create a simple test image
    img = Image.new('RGB', (200, 100), color=(255, 0, 0))  # Red image
    
    # Add some simple content
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes
    draw.rectangle([20, 20, 80, 60], fill=(0, 255, 0))  # Green rectangle
    draw.ellipse([120, 30, 180, 70], fill=(0, 0, 255))   # Blue circle
    
    # Try to add text (might not work without proper font)
    try:
        draw.text((10, 80), "TEST IMAGE", fill=(255, 255, 255))
    except:
        pass  # Font might not be available
    
    return img

def create_sample_audio():
    """Create a sample WAV audio file."""
    # Audio parameters
    sample_rate = 44100
    duration = 2  # 2 seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Add some variation (amplitude envelope)
    envelope = np.exp(-t / 2)  # Exponential decay
    audio_data = audio_data * envelope
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    return audio_data, sample_rate

def create_sample_pdf_content():
    """Create sample PDF content (as text for mock)."""
    return """Sample PDF Document

This is a test PDF document for the distributed processing system.
It contains multiple pages and various types of content.

Chapter 1: Introduction
This chapter introduces the concept of distributed processing.
The system can handle multiple file types including PDFs.

Chapter 2: Implementation
The implementation uses Flask and HTTP for communication.
Multiple slaves can process files concurrently.

Chapter 3: Testing
This PDF is used for testing the document processing module.
It should extract text and metadata correctly.

End of Document"""

def generate_test_data():
    """Generate all test data files."""
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    print("Generating test data files...")
    
    # Create sample image
    print("Creating sample image...")
    img = create_sample_image()
    img.save(test_data_dir / "sample_image.png", "PNG")
    
    # Create sample audio
    print("Creating sample audio...")
    audio_data, sample_rate = create_sample_audio()
    
    with wave.open(str(test_data_dir / "sample_audio.wav"), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    # Create sample documents
    print("Creating sample documents...")
    
    # Sample text for embedding testing
    embedding_texts = [
        "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
        "Natural language processing helps computers understand human language effectively.",
        "Computer vision enables machines to interpret and understand visual information from images.",
        "Deep learning uses neural networks with multiple layers to solve complex problems."
    ]
    
    for i, text in enumerate(embedding_texts):
        with open(test_data_dir / f"embedding_text_{i+1}.txt", 'w') as f:
            f.write(text)
    
    # Sample PDF content (as text file for testing)
    with open(test_data_dir / "sample_document.txt", 'w') as f:
        f.write(create_sample_pdf_content())
    
    # Create negative sentiment text
    negative_text = """
    This is a terrible document with awful content.
    Everything about this is bad and horrible.
    I hate this terrible, disgusting text.
    The worst possible example of bad writing.
    """
    
    with open(test_data_dir / "negative_sentiment.txt", 'w') as f:
        f.write(negative_text.strip())
    
    # Create positive sentiment text  
    positive_text = """
    This is an excellent document with wonderful content.
    Everything about this is great and amazing.
    I love this fantastic, beautiful text.
    The best possible example of good writing.
    """
    
    with open(test_data_dir / "positive_sentiment.txt", 'w') as f:
        f.write(positive_text.strip())
    
    print("✅ Test data generation complete!")
    print(f"Files created in: {test_data_dir}")
    
    # List generated files
    for file_path in test_data_dir.glob("*"):
        print(f"  - {file_path.name}")

if __name__ == "__main__":
    generate_test_data()
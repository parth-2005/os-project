"""Tests for slave service functionality."""
import pytest
import json
import io
import base64
from unittest.mock import Mock, patch, MagicMock
from slave_service.app import create_app
from slave_service.processing import process_images
from slave_service.text_processing import process_text
from slave_service.embedding_processing import process_embeddings

@pytest.fixture
def app():
    """Create a test Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

class TestSlaveRoutes:
    """Test slave service routes."""
    
    def test_home_route(self, client):
        """Test the home route returns correct message."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"Slave is working" in response.data
    
    def test_check_status(self, client):
        """Test the check_status endpoint."""
        response = client.get('/check_status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'alive'
    
    def test_get_task_image_processing(self, client, sample_image_file):
        """Test image processing task."""
        with open(sample_image_file, 'rb') as f:
            data = {
                'task_type': 'image',
                'images': (f, 'test.png')
            }
            response = client.post('/get_task', data=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'results' in result
        assert len(result['results']) == 1
        assert result['results'][0]['filename'] == 'test.png'
        assert 'image_data' in result['results'][0]
    
    def test_get_task_text_processing(self, client, sample_text_file):
        """Test text processing task."""
        with open(sample_text_file, 'rb') as f:
            data = {
                'task_type': 'text',
                'texts': (f, 'test.txt')
            }
            response = client.post('/get_task', data=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'results' in result
        assert len(result['results']) == 1
        assert result['results'][0]['filename'] == 'test.txt'
        assert 'analysis_data' in result['results'][0]
    
    def test_get_task_no_files(self, client):
        """Test task processing with no files."""
        data = {'task_type': 'image'}
        response = client.post('/get_task', data=data)
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result

class TestImageProcessing:
    """Test image processing module."""
    
    def test_process_images_success(self, mock_file_storage):
        """Test successful image processing."""
        # Create a mock image file
        from PIL import Image
        img = Image.new('RGB', (10, 10), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        mock_file = mock_file_storage('test.png', img_buffer.getvalue(), 'image/png')
        mock_file.stream = img_buffer
        
        results = process_images([mock_file])
        
        assert len(results) == 1
        assert results[0]['filename'] == 'test.png'
        assert 'image_data' in results[0]
        
        # Verify the result is valid base64
        image_data = results[0]['image_data']
        decoded = base64.b64decode(image_data)
        assert len(decoded) > 0
    
    def test_process_images_invalid_format(self, mock_file_storage):
        """Test image processing with invalid image format."""
        mock_file = mock_file_storage('test.txt', b'not an image', 'text/plain')
        
        results = process_images([mock_file])
        
        # Should handle errors gracefully
        assert isinstance(results, list)

class TestTextProcessing:
    """Test text processing module."""
    
    def test_process_text_success(self, mock_file_storage):
        """Test successful text processing."""
        text_content = "This is a great day! I love this wonderful weather. It's amazing and fantastic."
        mock_file = mock_file_storage('test.txt', text_content.encode(), 'text/plain')
        
        results = process_text([mock_file])
        
        assert len(results) == 1
        assert results[0]['filename'] == 'test.txt'
        assert 'analysis_data' in results[0]
        
        # Decode and verify the analysis
        analysis_data = base64.b64decode(results[0]['analysis_data']).decode()
        analysis = json.loads(analysis_data)
        
        assert 'word_count' in analysis
        assert 'sentiment_score' in analysis
        assert 'character_count' in analysis
        assert analysis['word_count'] > 0
        assert analysis['sentiment_score'] > 0  # Should be positive due to positive words
    
    def test_process_text_negative_sentiment(self, mock_file_storage):
        """Test text processing with negative sentiment."""
        text_content = "This is terrible and awful. I hate this bad weather."
        mock_file = mock_file_storage('negative.txt', text_content.encode(), 'text/plain')
        
        results = process_text([mock_file])
        
        analysis_data = base64.b64decode(results[0]['analysis_data']).decode()
        analysis = json.loads(analysis_data)
        
        assert analysis['sentiment_score'] < 0  # Should be negative

class TestEmbeddingProcessing:
    """Test embedding processing module."""
    
    def test_process_embeddings_success(self, mock_file_storage):
        """Test successful embedding generation."""
        texts = [
            "This is the first document about technology.",
            "This document is about sports and games."
        ]
        
        mock_files = []
        for i, text in enumerate(texts):
            mock_file = mock_file_storage(f'doc{i}.txt', text.encode(), 'text/plain')
            mock_files.append(mock_file)
        
        with patch('sklearn.feature_extraction.text.TfidfVectorizer') as mock_vectorizer:
            # Mock the vectorizer
            mock_vectorizer_instance = Mock()
            mock_vectorizer_instance.fit_transform.return_value.toarray.return_value = [
                [0.5, 0.3, 0.2],
                [0.2, 0.4, 0.4]
            ]
            mock_vectorizer_instance.get_feature_names_out.return_value = ['word1', 'word2', 'word3']
            mock_vectorizer.return_value = mock_vectorizer_instance
            
            results = process_embeddings(mock_files)
        
        assert len(results) == 2
        for i, result in enumerate(results):
            assert result['filename'] == f'doc{i}.txt'
            assert 'embedding_data' in result
            
            # Decode and verify embedding
            embedding_data = base64.b64decode(result['embedding_data']).decode()
            embedding = json.loads(embedding_data)
            
            assert 'vector' in embedding
            assert 'features' in embedding
            assert 'vector_size' in embedding
            assert len(embedding['vector']) == 3

class TestOCRProcessing:
    """Test OCR processing module."""
    
    @patch('pytesseract.image_to_string')
    @patch('pytesseract.image_to_data')
    def test_process_ocr_success(self, mock_image_to_data, mock_image_to_string, mock_file_storage):
        """Test successful OCR processing."""
        from slave_service.ocr_processing import process_ocr
        
        # Mock OCR results
        mock_image_to_string.return_value = "Sample extracted text"
        mock_image_to_data.return_value = {
            'conf': ['95', '90', '85']
        }
        
        # Create mock image file
        from PIL import Image
        img = Image.new('RGB', (100, 50), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        mock_file = mock_file_storage('document.png', img_buffer.getvalue(), 'image/png')
        mock_file.stream = img_buffer
        
        results = process_ocr([mock_file])
        
        assert len(results) == 1
        assert results[0]['filename'] == 'document.png'
        assert 'ocr_data' in results[0]
        
        # Decode and verify OCR result
        ocr_data = base64.b64decode(results[0]['ocr_data']).decode()
        ocr_result = json.loads(ocr_data)
        
        assert ocr_result['extracted_text'] == "Sample extracted text"
        assert 'average_confidence' in ocr_result

class TestAudioProcessing:
    """Test audio processing module."""
    
    def test_process_audio_wav_success(self, mock_file_storage, sample_audio_data):
        """Test successful WAV audio processing."""
        from slave_service.audio_processing import process_audio
        
        with open(sample_audio_data, 'rb') as f:
            audio_content = f.read()
        
        mock_file = mock_file_storage('test.wav', audio_content, 'audio/wav')
        
        results = process_audio([mock_file])
        
        assert len(results) == 1
        assert results[0]['filename'] == 'test.wav'
        assert 'audio_data' in results[0]
        
        # Decode and verify audio analysis
        audio_data = base64.b64decode(results[0]['audio_data']).decode()
        audio_result = json.loads(audio_data)
        
        assert 'duration_seconds' in audio_result
        assert 'sample_rate' in audio_result
        assert audio_result['sample_rate'] == 44100

class TestDocumentProcessing:
    """Test document processing module."""
    
    @patch('PyPDF2.PdfReader')
    def test_process_pdf_success(self, mock_pdf_reader, mock_file_storage):
        """Test successful PDF processing."""
        from slave_service.document_processing import process_documents
        
        # Mock PDF reader
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF content"
        mock_reader.pages = [mock_page]
        mock_reader.metadata = {'/Title': 'Test Document'}
        mock_pdf_reader.return_value = mock_reader
        
        mock_file = mock_file_storage('document.pdf', b'fake pdf content', 'application/pdf')
        
        results = process_documents([mock_file])
        
        assert len(results) == 1
        assert results[0]['filename'] == 'document.pdf'
        assert 'document_data' in results[0]
        
        # Decode and verify document analysis
        doc_data = base64.b64decode(results[0]['document_data']).decode()
        doc_result = json.loads(doc_data)
        
        assert doc_result['document_type'] == 'PDF'
        assert doc_result['page_count'] == 1
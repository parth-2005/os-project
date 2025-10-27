"""Tests for master service functionality."""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from master_service.app import create_app
from master_service.worker import slaves, check_slaves, assign_task_to_slaves

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

class TestMasterRoutes:
    """Test master service routes."""
    
    def test_home_route(self, client):
        """Test the home route returns correct message."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"Master is working" in response.data
    
    def test_register_slave_success(self, client):
        """Test successful slave registration."""
        # Clear any existing slaves
        slaves.clear()
        
        slave_data = {
            "slave_ip": "127.0.0.1",
            "slave_port": 3001
        }
        
        response = client.post('/register', 
                             data=json.dumps(slave_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert ('127.0.0.1', 3001) in slaves
    
    def test_register_slave_missing_data(self, client):
        """Test slave registration with missing data."""
        slave_data = {"slave_ip": "127.0.0.1"}  # Missing slave_port
        
        response = client.post('/register',
                             data=json.dumps(slave_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_assign_task_no_slaves(self, client):
        """Test task assignment when no slaves available."""
        slaves.clear()
        
        # Create a fake file
        data = {
            'task_type': 'image',
            'images': (io.BytesIO(b'fake image data'), 'test.png')
        }
        
        response = client.post('/assign_task', data=data)
        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'No slaves available' in data['error']
    
    def test_assign_task_no_files(self, client):
        """Test task assignment with no files provided."""
        # Register a mock slave
        slaves.add(('127.0.0.1', 3001))
        
        response = client.post('/assign_task', data={'task_type': 'image'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No files provided' in data['error']
    
    def test_assign_task_unknown_type(self, client):
        """Test task assignment with unknown task type."""
        slaves.add(('127.0.0.1', 3001))
        
        data = {
            'task_type': 'unknown_type',
            'files': (io.BytesIO(b'fake data'), 'test.file')
        }
        
        response = client.post('/assign_task', data=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Unknown task type' in data['error']

class TestWorkerFunctions:
    """Test worker utility functions."""
    
    def test_check_slaves_removes_unresponsive(self):
        """Test that unresponsive slaves are removed."""
        slaves.clear()
        slaves.add(('127.0.0.1', 9999))  # Fake unresponsive slave
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            check_slaves()
        
        assert len(slaves) == 0
    
    def test_check_slaves_keeps_responsive(self):
        """Test that responsive slaves are kept."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            check_slaves()
        
        assert ('127.0.0.1', 3001) in slaves
    
    @patch('master_service.worker.send_work_to_slave')
    @patch('os.makedirs')
    def test_assign_task_to_slaves_image(self, mock_makedirs, mock_send_work):
        """Test task assignment for image processing."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock slave response
        mock_send_work.return_value = [
            {
                'filename': 'test.png',
                'image_data': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
            }
        ]
        
        # Create mock files
        mock_files = [Mock()]
        mock_files[0].filename = 'test.png'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.open', create=True) as mock_open:
                result = assign_task_to_slaves(mock_files, temp_dir, 'image')
        
        assert result['task_type'] == 'image'
        assert result['total_files_processed'] == 1
        assert 'Image processing complete' in result['message']
    
    @patch('master_service.worker.send_work_to_slave')
    def test_assign_task_to_slaves_text(self, mock_send_work):
        """Test task assignment for text processing."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock slave response
        mock_send_work.return_value = [
            {
                'filename': 'test.txt',
                'analysis_data': 'eyJ3b3JkX2NvdW50IjogMTB9'  # base64 encoded '{"word_count": 10}'
            }
        ]
        
        # Create mock files
        mock_files = [Mock()]
        mock_files[0].filename = 'test.txt'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('builtins.open', create=True) as mock_open:
                result = assign_task_to_slaves(mock_files, temp_dir, 'text')
        
        assert result['task_type'] == 'text'
        assert result['total_files_processed'] == 1

import io
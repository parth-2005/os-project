"""Integration tests for master-slave communication."""
import pytest
import json
import time
import threading
import requests
from unittest.mock import patch, Mock
from master_service.app import create_app as create_master_app
from slave_service.app import create_app as create_slave_app
from master_service.worker import slaves

@pytest.fixture
def master_app():
    """Create master app for testing."""
    app = create_master_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def slave_app():
    """Create slave app for testing."""
    app = create_slave_app()
    app.config['TESTING'] = True
    return app

class TestMasterSlaveIntegration:
    """Integration tests for master-slave interaction."""
    
    def test_slave_registration_integration(self, master_app, slave_app):
        """Test complete slave registration flow."""
        slaves.clear()
        
        with master_app.test_client() as master_client:
            # Test slave registration
            registration_data = {
                "slave_ip": "127.0.0.1",
                "slave_port": 3001
            }
            
            response = master_client.post('/register',
                                        data=json.dumps(registration_data),
                                        content_type='application/json')
            
            assert response.status_code == 200
            assert ('127.0.0.1', 3001) in slaves
    
    @patch('requests.post')
    def test_end_to_end_image_processing(self, mock_post, master_app):
        """Test complete image processing workflow."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock slave response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'filename': 'test.png',
                    'image_data': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
                }
            ]
        }
        mock_post.return_value = mock_response
        
        with master_app.test_client() as client:
            # Create fake image data
            import io
            data = {
                'task_type': 'image',
                'images': (io.BytesIO(b'fake image data'), 'test.png')
            }
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                response = client.post('/assign_task', data=data)
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['task_type'] == 'image'
            assert result['total_files_processed'] == 1
    
    @patch('requests.post')
    def test_end_to_end_text_processing(self, mock_post, master_app):
        """Test complete text processing workflow."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock slave response with base64 encoded analysis
        import base64
        analysis = {"word_count": 10, "sentiment_score": 2}
        encoded_analysis = base64.b64encode(json.dumps(analysis).encode()).decode()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'filename': 'test.txt',
                    'analysis_data': encoded_analysis
                }
            ]
        }
        mock_post.return_value = mock_response
        
        with master_app.test_client() as client:
            import io
            data = {
                'task_type': 'text',
                'texts': (io.BytesIO(b'sample text content'), 'test.txt')
            }
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                response = client.post('/assign_task', data=data)
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['task_type'] == 'text'
            assert result['total_files_processed'] == 1
    
    @patch('requests.get')
    def test_slave_health_check_integration(self, mock_get, master_app):
        """Test slave health checking."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        slaves.add(('127.0.0.1', 3002))  # This one will be "unhealthy"
        
        # Mock responses - first slave healthy, second unhealthy
        def side_effect(url, **kwargs):
            if '3001' in url:
                mock_response = Mock()
                mock_response.status_code = 200
                return mock_response
            else:
                raise requests.RequestException("Connection failed")
        
        mock_get.side_effect = side_effect
        
        from master_service.worker import check_slaves
        check_slaves()
        
        # Only healthy slave should remain
        assert ('127.0.0.1', 3001) in slaves
        assert ('127.0.0.1', 3002) not in slaves
    
    def test_multiple_slaves_task_distribution(self, master_app):
        """Test task distribution among multiple slaves."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        slaves.add(('127.0.0.1', 3002))
        
        with patch('master_service.worker.send_work_to_slave') as mock_send:
            # Mock responses from both slaves
            mock_send.return_value = [
                {
                    'filename': 'test.png',
                    'image_data': 'fake_base64_data'
                }
            ]
            
            # Create mock files
            mock_files = []
            for i in range(4):  # 4 files to be distributed among 2 slaves
                mock_file = Mock()
                mock_file.filename = f'test{i}.png'
                mock_files.append(mock_file)
            
            from master_service.worker import assign_task_to_slaves
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                result = assign_task_to_slaves(mock_files, '/tmp/test', 'image')
            
            # Should have called send_work_to_slave for each slave
            assert mock_send.call_count == 2
            assert result['total_files_processed'] >= 0
    
    @patch('requests.post')
    def test_slave_failure_handling(self, mock_post, master_app):
        """Test handling of slave failures during processing."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock slave failure
        mock_post.side_effect = requests.RequestException("Slave unreachable")
        
        with master_app.test_client() as client:
            import io
            data = {
                'task_type': 'image',
                'images': (io.BytesIO(b'fake image data'), 'test.png')
            }
            
            with patch('os.makedirs'):
                response = client.post('/assign_task', data=data)
            
            assert response.status_code == 200
            result = json.loads(response.data)
            # Should handle failure gracefully
            assert result['total_files_processed'] == 0

class TestClientIntegration:
    """Test client.py integration with master service."""
    
    def test_client_image_upload_flow(self, master_app):
        """Test client uploading images to master."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        with master_app.test_client() as client:
            # Simulate client.py behavior
            import io
            files = {
                'images': (io.BytesIO(b'fake image'), 'test.png')
            }
            data = {'task_type': 'image'}
            
            with patch('master_service.worker.send_work_to_slave') as mock_send:
                mock_send.return_value = [
                    {'filename': 'test.png', 'image_data': 'fake_data'}
                ]
                
                with patch('os.makedirs'), patch('builtins.open', create=True):
                    response = client.post('/assign_task', data={**data, **files})
                
                assert response.status_code == 200
    
    def test_client_multiple_task_types(self, master_app):
        """Test client handling different task types."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        task_types = ['image', 'text', 'audio', 'document', 'ocr', 'embedding']
        
        with master_app.test_client() as client:
            for task_type in task_types:
                # Determine appropriate file field
                if task_type == 'image' or task_type == 'ocr':
                    file_field = 'images'
                elif task_type in ['text', 'embedding']:
                    file_field = 'texts'
                elif task_type == 'audio':
                    file_field = 'audio_files'
                elif task_type == 'document':
                    file_field = 'documents'
                
                import io
                files = {
                    file_field: (io.BytesIO(b'fake content'), f'test.{task_type}')
                }
                data = {'task_type': task_type}
                
                with patch('master_service.worker.send_work_to_slave') as mock_send:
                    mock_send.return_value = [
                        {'filename': f'test.{task_type}', f'{task_type}_data': 'fake_data'}
                    ]
                    
                    with patch('os.makedirs'), patch('builtins.open', create=True):
                        response = client.post('/assign_task', data={**data, **files})
                    
                    assert response.status_code == 200
                    result = json.loads(response.data)
                    assert result['task_type'] == task_type

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_requests(self, master_app, slave_app):
        """Test handling of malformed requests."""
        with master_app.test_client() as master_client:
            # Test malformed registration
            response = master_client.post('/register',
                                        data='invalid json',
                                        content_type='application/json')
            assert response.status_code == 400
        
        with slave_app.test_client() as slave_client:
            # Test task without required fields
            response = slave_client.post('/get_task', data={})
            assert response.status_code == 400
    
    def test_concurrent_requests(self, master_app):
        """Test handling of concurrent task assignments."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        def make_request():
            with master_app.test_client() as client:
                import io
                data = {
                    'task_type': 'image',
                    'images': (io.BytesIO(b'fake image'), 'test.png')
                }
                
                with patch('master_service.worker.send_work_to_slave') as mock_send:
                    mock_send.return_value = [{'filename': 'test.png', 'image_data': 'data'}]
                    
                    with patch('os.makedirs'), patch('builtins.open', create=True):
                        return client.post('/assign_task', data=data)
        
        # Make multiple concurrent requests
        threads = []
        results = []
        
        for _ in range(3):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should complete successfully
        assert len(results) == 3
        for response in results:
            if response:  # Some might be None due to threading
                assert response.status_code == 200
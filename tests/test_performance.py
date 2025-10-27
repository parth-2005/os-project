"""Performance and load tests for the distributed processing system."""
import pytest
import time
import threading
import statistics
from unittest.mock import Mock, patch
from master_service.app import create_app as create_master_app
from master_service.worker import slaves, assign_task_to_slaves

@pytest.fixture
def master_app():
    """Create master app for performance testing."""
    app = create_master_app()
    app.config['TESTING'] = True
    return app

class TestPerformance:
    """Performance tests for the system."""
    
    @pytest.mark.slow
    def test_single_slave_throughput(self, master_app):
        """Test throughput with single slave."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Mock fast processing
        with patch('master_service.worker.send_work_to_slave') as mock_send:
            mock_send.return_value = [
                {'filename': 'test.png', 'image_data': 'fake_data'}
            ]
            
            # Create mock files
            num_files = 100
            mock_files = []
            for i in range(num_files):
                mock_file = Mock()
                mock_file.filename = f'test{i}.png'
                mock_files.append(mock_file)
            
            start_time = time.time()
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                result = assign_task_to_slaves(mock_files, '/tmp/test', 'image')
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should process reasonably quickly
            assert duration < 5.0  # Should complete in under 5 seconds
            assert result['total_files_processed'] == num_files
            
            throughput = num_files / duration
            print(f"Single slave throughput: {throughput:.2f} files/second")
    
    @pytest.mark.slow
    def test_multiple_slaves_scalability(self, master_app):
        """Test scalability with multiple slaves."""
        test_cases = [1, 2, 4, 8]  # Different numbers of slaves
        results = {}
        
        for num_slaves in test_cases:
            slaves.clear()
            for i in range(num_slaves):
                slaves.add(('127.0.0.1', 3001 + i))
            
            with patch('master_service.worker.send_work_to_slave') as mock_send:
                mock_send.return_value = [
                    {'filename': 'test.png', 'image_data': 'fake_data'}
                ]
                
                # Create mock files
                num_files = 50
                mock_files = []
                for i in range(num_files):
                    mock_file = Mock()
                    mock_file.filename = f'test{i}.png'
                    mock_files.append(mock_file)
                
                start_time = time.time()
                
                with patch('os.makedirs'), patch('builtins.open', create=True):
                    result = assign_task_to_slaves(mock_files, '/tmp/test', 'image')
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[num_slaves] = duration
                print(f"{num_slaves} slaves: {duration:.3f}s")
        
        # More slaves should generally be faster (or at least not much slower)
        # allowing some variance due to overhead
        assert results[1] >= results[2] * 0.8  # 2 slaves should be competitive with 1
    
    def test_request_latency_distribution(self, master_app):
        """Test latency distribution of requests."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        latencies = []
        
        with master_app.test_client() as client:
            for i in range(20):
                import io
                data = {
                    'task_type': 'image',
                    'images': (io.BytesIO(b'fake image'), f'test{i}.png')
                }
                
                with patch('master_service.worker.send_work_to_slave') as mock_send:
                    mock_send.return_value = [
                        {'filename': f'test{i}.png', 'image_data': 'fake_data'}
                    ]
                    
                    start_time = time.time()
                    
                    with patch('os.makedirs'), patch('builtins.open', create=True):
                        response = client.post('/assign_task', data=data)
                    
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  # Convert to ms
                    latencies.append(latency)
                    
                    assert response.status_code == 200
        
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"95th percentile latency: {p95_latency:.2f}ms")
        
        # Reasonable performance expectations
        assert avg_latency < 100  # Average under 100ms
        assert p95_latency < 200   # 95th percentile under 200ms

class TestLoadTesting:
    """Load testing for high concurrency scenarios."""
    
    @pytest.mark.slow
    def test_concurrent_task_assignments(self, master_app):
        """Test handling of concurrent task assignments."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        slaves.add(('127.0.0.1', 3002))
        
        num_concurrent = 10
        results = []
        errors = []
        
        def make_request(request_id):
            try:
                with master_app.test_client() as client:
                    import io
                    data = {
                        'task_type': 'image',
                        'images': (io.BytesIO(b'fake image'), f'test{request_id}.png')
                    }
                    
                    with patch('master_service.worker.send_work_to_slave') as mock_send:
                        mock_send.return_value = [
                            {'filename': f'test{request_id}.png', 'image_data': 'fake_data'}
                        ]
                        
                        start_time = time.time()
                        
                        with patch('os.makedirs'), patch('builtins.open', create=True):
                            response = client.post('/assign_task', data=data)
                        
                        end_time = time.time()
                        
                        results.append({
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'duration': end_time - start_time
                        })
            except Exception as e:
                errors.append({'request_id': request_id, 'error': str(e)})
        
        # Launch concurrent requests
        threads = []
        for i in range(num_concurrent):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify results
        successful_requests = [r for r in results if r['status_code'] == 200]
        
        print(f"Concurrent requests: {num_concurrent}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Errors: {len(errors)}")
        print(f"Total time: {total_time:.3f}s")
        
        # Should handle most requests successfully
        assert len(successful_requests) >= num_concurrent * 0.8  # At least 80% success
        assert len(errors) <= num_concurrent * 0.2  # No more than 20% errors
    
    @pytest.mark.slow
    def test_memory_usage_stability(self, master_app):
        """Test memory usage doesn't grow excessively under load."""
        import gc
        import sys
        
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Run many requests
        with master_app.test_client() as client:
            for i in range(50):
                import io
                data = {
                    'task_type': 'text',
                    'texts': (io.BytesIO(b'sample text content'), f'test{i}.txt')
                }
                
                with patch('master_service.worker.send_work_to_slave') as mock_send:
                    mock_send.return_value = [
                        {'filename': f'test{i}.txt', 'analysis_data': 'fake_data'}
                    ]
                    
                    with patch('os.makedirs'), patch('builtins.open', create=True):
                        response = client.post('/assign_task', data=data)
                    
                    assert response.status_code == 200
        
        # Check memory usage after
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_growth = final_objects - initial_objects
        growth_ratio = object_growth / initial_objects if initial_objects > 0 else 0
        
        print(f"Initial objects: {initial_objects}")
        print(f"Final objects: {final_objects}")
        print(f"Growth ratio: {growth_ratio:.2%}")
        
        # Memory should not grow excessively
        assert growth_ratio < 0.5  # Less than 50% growth in objects

class TestStressTests:
    """Stress tests for system limits."""
    
    @pytest.mark.slow
    def test_large_file_processing(self, master_app):
        """Test processing of large files."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        
        # Simulate large file (1MB)
        large_content = b'x' * (1024 * 1024)
        
        with master_app.test_client() as client:
            import io
            data = {
                'task_type': 'image',
                'images': (io.BytesIO(large_content), 'large_image.png')
            }
            
            with patch('master_service.worker.send_work_to_slave') as mock_send:
                mock_send.return_value = [
                    {'filename': 'large_image.png', 'image_data': 'large_fake_data'}
                ]
                
                start_time = time.time()
                
                with patch('os.makedirs'), patch('builtins.open', create=True):
                    response = client.post('/assign_task', data=data)
                
                duration = time.time() - start_time
                
                assert response.status_code == 200
                print(f"Large file processing time: {duration:.3f}s")
                
                # Should complete within reasonable time
                assert duration < 10.0
    
    @pytest.mark.slow
    def test_many_small_files(self, master_app):
        """Test processing many small files."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        slaves.add(('127.0.0.1', 3002))
        
        num_files = 200
        
        with patch('master_service.worker.send_work_to_slave') as mock_send:
            mock_send.return_value = [
                {'filename': 'test.png', 'image_data': 'small_data'}
            ]
            
            # Create many small mock files
            mock_files = []
            for i in range(num_files):
                mock_file = Mock()
                mock_file.filename = f'small{i}.png'
                mock_files.append(mock_file)
            
            start_time = time.time()
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                result = assign_task_to_slaves(mock_files, '/tmp/test', 'image')
            
            duration = time.time() - start_time
            
            print(f"Processing {num_files} files took {duration:.3f}s")
            print(f"Throughput: {num_files/duration:.1f} files/second")
            
            # Should handle many files efficiently
            assert result['total_files_processed'] == num_files
            assert duration < 30.0  # Should complete within 30 seconds
    
    def test_slave_failure_recovery(self, master_app):
        """Test system recovery when slaves fail during processing."""
        slaves.clear()
        slaves.add(('127.0.0.1', 3001))
        slaves.add(('127.0.0.1', 3002))  # This slave will "fail"
        
        def failing_send_work(slave, files, task_type):
            if slave[1] == 3002:  # Second slave fails
                raise Exception("Slave connection failed")
            else:
                return [{'filename': 'test.png', 'image_data': 'data'}]
        
        with patch('master_service.worker.send_work_to_slave', side_effect=failing_send_work):
            mock_files = [Mock()]
            mock_files[0].filename = 'test.png'
            
            with patch('os.makedirs'), patch('builtins.open', create=True):
                result = assign_task_to_slaves(mock_files, '/tmp/test', 'image')
            
            # Should handle partial failure gracefully
            # At least some files should be processed by the working slave
            assert isinstance(result, dict)
            assert 'total_files_processed' in result
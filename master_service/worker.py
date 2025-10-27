import os
import base64
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

# Keep slave registry and helper methods here
slaves = set()

def check_slaves():
    """Ping registered slaves and remove unresponsive ones."""
    for slave in list(slaves):
        slave_ip, slave_port = slave
        try:
            response = requests.get(f"http://{slave_ip}:{slave_port}/check_status", timeout=2)
            if response.status_code != 200:
                print(f"Slave {slave_ip}:{slave_port} is unresponsive, removing from list")
                slaves.remove(slave)
        except requests.RequestException:
            print(f"Slave {slave_ip}:{slave_port} is unresponsive, removing from list")
            slaves.remove(slave)

def send_work_to_slave(slave, assigned_files, task_type):
    slave_ip, slave_port = slave
    
    # Prepare files based on task type
    if task_type == 'image':
        files = [('images', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    elif task_type in ['text', 'embedding']:
        files = [('texts', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    elif task_type == 'ocr':
        files = [('images', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    elif task_type == 'audio':
        files = [('audio_files', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    elif task_type == 'document':
        files = [('documents', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    else:
        files = [('files', (f.filename, f.stream, f.mimetype)) for f in assigned_files]
    
    try:
        print(f"Sending {len(assigned_files)} {task_type} files to slave {slave_ip}:{slave_port}")
        resp = requests.post(
            f"http://{slave_ip}:{slave_port}/get_task",
            files=files,
            data={'task_type': task_type},
            timeout=45
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
        else:
            print(f"Slave {slave_ip}:{slave_port} returned status {resp.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Failed to contact slave {slave_ip}:{slave_port}: {e}")
        return None

def assign_task_to_slaves(files, output_dir, task_type='image'):
    slave_list = list(slaves)
    num_slaves = len(slave_list)
    num_files = len(files)

    tasks = []
    start = 0
    for i in range(num_slaves):
        end = start + num_files // num_slaves + (1 if i < num_files % num_slaves else 0)
        if start < end:
            tasks.append((slave_list[i], files[start:end]))
        start = end

    final_results = []
    with ThreadPoolExecutor(max_workers=max(1, num_slaves)) as executor:
        future_to_task = {executor.submit(send_work_to_slave, task[0], task[1], task_type): task for task in tasks}
        for future in as_completed(future_to_task):
            slave_results = future.result()
            task_info = future_to_task[future]

            if slave_results is not None:
                for result in slave_results:
                    try:
                        filename = result.get("filename")
                        
                        # Handle different result data types
                        if task_type == 'image':
                            data_key = "image_data"
                            file_ext = ".png"
                        elif task_type == 'text':
                            data_key = "analysis_data"
                            file_ext = "_analysis.json"
                        elif task_type == 'embedding':
                            data_key = "embedding_data"
                            file_ext = "_embedding.json"
                        elif task_type == 'ocr':
                            data_key = "ocr_data"
                            file_ext = "_ocr.json"
                        elif task_type == 'audio':
                            data_key = "audio_data"
                            file_ext = "_audio_analysis.json"
                        elif task_type == 'document':
                            data_key = "document_data"
                            file_ext = "_document_analysis.json"
                        else:
                            data_key = "data"
                            file_ext = "_result.json"
                        
                        result_data = result.get(data_key)
                        if result_data:
                            if task_type == 'image':
                                # For images, decode base64 to binary
                                file_data = base64.b64decode(result_data)
                                save_path = os.path.join(output_dir, f"processed_{filename}")
                            else:
                                # For other types, decode base64 to JSON text
                                file_data = base64.b64decode(result_data).decode('utf-8')
                                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                                save_path = os.path.join(output_dir, f"{base_name}{file_ext}")
                            
                            with open(save_path, "wb" if task_type == 'image' else "w") as f:
                                if task_type == 'image':
                                    f.write(file_data)
                                else:
                                    f.write(file_data)
                            final_results.append(save_path)
                    except (TypeError, ValueError) as e:
                        print(f"Error decoding or saving result for '{filename}': {e}")
            else:
                print(f"Task failed for slave: {task_info[0]}.")

    return {
        "message": f"{task_type.title()} processing complete",
        "total_files_processed": len(final_results),
        "saved_files": final_results,
        "task_type": task_type
    }

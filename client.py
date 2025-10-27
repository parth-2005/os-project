"""Multi-type client to POST files to the master `/assign_task` endpoint."""
import requests
from pathlib import Path

def send_files(master_url, task_type, file_paths):
    """Send files to master for processing based on task type."""
    files = []
    
    # Determine the form field name based on task type
    if task_type == 'image':
        field_name = 'images'
    elif task_type in ['text', 'embedding']:
        field_name = 'texts'
    elif task_type == 'ocr':
        field_name = 'images'
    elif task_type == 'audio':
        field_name = 'audio_files'
    elif task_type == 'document':
        field_name = 'documents'
    else:
        print(f"Unknown task type: {task_type}")
        return
    
    for p in file_paths:
        p = Path(p)
        if not p.exists():
            print(f"File not found: {p}")
            continue
        files.append((field_name, (p.name, open(p, "rb"), "application/octet-stream")))

    if not files:
        print("No valid files to send")
        return

    # Send request with task_type
    data = {'task_type': task_type}
    resp = requests.post(f"{master_url.rstrip('/')}/assign_task", files=files, data=data)
    
    try:
        result = resp.json()
        print(f"Task Type: {result.get('task_type', task_type)}")
        print(f"Message: {result.get('message', 'Processing complete')}")
        print(f"Files Processed: {result.get('total_files_processed', 0)}")
        if result.get('saved_files'):
            print("Saved Files:")
            for file_path in result['saved_files']:
                print(f"  - {file_path}")
    except Exception:
        print("Response:", resp.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python client.py <master_url> <task_type> <file1> [file2 ...]")
        print("Task types: image, text, embedding, ocr, audio, document")
        print("Examples:")
        print("  python client.py http://localhost:5000 image photo1.jpg photo2.png")
        print("  python client.py http://localhost:5000 text document.txt essay.txt")
        print("  python client.py http://localhost:5000 ocr scanned_doc.png")
        print("  python client.py http://localhost:5000 audio song.wav speech.wav")
        print("  python client.py http://localhost:5000 document report.pdf presentation.docx")
    else:
        master = sys.argv[1]
        task_type = sys.argv[2]
        files = sys.argv[3:]
        send_files(master, task_type, files)

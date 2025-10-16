from flask import jsonify, request
import os
import socket
import requests
from .processing import process_images
from .text_processing import process_text
from .embedding_processing import process_embeddings
from .ocr_processing import process_ocr
from .audio_processing import process_audio
from .document_processing import process_documents

def register_routes(app):
    @app.post("/get_task")
    def get_task():
        # Determine task type from request
        task_type = request.form.get('task_type', 'image')
        
        if task_type == 'image':
            if 'images' not in request.files:
                return jsonify({"error": "No images provided"}), 400
            files = request.files.getlist('images')
            print(f"Received {len(files)} images for processing")
            results = process_images(files)
            
        elif task_type == 'text':
            if 'texts' not in request.files:
                return jsonify({"error": "No text files provided"}), 400
            files = request.files.getlist('texts')
            print(f"Received {len(files)} text files for processing")
            results = process_text(files)
            
        elif task_type == 'embedding':
            if 'texts' not in request.files:
                return jsonify({"error": "No text files provided for embedding"}), 400
            files = request.files.getlist('texts')
            print(f"Received {len(files)} text files for embedding generation")
            results = process_embeddings(files)
            
        elif task_type == 'ocr':
            if 'images' not in request.files:
                return jsonify({"error": "No images provided for OCR"}), 400
            files = request.files.getlist('images')
            print(f"Received {len(files)} images for OCR processing")
            results = process_ocr(files)
            
        elif task_type == 'audio':
            if 'audio_files' not in request.files:
                return jsonify({"error": "No audio files provided"}), 400
            files = request.files.getlist('audio_files')
            print(f"Received {len(files)} audio files for processing")
            results = process_audio(files)
            
        elif task_type == 'document':
            if 'documents' not in request.files:
                return jsonify({"error": "No documents provided"}), 400
            files = request.files.getlist('documents')
            print(f"Received {len(files)} documents for processing")
            results = process_documents(files)
            
        else:
            return jsonify({"error": f"Unknown task type: {task_type}"}), 400

        return jsonify({"results": results})

    @app.get("/check_status")
    def check_status():
        return jsonify({"status": "alive"})

    @app.get("/")
    def home():
        return "Slave is working"

def register_slave(env=os.environ):
    master_url = env.get("MASTER_URL", "http://localhost:5000")
    slave_ip = env.get("SLAVE_IP", socket.gethostbyname(socket.gethostname()))
    slave_port = env.get("SLAVE_PORT", 3000)
    print(f"Attempting to register with master at {master_url} as {slave_ip}:{slave_port}")
    try:
        response = requests.post(master_url+"/register", json={"slave_ip": slave_ip, "slave_port": slave_port}, timeout=5)
        if response.status_code == 200:
            print("Slave registered successfully")
            return True
        else:
            print(f"Failed to register slave. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Error during registration: Could not connect to master. {e}")
        return False
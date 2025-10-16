from flask import jsonify, request
import os
from .worker import assign_task_to_slaves, slaves, check_slaves

def register_routes(app):
    @app.get("/")
    def home():
        return "Master is working"

    @app.post("/register")
    def register():
        data = request.get_json()
        slave_ip = data.get("slave_ip")
        slave_port = data.get("slave_port")

        if not slave_ip or not slave_port:
            return jsonify({"error": "slave_ip and slave_port are required"}), 400

        slave_address = (slave_ip, slave_port)
        slaves.add(slave_address)
        print(f"Slave registered: {slave_ip}:{slave_port}")
        print(f"Current slaves: {slaves}")
        return jsonify({"status": "success"})

    @app.post("/assign_task")
    def assign_task():
        # Ensure slaves are alive before assigning
        check_slaves()
        if not slaves:
            return jsonify({"error": "No slaves available"}), 503

        # Determine task type
        task_type = request.form.get('task_type', 'image')
        
        # Get files based on task type
        files = None
        if task_type == 'image':
            files = request.files.getlist('images')
        elif task_type == 'text':
            files = request.files.getlist('texts')
        elif task_type == 'embedding':
            files = request.files.getlist('texts')
        elif task_type == 'ocr':
            files = request.files.getlist('images')
        elif task_type == 'audio':
            files = request.files.getlist('audio_files')
        elif task_type == 'document':
            files = request.files.getlist('documents')
        else:
            return jsonify({"error": f"Unknown task type: {task_type}"}), 400

        if not files:
            return jsonify({"error": f"No files provided for {task_type} processing"}), 400

        output_dir = f"processed_results/{task_type}"
        os.makedirs(output_dir, exist_ok=True)

        result = assign_task_to_slaves(files, output_dir, task_type)

        return jsonify(result)

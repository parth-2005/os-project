from slave_service.app import create_app
from slave_service.routes import register_slave
import os

app = create_app()

if __name__ == "__main__":
    if register_slave(os.environ):
        app.run(host="0.0.0.0", port=int(os.getenv("SLAVE_PORT", 3000)), debug=True)
    else:
        print("Could not register with master. Shutting down.")
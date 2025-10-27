from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register routes here to avoid circular imports
    from . import routes
    routes.register_routes(app)

    return app

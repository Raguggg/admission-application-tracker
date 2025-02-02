from .serializers import auth_bp, auth_ns


# Register Blueprint in Flask app
def register_auth_blueprint(app, api):
    api.add_namespace(auth_ns)
    app.register_blueprint(auth_bp)

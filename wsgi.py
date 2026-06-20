from app import create_app

# Create the Flask application instance for WSGI servers (gunicorn)
app = create_app()

if __name__ == "__main__":
    app.run()

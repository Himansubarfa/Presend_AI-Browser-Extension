from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    # For development only. In production, use gunicorn/ waitress.
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    print("Starting production server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
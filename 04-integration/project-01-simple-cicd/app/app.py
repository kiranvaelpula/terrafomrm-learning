from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Simple CI/CD!',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'status': 'running',
        'project': 'project-01-simple-cicd'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/info')
def info():
    return jsonify({
        'application': 'Simple CI/CD Demo',
        'technologies': ['Git', 'Docker', 'Jenkins', 'Flask'],
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Home'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/api/info', 'method': 'GET', 'description': 'Application info'}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

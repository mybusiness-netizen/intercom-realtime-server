from flask import Flask, request
from flask_socketio import SocketIO, emit
import base64
import time
from datetime import datetime
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected clients
clients = {}

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎧 INTERCOM REAL-TIME SERVER</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎧 INTERCOM REAL-TIME SERVER</h1>
            <p><strong>Status:</strong> ONLINE ✅</p>
            <p><strong>Connected Clients:</strong> <span id="clientCount">0</span></p>
            <p><strong>WebSocket Ready</strong> for real-time audio</p>
        </div>
        <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
        <script>
            // Real-time client count update
            const socket = io();
            socket.on('client_count_update', (data) => {
                document.getElementById('clientCount').textContent = data.count;
            });
        </script>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return {
        'status': 'online',
        'clients': len(clients),
        'timestamp': datetime.now().isoformat(),
        'server': 'Render.com WebSocket'
    }

@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    clients[client_id] = {
        'connected_at': datetime.now(),
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    print(f"✅ Client connected: {client_id}")
    emit('connection_ack', {'message': 'Connected to server', 'client_id': client_id})
    
    # Broadcast to all clients
    emit('client_count_update', {'count': len(clients)}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in clients:
        del clients[client_id]
        print(f"❌ Client disconnected: {client_id}")
        # Broadcast updated count
        emit('client_count_update', {'count': len(clients)}, broadcast=True)

@socketio.on('audio_data')
def handle_audio_data(data):
    # Broadcast audio to all OTHER clients
    emit('audio_stream', {
        'audio_data': data['audio_data'],
        'timestamp': datetime.now().isoformat(),
        'client_id': request.sid
    }, broadcast=True, include_self=False)

@socketio.on('ping')
def handle_ping():
    emit('pong', {'message': 'pong', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 INTERCOM REAL-TIME SERVER STARTING...")
    socketio.run(app, host='0.0.0.0', port=10000, debug=False)

from flask import Flask, request, jsonify
import json
import threading
import time
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
DATA_FILE = 'events.json'

# Load events from file at startup
try:
    with open(DATA_FILE, 'r') as f:
        events = json.load(f)
except FileNotFoundError:
    events = []

# Helper to save events to file
def save_events():
    with open(DATA_FILE, 'w') as f:
        json.dump(events, f, indent=4)

# Reminder checker every minute
def reminder_checker():
    while True:
        now = datetime.now()
        upcoming = []
        for event in events:
            start_time = datetime.fromisoformat(event['start_time'])
            if now <= start_time <= now + timedelta(hours=1):
                upcoming.append(event)
        if upcoming:
            print("🔔 Upcoming Events within 1 hour:")
            for e in upcoming:
                print(f"{e['title']} at {e['start_time']}")
        time.sleep(60)

# Start the reminder thread as daemon
threading.Thread(target=reminder_checker, daemon=True).start()

# Root route
@app.route('/')
def home():
    return "✅ Event Scheduler API is running."

# Create Event
@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    new_event = {
        "id": str(uuid.uuid4()),
        "title": data['title'],
        "description": data['description'],
        "start_time": data['start_time'],
        "end_time": data['end_time']
    }
    events.append(new_event)
    save_events()
    return jsonify(new_event), 201

# Get All Events
@app.route('/events', methods=['GET'])
def get_events():
    sorted_events = sorted(events, key=lambda x: x['start_time'])
    return jsonify(sorted_events), 200

# Update Event
@app.route('/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    for event in events:
        if event['id'] == event_id:
            event.update({
                "title": data.get('title', event['title']),
                "description": data.get('description', event['description']),
                "start_time": data.get('start_time', event['start_time']),
                "end_time": data.get('end_time', event['end_time'])
            })
            save_events()
            return jsonify(event), 200
    return jsonify({"error": "Event not found"}), 404

# Delete Event
@app.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    global events
    events = [e for e in events if e['id'] != event_id]
    save_events()
    return jsonify({"message": "Deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)

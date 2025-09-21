from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Chatterbox API</h1>'

# GET /messages - returns all messages ordered by created_at in ascending order
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = db.session.execute(db.select(Message).order_by(Message.created_at.asc())).scalars().all()
    return jsonify([message.to_dict() for message in messages])

# POST /messages - creates a new message
@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        new_message = Message(
            body=data.get('body'),
            username=data.get('username')
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# PATCH /messages/<int:id> - updates a message's body
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    try:
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']
        
        db.session.commit()
        return jsonify(message.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# DELETE /messages/<int:id> - deletes a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    try:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
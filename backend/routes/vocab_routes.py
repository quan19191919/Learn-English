from flask import Blueprint, request, jsonify
from models.database import get_db_connection

vocab_bp = Blueprint('vocab', __name__)

@vocab_bp.route('/vocab-sets', methods=['POST'])
def create_vocab_set():
    data = request.json
    name = data['name']
    language = data['language']
    level = data['level']
    topic = data['topic']
    created_by = data['created_by']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vocab_sets (name, language, level, topic, created_by)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, language, level, topic, created_by))
    conn.commit()
    return jsonify({'message': 'Tạo bộ từ vựng thành công'})

@vocab_bp.route('/vocab-sets', methods=['GET'])
def get_vocab_sets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vocab_sets")
    return jsonify(cursor.fetchall())

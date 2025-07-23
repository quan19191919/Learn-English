from flask import Blueprint, request, jsonify
from models.database import get_db_connection

word_bp = Blueprint('word', __name__)

@word_bp.route('/words', methods=['POST'])
def add_word():
    data = request.json
    term, definition, example, image_url, audio_url, set_id = (
        data['term'], data['definition'], data['example'], data['image_url'], data['audio_url'], data['set_id']
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO words (term, definition, example, image_url, audio_url, set_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (term, definition, example, image_url, audio_url, set_id))
    conn.commit()
    return jsonify({'message': 'Thêm từ vựng thành công'})

@word_bp.route('/words/<int:set_id>', methods=['GET'])
def get_words_by_set(set_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM words WHERE set_id = %s", (set_id,))
    return jsonify(cursor.fetchall())

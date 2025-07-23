from flask import Blueprint, request, jsonify
from models.database import get_db_connection

game_bp = Blueprint('game', __name__)

@game_bp.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.json
    type = data['type']
    set_id = data['set_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exercises (type, set_id) VALUES (%s, %s)", (type, set_id))
    conn.commit()
    return jsonify({'message': 'Tạo bài tập thành công'})

@game_bp.route('/exercise-questions', methods=['POST'])
def add_question():
    data = request.json
    exercise_id = data['exercise_id']
    question = data['question']
    options = data['options']
    correct_answer = data['correct_answer']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exercise_questions (exercise_id, question, options, correct_answer) VALUES (%s, %s, %s, %s)",
                   (exercise_id, question, options, correct_answer))
    conn.commit()
    return jsonify({'message': 'Thêm câu hỏi thành công'})

@game_bp.route('/game-scores', methods=['POST'])
def save_score():
    data = request.json
    user_id = data['user_id']
    exercise_id = data['exercise_id']
    score = data['score']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO game_scores (user_id, exercise_id, score) VALUES (%s, %s, %s)",
                   (user_id, exercise_id, score))
    conn.commit()
    return jsonify({'message': 'Lưu điểm thành công'})

@game_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, gs.score, gs.played_at
        FROM game_scores gs
        JOIN users u ON gs.user_id = u.id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    return jsonify(cursor.fetchall())

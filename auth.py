import hashlib
import re
import sqlite3
from database import create_connection

# Регистрация
def register(email, password):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email format"

    if not password:
        return "Password cannot be empty"

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
        return "Registration successful!"
    except sqlite3.IntegrityError:
        return "Email already registered"
    finally:
        conn.close()

# Авторизация
def login(email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ? AND password = ?', (email, hashed_password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0], "Login successful!"
    else:
        return None, "Invalid email or password"

# Сохранение рекордов
def save_score(user_id, score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', (user_id, score))
    conn.commit()
    conn.close()

# Получение топ-10 рекордов
def get_top_scores():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT users.email, scores.score, scores.date 
                      FROM scores 
                      JOIN users ON scores.user_id = users.id 
                      ORDER BY score DESC 
                      LIMIT 10''')
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores
from flask import Flask, jsonify, request
from flasgger import Swagger
from sqlalchemy import and_, between
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
from flask import Flask, request, jsonify
from pydantic import ValidationError
from schemas import ChildCreate  # Импортируйте вашу схему Pydantic
import logging
import hashlib
from antipyretic_calculator import calculateAntipyreticDosage
from creds import *
from data import *
from sqlalchemy.exc import IntegrityError
from database import DatabaseManager  # Импортируйте ваш класс DatabaseManager
from models import Base  # Импортируйте Base из models.py

db_manager = DatabaseManager()  # Создайте экземпляр DatabaseManager
    # Здесь вы можете добавить другие операции, если необходимо

# Создание Flask-приложения
app = Flask(__name__)




def validate_input(data):
    if not all(data.values()):
        return ERRORS['fields_required']

    username, email, password = data['username'], data['email'], data['password']

    if not 3 <= len(username) <= 30:
        return ERRORS['username_length']
    if not VALIDATORS['username'].match(username):
        return ERRORS['username_format']
    if not VALIDATORS['email'].match(email):
        return ERRORS['email_format']
    if not 8 <= len(password) <= 30:
        return ERRORS['password_length']
    if not VALIDATORS['password'].match(password):
        return ERRORS['password_strength']

    return None


@app.route('/api/register', methods=['POST'])
def register_user():
    db_manager = DatabaseManager()  # Создайте экземпляр DatabaseManager
    user_manager = UserManager(db_manager)  # Передайте его в UserManager
    try:
        data = {
            'username': request.json.get('username', '').strip(),
            'email': request.json.get('email', '').strip(),
            'password': request.json.get('password', '')
        }
        # Валидация данных
        if error := validate_input(data):
            return jsonify({'message': error[0]}), error[1]
        # Проверка уникальности username и email
        user_by_username, user_by_email = user_manager.user_exists(data['username'], data['email'])
        if user_by_username:
            return jsonify({'message': ERRORS['username_exists'][0]}), 409
        if user_by_email:
            return jsonify({'message': ERRORS['email_exists'][0]}), 409
        # Создание нового пользователя
        new_user = user_manager.create_user(data['username'], data['email'], hashlib.sha256(data['password'].encode()).hexdigest())
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        logging.error(f"Registration error: {e}")  # Логируем ошибку
        return jsonify({'message': 'Database error', 'details': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login_user():
    db_manager = DatabaseManager()  # Создайте экземпляр DatabaseManager
    user_manager = UserManager(db_manager)  # Передайте его в UserManager
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        user = user_manager.authenticate_user(username, password)
        if not user:
            return jsonify({'message': 'Неверные учетные данные'}), 401

        # Получаем user_id
        user_id = user.id
        access_token = create_access_token(identity=user_id)  # Генерация токена

        # Возвращаем токен и user_id
        return jsonify(access_token=access_token, user_id=user_id), 200
    except Exception as e:
        logging.error(f"Login error: {e}")  # Логируем ошибку
        return jsonify({'message': 'Database error', 'details': str(e)}), 500


@app.route('/api/auth/yandex', methods=['POST'])
def handle_yandex_auth():
    db_manager = DatabaseManager()  # Создайте экземпляр DatabaseManager
    user_manager = UserManager(db_manager)  # Передайте его в UserManager
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Токен отсутствует"}), 400
    try:
        # Получаем данные пользователя
        user_info = get_user_info(token)
        yandex_id = user_info["id"]  # Уникальный ID Яндекса
        # Проверяем, есть ли пользователь в БД
        user = user_manager.get_user_by_yandex_id(yandex_id)
        if not user:
            # Пользователя нет, создаем его
            username = user_info.get("login")
            email = user_info.get("default_email", user_info.get("emails", [None])[0])
            password = yandex_id  # Пароль = yandex_id (или можно оставить NULL)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            new_user = user_manager.create_user(username, email, hashed_password, is_yandex=1, yandex_id=yandex_id)
            # Получаем только что созданного пользователя
            user = user_manager.get_user_by_yandex_id(yandex_id)
        return jsonify({"success": True, "user": user_info})
    except IntegrityError as e:
        logging.error(f"IntegrityError: {e}")
        return jsonify({"error": "Ошибка базы данных: пользователь уже существует"}), 500
    except Exception as e:
        logging.error(f"Error during Yandex auth: {e}")
        return jsonify({"error": str(e)}), 500


def get_user_info(token):
    url = "https://login.yandex.ru/info"
    headers = {"Authorization": f"OAuth {token}"}
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка: {response.status_code}, {response.text}")


@app.route('/api/user', methods=['GET'])
@jwt_required()  # Проверка токена
def get_user_info():
    user_id = get_jwt_identity()  # Получаем ID пользователя из токена
    db_manager = DatabaseManager()  # Создаем экземпляр DatabaseManager
    user_manager = UserManager(db_manager)  # Передаем его в UserManager

    try:
        user = user_manager.get_user_by_id(user_id)  # Используем метод из UserManager
        if not user:
            return jsonify({'message': 'Пользователь не найден'}), 404

        # Преобразуем объект User в словарь для JSON
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_yandex": user.is_yandex,
            "yandex_id": user.yandex_id
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'message': 'Database error', 'details': str(e)}), 500


# @app.route('/api/children', methods=['POST'])
# def create_child_profile():
#     db_manager = DatabaseManager()  # Создайте экземпляр DatabaseManager
#     child_manager = ChildManager(db_manager)  # Передайте его в ChildManager
#     try:
#         # Получаем данные из запроса
#         data = request.json
#         # Валидация данных с помощью Pydantic
#         child_data = ChildCreate(**data)
#
#         # Извлекаем user_id и аллергенов из запроса
#         user_id = request.json.get('user_id')
#         allergens = request.json.get('allergens', [])
#
#         # Создание нового профиля ребенка
#         new_child = child_manager.create_child(
#             user_id=user_id,
#             name=child_data.name,
#             birth_date=child_data.birth_date,
#             gender=child_data.gender,
#             height=child_data.height,
#             weight=child_data.weight,
#             allergens=allergens
#         )
#         return jsonify({'message': 'Профиль ребенка создан успешно', 'child_id': new_child.id}), 201
#     except ValidationError as e:
#         logging.error(f"Validation error: {e}")  # Логируем ошибку валидации
#         return jsonify({'message': 'Ошибка валидации', 'details': e.errors()}), 400
#     except Exception as e:
#         logging.error(f"Error creating child profile: {e}")  # Логируем ошибку
#         return jsonify({'message': 'Ошибка базы данных', 'details': str(e)}), 500
#
#
# @app.route('/api/children', methods=['GET'])
# @jwt_required()
# def get_all_children():
#     user_id = get_jwt_identity()  # Получаем ID пользователя из токена
#     db_manager = DatabaseManager()  # Создаем экземпляр DatabaseManager
#     child_manager = ChildManager(db_manager)  # Передаем его в ChildManager
#
#     try:
#         children = child_manager.get_all_children_for_user(user_id)  # Используем метод из ChildManager
#         # Преобразуем объекты Child в словари для JSON
#         children_data = [{
#             "id": child.id,
#             "name": child.name,
#             "birth_date": child.birth_date.isoformat(),
#             "gender": child.gender,
#             "height": child.height,
#             "weight": child.weight,
#             "allergens": [{"id": allergen.id, "name": allergen.name} for allergen in child.allergens]
#         } for child in children]
#         return jsonify(children_data), 200
#     except Exception as e:
#         return jsonify({'message': 'Database error', 'details': str(e)}), 500
#
# @app.route('/api/children/<int:child_id>', methods=['GET'])
# @jwt_required()
# def get_child(child_id: int):
#     user_id = get_jwt_identity()  # Получаем ID пользователя из токена
#     db_manager = DatabaseManager()  # Создаем экземпляр DatabaseManager
#     child_manager = ChildManager(db_manager)  # Передаем его в ChildManager
#
#     try:
#         child = child_manager.get_child_by_id(user_id, child_id)  # Используем метод из ChildManager
#         if not child:
#             return jsonify({'message': 'Ребенок не найден'}), 404
#
#         # Преобразуем объект Child в словарь для JSON
#         child_data = {
#             "id": child.id,
#             "name": child.name,
#             "birth_date": child.birth_date.isoformat(),
#             "gender": child.gender,
#             "height": child.height,
#             "weight": child.weight,
#             "allergens": [{"id": allergen.id, "name": allergen.name} for allergen in child.allergens]
#         }
#         return jsonify(child_data), 200
#     except Exception as e:
#         return jsonify({'message': 'Database error', 'details': str(e)}), 500
#
#



@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    try:
        # Создание сессии
        session = db_manager.Session()

        # Выполняем запрос с JOIN и сортировкой
        drugs = session.query(Drug, DrugsCategory.category_name) \
            .join(DrugsCategory, Drug.category_id == DrugsCategory.category_id) \
            .order_by(DrugsCategory.category_name, Drug.name) \
            .all()

        # Группируем препараты по категориям
        drugs_by_categories = {}
        for drug, category_name in drugs:
            if category_name not in drugs_by_categories:
                drugs_by_categories[category_name] = []
            drugs_by_categories[category_name].append({
                'id': drug.id,
                'name': drug.name,
                'tablet_only': drug.tablet_only,
                'mls_var': drug.mls_var,
                'instructions': drug.instructions
            })

        return jsonify(drugs_by_categories)

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch drugs from the database."}), 500
    finally:
        session.close()  # Закрываем сессию


##Расчет дозировки и сохранение в БД@app.route('/calculate', methods=['POST'])
@app.route('/api/calculate', methods=['POST'])
def calculate_dosage():
    data = request.json
    try:
        result = calculateAntipyreticDosage(data)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400



@app.route('/api/calculation-history/', methods=['GET'])
def get_calculation_history():
    user_id = request.args.get('user_id')
    category_name = request.args.get('category_name', default=None, type=str)
    date_from = request.args.get('date_from', default=None, type=str)
    date_to = request.args.get('date_to', default=None, type=str)

    # Проверяем наличие обязательного параметра
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        # Создание сессии
        session = db_manager.Session()

        # Формируем базовый запрос
        query = session.query(CalculationHistory).join(
            DrugsCategory, CalculationHistory.calculation_type == DrugsCategory.category_id
        ).filter(CalculationHistory.user_id == user_id)

        # Добавляем фильтры, если они переданы
        if category_name:
            query = query.filter(DrugsCategory.category_name == category_name)

        if date_from and date_to:
            # Преобразуем строки в объекты datetime
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(between(CalculationHistory.calculation_time, date_from, date_to))

        # Выполняем запрос
        history = query.all()

        # Преобразуем данные в формат JSON
        result = []
        for row in history:
            result.append({
                'id': row.id,
                'user_id': row.user_id,
                'drug_name': row.drug_name,
                'calculation_type': row.calculation_type,
                'weight': row.weight,
                'standard_dose_ml': row.dosage_mls,
                'high_dose_ml': row.highMgs,
                'suppositories_high': row.suppositories_high,
                'suppositories_min': row.suppositories_min,
                'created_at': row.calculation_time.strftime('%Y-%m-%d %H:%M:%S')  # Форматируем дату
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()  # Закрываем сессию


# Запуск приложения
if __name__ == '__main__':
    # Инициализация базы данных
    db_manager
    #populate_initial_data()
    app.config['SWAGGER'] = {
        'title': 'Calculator API',
        'host': 'localhost:8080',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'swagger_ui_bundle_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui-bundle.js',
        'swagger_ui_standalone_preset_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui-standalone-preset.js',
        'swagger_ui_css': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui.css',
        'jquery_js': 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js'
    }
    Swagger(app, template_file='swagger.yaml')

    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените 'your-secret-key' на ваш секретный ключ
    jwt = JWTManager(app)
    # Настройка CORS
    CORS(app)
    app.run()

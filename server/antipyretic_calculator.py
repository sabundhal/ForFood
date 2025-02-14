from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib



##Расчет дозировки и сохранение в БД@app.route('/calculate', methods=['POST'])
# @app.route('/api/calculate', methods=['POST'])
# #@jwt_required()  # Защищаем маршрут JWT-токеном
# def calculate_dosage():
#     data = request.json
#     user_id = data.get('user_id')
#     drug_id = data.get('drug_id')
#     weight = data.get('weight')
#     weight = float(weight)
#
#     # Проверяем наличие обязательных параметров
#     if user_id is None or drug_id is None or weight is None:
#         return jsonify({'error': 'user_id, drug_id, and weight are required'}), 400
#     # Проверяем корректность веса
#     if weight <= 0:
#         return jsonify({'error': 'Weight must be greater than 0'}), 400
#     # Получаем данные о препарате из базы данных
#     try:
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#
#         # Запрос данных о препарате
#         #можно ли тут написать. select *?
#         cursor.execute('''SELECT name, category_id, mls_var, mgs_var
#                           FROM drugs
#                           WHERE id = ?''', (drug_id,))
#         drug = cursor.fetchone()
#
#         if not drug:
#             conn.close()
#             return jsonify({'error': 'Drug not found'}), 404
#
#         # Извлекаем данные из результата запроса
#         name, category_id, mls_var, mgs_var = drug
#
#         # Выполняем расчеты
#         mls_total = weight * mls_var
#         mgs_total = weight * mgs_var
#
#         # Сохраняем расчет в историю
#         # Установка значений для всех 23 полей
#         cursor.execute('''
#             INSERT INTO calculation_history (
#                 user_id, calculation_id, drug_id, drug_name, username, weight, dosage_mls, dosage_mgs,
#                 totalMgs, totalhigh, totalhighsachets, maximumMgsPerDay, highMgs,
#                 loading_dose, strep_drug, messageMgs, messageOther, calculation_type,
#                 calculation_status, calculation_version, patient_id, patient_name, error_message, age
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
#                        (
#                            user_id, None, drug_id, name, 'Username', weight, mls_total, mgs_total,
#                            0, 0, 0, 0, 0, 0, 0, 'Message', None, category_id,
#                            'Status', 'Version', 0, 'Patient Name', None , None
#                        ))
#         # Получаем автоматически сгенерированный id
#         calculation_id = cursor.lastrowid
#         # Обновляем запись, чтобы установить calculation_id равным id
#         cursor.execute('''
#             UPDATE calculation_history
#             SET calculation_id = ?
#             WHERE id = ?''',
#                        (calculation_id, calculation_id))
#         conn.commit()
#
#
#     except sqlite3.Error as e:
#         return jsonify({'error': f'Database error: {str(e)}'}), 500
#
#         # Возвращаем ответ с calculation_id
#     return jsonify({
#             'mlsTotal': mls_total,
#             'mgsTotal': mgs_total,
#             'calculation_id': calculation_id
#         })
#     conn.close()


def validateInput(data):
    """
    Проверяет корректность входных данных.
    :param data: Входные данные (user_id, drug_id, weight)
    :raises ValueError: Если данные некорректны
    """
    if not all(k in data for k in ['user_id', 'drug_id', 'weight']):
        raise ValueError("user_id, drug_id, and weight are required")
    try:
        weight = float(data['weight'])
        if weight <= 0:
            raise ValueError("Weight must be greater than 0")
    except ValueError:
        raise ValueError("Weight must be a valid number")

def fetchDrugInfo(drug_id):
    """
    Получает данные о препарате из базы данных.
    :param drug_id: ID препарата
    :return: Словарь с данными о препарате
    :raises ValueError: Если препарат не найден или произошла ошибка БД
    """
    try:
        conn = sqlite3.connect('myapp.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT name, category_id, mls_var, mgs_var, mls_max, mgs_max, high_range, high_modifier, mls_max_high, mgs_max_high
                                 FROM drugs
                                 WHERE id = ?''', (drug_id,))
        drug = cursor.fetchone()
        if not drug:
            raise ValueError("Drug not found")
        return {
            'name': drug[0],                 # Название препарата
            'category_id': drug[1],          # ID категории
            'mls_var': drug[2],              # Объем на одну дозу (мл)
            'mgs_var': drug[3],              # Доза на одну дозу (мг)
            'mls_max': drug[4],              # Максимальный объем в сутки (мл)
            'mgs_max': drug[5],              # Максимальная доза в сутки (мг)
            'high_range': drug[6],           # Флаг для высокой дозировки
            'high_modifier': drug[7],        # Модификатор для высокой дозировки
            'mls_max_high': drug[8],         # Максимальный объем для высокой дозировки (мл)
            'mgs_max_high': drug[9]          # Максимальная доза для высокой дозировки (мг)
        }
    except sqlite3.Error as e:
        raise ValueError(f"Database error: {str(e)}")
    finally:
        conn.close()

def calculateDosage(weight, drug_info):
    """
    Рассчитывает дозировку на основе веса пациента.
    :param weight: Вес пациента (кг)
    :param drug_info: Данные о препарате (mls_var, mgs_var)
    :return: mls_total, mgs_total
    """
    # Стандартная дозировка
    mls_total = weight * drug_info['mls_var']
    mgs_total = weight * drug_info['mgs_var']

    # Проверка на высокую дозировку
    if drug_info['high_range'] == 1:  # Если высокая дозировка разрешена
        # Применяем high_modifier к стандартной дозировке
        mls_high = weight * drug_info['mls_var'] * drug_info['high_modifier']
        mgs_high = weight * drug_info['mgs_var'] * drug_info['high_modifier']
        # Проверка, чтобы высокая дозировка не превышала максимальную суточную дозу
        if mls_high > drug_info['mls_max']:
            mls_high = drug_info['mls_max']
        if mgs_high > drug_info['mgs_max']:
            mgs_high = drug_info['mgs_max']
    else:
        mls_high = None
        mgs_high = None

    return {
        'standard_dose_ml': mls_total,  # Стандартный объем на одну дозу (мл)
        'standard_dose_mg': mgs_total,  # Стандартная доза на одну дозу (мг)
        'high_dose_ml': mls_high,  # Высокий объем на одну дозу (мл)
        'high_dose_mg': mgs_high,  # Высокая доза на одну дозу (мг)
        'max_dose_ml': drug_info['mls_max'],  # Максимальный объем в сутки (мл)
        'max_dose_mg': drug_info['mgs_max']  # Максимальная доза в сутки (мг)
    }
#def saveCalculationToDB(data, mls_total, mgs_total, drug_info, category_id, mls_high):
def saveCalculationToDB(data, standard_dose_ml, standard_dose_mg, drug_info, category_id, high_dose_ml):
    """
    Сохраняет результат расчета в базу данных.
    :param data: Входные данные (user_id, drug_id, weight)
    :param mls_total: Рассчитанный объем (мл)
    :param mgs_total: Рассчитанная доза (мг)
    :param drug_info: Данные о препарате
    :return: ID расчета
    :raises ValueError: Если произошла ошибка БД
    """
    try:
        conn = sqlite3.connect('myapp.db')
        cursor = conn.cursor()
        cursor.execute('''
                    INSERT INTO calculation_history (
                        user_id, calculation_id, drug_id, drug_name, username, weight, dosage_mls, dosage_mgs,
                        totalMgs, totalhigh, totalhighsachets, maximumMgsPerDay, highMgs,
                        loading_dose, strep_drug, messageMgs, messageOther, calculation_type,
                        calculation_status, calculation_version, patient_id, patient_name, error_message, age
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
                               (
                                   data['user_id'], None, data['drug_id'], drug_info['name'], 'Username', float(data['weight']), standard_dose_ml, standard_dose_mg,
                                   0, high_dose_ml, 0, 0, 0, 0, 0, 'Message', None, category_id,
                                   'Status', 'Version', 0, 'Patient Name', None , None))
        calculation_id = cursor.lastrowid
        # Обновляем запись, чтобы установить calculation_id равным id
        cursor.execute('''
                    UPDATE calculation_history
                    SET calculation_id = ?
                    WHERE id = ?''',
                               (calculation_id, calculation_id))
        conn.commit()
        return calculation_id
    except sqlite3.Error as e:
        raise ValueError(f"Database error: {str(e)}")
    finally:
        conn.close()


def calculateAntipyreticDosage(data):
    """
    Основная функция для расчета дозировки жаропонижающего препарата.
    :param data: Входные данные (user_id, drug_id, weight)
    :return: Словарь с результатами расчета
    :raises ValueError: Если произошла ошибка
    """
    validateInput(data)
    drug_info = fetchDrugInfo(data['drug_id'])
    category_id = drug_info['category_id']
    # Вызов calculateDosage, который возвращает нужные значения
    result = calculateDosage(float(data['weight']), drug_info)
    # Вызов saveCalculationToDB с новыми параметрами
    calculation_id = saveCalculationToDB(
        data,
        result['standard_dose_ml'],  # standard_dose_ml
        result['standard_dose_mg'],  # standard_dose_mg
        drug_info,
        category_id,
        result['high_dose_ml']  # high_dose_ml
    )

    # Возвращаем все необходимые поля
    return {
        'standard_dose_ml': result['standard_dose_ml'],  # Стандартный объем (мл)
        'standard_dose_mg': result['standard_dose_mg'],  # Стандартная доза (мг)
        'high_dose_ml': result['high_dose_ml'],  # Высокий объем (мл)
        'high_dose_mg': result['high_dose_mg'],  # Высокая доза (мг)
        'max_dose_ml': drug_info['mls_max'],  # Максимальный объем (мл)
        'max_dose_mg': drug_info['mgs_max'],  # Максимальная доза (мг)
        'calculation_id': calculation_id  # ID расчета
    }
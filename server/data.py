from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.exc import NoResultFound  # Для обработки ошибок
from datetime import date
from database import DatabaseManager
from models import Child
from schemas import ChildCreate
from sqlalchemy.orm import joinedload
import logging
import hashlib
from models import *

from sqlalchemy.exc import IntegrityError
from models import User  # Импортируйте вашу модель User
from database import DatabaseManager  # Импортируйте ваш экземпляр DatabaseManager

class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_user(self, username, email, password, is_yandex=0, yandex_id=None):
        session = self.db_manager.get_session()
        try:
            user = User(
                username=username,
                email=email,
                password=password,
                is_yandex=is_yandex,
                yandex_id=yandex_id
            )
            session.add(user)
            session.commit()
            return user
        except IntegrityError as e:
            session.rollback()
            logging.error(f"IntegrityError: {e}")
            raise
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating user: {e}")
            raise
        finally:
            session.close()

    def get_user_by_id(self, user_id: int):
        """
        Возвращает информацию о пользователе по его ID.
        :param user_id: ID пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).one()
            print(f" get_user_by_id информация о юзере: {user}")  # Логируем введенные данные
            return user
        except NoResultFound:
            print(f" get_user_by_id не найден юзер:")
            return None
        except Exception as e:
            logging.error(f"Error fetching user: {e}")
            raise
        finally:
            session.close()

    def user_exists(self, username, email):
        session = self.db_manager.get_session()
        try:
            user_by_username = session.query(User).filter_by(username=username).first()
            user_by_email = session.query(User).filter_by(email=email).first()
            return user_by_username, user_by_email
        finally:
            session.close()

    def get_user_by_yandex_id(self, yandex_id):
        session = self.db_manager.get_session()
        try:
            return session.query(User).filter_by(yandex_id=yandex_id).first()
        finally:
            session.close()

    def authenticate_user(self, username, password):
        session = self.db_manager.get_session()
        try:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            print(f"Hashed password: {hashed_password}")  # Логируем хешированный пароль
            user = session.query(User).filter_by(username=username, password=hashed_password).first()
            if not user:
                print("User not found")  # Логируем, если пользователь не найден
            return user
        finally:
            session.close()

class ChildManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_child(self, user_id: int, name: str, birth_date: str, gender: str, height: float, weight: float,
                     allergens: list = None):  # allergens теперь необязательный параметр
        session = self.db_manager.get_session()
        try:
            # Преобразуем строку даты в объект date (если birth_date - строка)
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()

            # Создаем объект ребенка
            child = Child(
                user_id=user_id,
                name=name,
                birth_date=birth_date,
                gender=gender,
                height=height,
                weight=weight
            )
            session.add(child)
            session.flush()  # Сохраняем ребенка, чтобы получить его ID, но не фиксируем транзакцию

            # Привязываем аллергены к ребенку (если они есть)
            if allergens:  # Проверяем, что allergens не None и не пустой список
                for allergen_id in allergens:
                    # Проверяем, существует ли аллерген
                    allergen = session.query(Ingredient).get(allergen_id)
                    if not allergen:
                        raise ValueError(f"Аллерген с ID {allergen_id} не найден")
                    child_allergen = ChildAllergen(child_id=child.id, ingredient_id=allergen_id)
                    session.add(child_allergen)

            session.commit()  # Фиксируем все изменения
            session.refresh(child)  # Обновляем объект child
            return child
        except IntegrityError as e:
            session.rollback()
            logging.error(f"IntegrityError: {e}")
            raise
        except Exception as e:
            session.rollback()
            logging.error(f"Error creating child: {e}")
            raise
        finally:
            session.close()



    def get_all_children_for_user(self, user_id: int):
        """Возвращает всех детей для указанного пользователя.
        :param user_id: ID пользователя.
        :return: Список детей."""
        session = self.db_manager.get_session()
        try:
            children = (
                session.query(Child)
                .options(joinedload(Child.allergens))  # Загружаем аллергены
                .filter(Child.user_id == user_id)
                .all()
            )
            return children
        except Exception as e:
            logging.error(f"Error fetching children: {e}")
            raise
        finally:
            session.close()

    from sqlalchemy.orm import joinedload

    def get_child_by_id(self, user_id: int, child_id: int):
        """
        Возвращает ребенка по ID, если он принадлежит указанному пользователю.
        :param user_id: ID пользователя.
        :param child_id: ID ребенка.
        :return: Ребенок или None, если не найден.
        """
        session = self.db_manager.get_session()
        try:
            child = (
                session.query(Child)
                .options(joinedload(Child.allergens))  # Загружаем аллергены
                .filter(
                    Child.id == child_id,
                    Child.user_id == user_id
                )
                .first()
            )
            return child
        except Exception as e:
            logging.error(f"Error fetching child: {e}")
            raise
        finally:
            session.close()

    def update_child(self, child_id, name, birth_date, gender, height, weight, allergens):
        """
        Обновляет данные ребенка.
        :param child_id: ID ребенка.
        :param name: Имя ребенка.
        :param birth_date: Дата рождения.
        :param gender: Пол.
        :param height: Рост.
        :param weight: Вес.
        :param allergens: Список аллергенов.
        :return: Обновленный ребенок или None, если ребенок не найден.
        """
        session = self.db_manager.get_session()
        try:
            # Получаем ребенка по ID
            child = (
                session.query(Child)
                .options(joinedload(Child.allergens))  # Загружаем аллергены
                .filter(Child.id == child_id)
                .first()
            )
            if not child:
                return None

            # Обновляем данные ребенка
            child.name = name
            child.birth_date = birth_date
            child.gender = gender
            child.height = height
            child.weight = weight
            child.allergens = allergens

            # Сохраняем изменения в базе данных
            session.commit()

            # Обновляем объект, чтобы получить актуальные данные
            session.refresh(child)
            return child
        except Exception as e:
            logging.error(f"Error updating child: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def delete_child(self, child_id):
        """
        Удаляет ребенка по ID.
        :param child_id: ID ребенка.
        :return: True, если ребенок удален, иначе False.
        """
        session = self.db_manager.get_session()
        try:
            # Получаем ребенка по ID
            child = session.query(Child).filter(Child.id == child_id).first()
            if not child:
                return False
            # Удаляем ребенка
            session.delete(child)
            session.commit()
            return True
        except Exception as e:
            logging.error(f"Error deleting child: {e}")
            session.rollback()
            raise
        finally:
            session.close()


# # Инициализация базы данных
# def initialize_database():
#     engine = create_engine('sqlite:///myapp2.db')
#     Base.metadata.create_all(engine)
#     print("Database initialized successfully.")
#
# def populate_initial_data():
#     engine = create_engine('sqlite:///myapp2.db')
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     try:
#         # Заполнение таблицы drugs_categories
#         categories_objects = []
#         for category_tuple in categories_data:
#             category_dict = dict(zip(category_fields, category_tuple))  # Сопоставляем поля с данными
#             category = DrugsCategory(**category_dict)  # Создаем объект DrugsCategory
#             categories_objects.append(category)
#
#         session.add_all(categories_objects)
#
#         # Заполнение таблицы drugs
#         drugs_objects = []
#         for drug_tuple in drugs_data:
#             drug_dict = dict(zip(drug_fields, drug_tuple))  # Сопоставляем поля с данными
#             drug = Drug(**drug_dict)  # Создаем объект Drug
#             drugs_objects.append(drug)
#
#         session.add_all(drugs_objects)
#
#         session.commit()
#         print("Initial data populated successfully.")
#     except Exception as e:
#         session.rollback()
#         print(f"Error populating initial data: {e}")
#     finally:
#         session.close()
#
# categories_data = [
#             (1, 'Analgesics'),
#             (2, 'Antibiotics'),
#             (3, 'Anti-inflammatory'),
#             (4, 'Antipyretic'),
#             (5, 'Antiviral'),
#                (6, 'Rectal antipyretic')
#         ]
# category_fields = ['category_id', 'category_name']
#
# users_data = [
#     ('user1', 'user1@example.com', 'b6ad34b0b6b7e38f878a513b3f7927ebeb4cffb01aeb6d9fd9f9ad67fbc76517', 0, None),
#     ('yandex_user', 'yandex_user@example.com', 'b6ad34b0b6b7e38f878a513b3f7927ebeb4cffb01aeb6d9fd9f9ad67fbc76517', 1, '123456789')
# ]
#
# user_fields = ['username', 'email', 'password', 'is_yandex', 'yandex_id']
#
# drug_fields = [
#     'name', 'category_id', 'tablet_only', 'mls_var', 'mgs_var', 'number_of_times_a_day',
#     'mls_max', 'mgs_max', 'loading_dose', 'mls_var_loading', 'mgs_var_loading',
#     'mls_max_loading', 'mgs_max_loading', 'instructions', 'nzf_link',
#     'high_range', 'high_modifier', 'mls_max_high', 'mgs_max_high',
#     'strep_drug', 'strep_frequency', 'mls_var_strep', 'mgs_var_strep',
#     'mls_strep_max', 'mgs_strep_max', 'weight_cutoff_1', 'weight_cutoff_2',
#     'range1_dose', 'range2_dose', 'form', 'age_range'
# ]
#
# drugs_data = [
# ('Парацетамол суспензия 24мл/мг (120мл/5мг)', 1, False, 0.625, 15, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#         Для детей в возрасте от 3 до 12 месяцев 2,5-5 мл сиропа (60-120 мг парацетамола).
#         Для детей от 1 года до 5 лет – 5-10 мл сиропа (120-240 мг парацетамола).
#         Для детей в возрасте от 5 до 12 лет – 10-20 мл сиропа (240-480 мг парацетамола).
#         Взрослые и дети массой тела выше 60 кг - 20-40 мл сиропа (480-960 мг парацетамола).
#         Частота приема сиропа парацетамола составляет 3-4 раза в день.''', 42,
#              60, True, 1.25, 30, 62.5, 1500,
#              'Противопоказания: возраст до 1 месяца, детям в возрасте до 3-х месяцев применять с осторожностью.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=343f01d1-bbda-436f-978c-d1a23dc670eb  https://www.eapteka.ru/volgograd/goods/id224735/', True, 1.5, None, None, False, '', None, None, None, None, None, None, None, 24, None, None),
#
#
#         ('Парацетамол ФортеКидс суспензия для приема внутрь 250 мг/5 мл', 1, False, 0.3, 15, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#         Разовая доза у детей - 10-15 мг/кг массы тела.
#         Максимальная суточная доза у детей - 60 мг/кг массы тела при приеме отдельными разовыми дозами по 10-15 мг/кг массы тела в течение 24 ч.''', 20,
#              1000, True, 0.6, 30, 30, 1500,
#              'Противопоказания: Не давайте ребенку более 4 доз в течение 24 часов! ПАРАЦЕТАМОЛ ФортеКидс ПОКАЗАН для симптоматической терапии у детей старше 6 лет и взрослых ',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=86c53657-c25d-4d2b-b0ad-92fa25ed74e4  https://www.eapteka.ru/volgograd/goods/id521602/', True, 1.5, None, None, False, '', None, None, None, None, None, None, None, 50, None, None),
#
#             ('Ибупрофен суспензия 100мг/5мл', 1, False, 0.25, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#         Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка c интервалами между приемами препарата 6-8 часов.
#         Дети в возрасте 3-6  месяцев (вес ребенка от 5 до 7,6 кг): по 2,5 мл (50 мг) до 3 раз в течение 24 часов, не более 7,5 мл (150 мг) в сутки.
#         Дети в возрасте 6-12 месяцев (вес ребенка 7,7 - 9 кг): по 2,5 мл (50 мг) до 3-4 раз в течение 24 часов, не более 10 мл (200 мг) в сутки.
#         Дети в возрасте 1-3 года (вес ребенка 10 - 16 кг): по 5,0 мл (100 мг) до 3 раз в течение 24 часов, не более 15 мл (300 мг) в сутки.
#         Дети в возрасте 4-6 лет (вес ребенка 17 - 20 кг): по 7,5 мл (150 мг) до 3 раз в течение 24 часов, не более 22,5 мл (450 мг) в сутки.
#         Дети в возрасте 7-9 лет (вес ребенка 21 - 30 кг): по 10 мл (200 мг) до 3 раз в течение 24 часов, не более 30 мл (600 мг) в сутки.
#         Дети в возрасте 10-12 лет (вес ребенка 31 - 40 кг): по 15 мл (300 мг) до 3 раз в течение 24 часов, не более 45 мл (900 мг) в сутки.''', 10, 200, False, None, None, None, None,
#              'Противопоказания: масса тела менее 5 кг, возраст менее 3 месяцев. Если при приеме препарата в течение 24 часов (у детей в возрасте 3-5 месяцев) или в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=a1ab07d8-6779-4029-9b52-04aa390eb440  https://www.eapteka.ru/volgograd/goods/id250621/', True, 2, None, None, False, '', None, None, None, None, None, None, None, 20, None, None),
#
#             ('Ибупрофен форте 40мг/мл (200мг/5мл)', 1, False, 0.125, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#         Возраст (Масса тела) Разовая доза мл препарата/ мг ибупрофена Максимальная суточная доза мл препарата/ мг ибупрофена
#         1-3 года (10-16 кг) 2,5 мл (100 мг) 7,5 мл (300 мг)
#         4-6 лет (17-20 кг) 3,75 мл (150 мг) 11,25 мл (450 мг)
#         7-9 лет (21-30 кг) 5 мл (200 мг) - 15 мл (600 мг)
#         10-12 лет (31-40 кг) 7,5 мл (300 мг) 22,5 мл (900 мг)
#         13 лет и старше (масса тела более 40кг) 7,5-10 мл (300-400 мг) 30 мл (1200 мг)''', 10, 400, False, None, None, None, None,
#              'Противопоказания: масса тела ребенка менее 10 кг, возраст до 1 года. Если улучшение не наступило или Вы чувствуете ухудшение через 3 дня, необходимо обратиться к врачу.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=a1ab07d8-6779-4029-9b52-04aa390eb440  https://www.eapteka.ru/volgograd/goods/id514767/', False, 2, None, None, False, '', None, None, None, None, None, None, None, 40, None, None),
#
#             ('Ибупрофен суппозитории ректальные для детей 60 мг', 6, False, None, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#         Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка с интервалами между приемами препарата 6-8 часов.
#         Дети в возрасте от 3 до 9 месяцев с массой тела от 6,0 кг до 8,0 кг - по 1 суппозиторию (60 мг) до 3 раз в течение 24 часов, не более 180 мг в сутки.
#         Дети в возрасте от 9 месяцев до 2 лет с массой тела от 8,0 кг до 12,0 кг - по 1 суппозиторию (60 мг) до 4 раз в течение 24 часов, не более 240 мг в сутки.''', None, 180,
#              False, None, None, None, None,
#              'Противопоказания: масса тела ребенка менее 6 кг, возраст до 3 месяцев. Если при приеме препарата в течение 24 часов (у детей в возрасте 3-5 месяцев) или в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=e9ee3f13-8126-4c0c-94f3-9e6069827956  https://www.eapteka.ru/volgograd/goods/id509733/', True, 2, None, None, False, '', None, None, None, None, None, None,
#              60, None, 'суппозитории ректальные', None),
#
#             ('Ибупрофен (Брудол) суппозитории ректальные для детей 125 мг,', 6, False, None, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
#             Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка с интервалами между приемами препарата 6-8 часов.
#             Дети в возрасте от 2 до 4 лет с массой тела от 12,5 до 17 кг - по 1 суппозиторию (125) до 3 раз в течение 24 часов, не более 375 мг в сутки. Дети в возрасте от 4 до 6 лет с массой 17 кг до 20,5 кг - по 1 суппозиторию (125мг) до 4 раз в сутки в течение 24 часов, не более 50 мг в сутки. ''', None, 375,
#              False, None, None, None, None,
#              'Противопоказания: масса тела ребенка менее 12 кг, возраст до 2х лет. Если при приеме препарата  в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=420ddf02-9061-49a6-b652-67a0f16dbab8  https://aptekiplus.ru/moskva/product/brudol-dlya-detey-125-mg-10-sht-suppozitorii-rektalnie-dlya-detey/?utm_referrer=https://www.google.com/', True, 2, None, None, False, '', None, None, None, None, None, None,
#              125, None, 'суппозитории ректальные', None),
#
#             ('Цефекон Д (парацетамол) для детей суппозитории ректальные 50 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
#             Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
#             Возраст	Вес	Разовая доза
#             1–3 месяца	4–6 кг	1 суппозиторий по 50 мг
#             3–12 месяцев	7–10 кг	1 суппозиторий по 100 мг
#             1–3 года	11–16 кг	1–2 суппозитория по 100 мг
#             3–10 лет	17–30 кг	1 суппозиторий по 250 мг
#             10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
#              False, None, None, None, None,
#              'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206253/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
#              50, None, 'суппозитории ректальные', None),
#
#             ('Цефекон Д (парацетамол) для детей суппозитории ректальные 100 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
#             Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
#             Возраст	Вес	Разовая доза
#             3–12 месяцев	7–10 кг	1 суппозиторий по 100 мг
#             1–3 года	11–16 кг	1–2 суппозитория по 100 мг
#             3–10 лет	17–30 кг	1 суппозиторий по 250 мг
#             10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
#              False, None, None, None, None,
#              'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206254/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
#              100, None, 'суппозитории ректальные', None),
#
#             ('Цефекон Д (парацетамол) для детей суппозитории ректальные 250 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
#             Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
#             Возраст	Вес	Разовая доза
#             3–10 лет	17–30 кг	1 суппозиторий по 250 мг
#             10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
#              False, None, None, None, None,
#              'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
#              'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206255/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
#              250, None, 'суппозитории ректальные', None) ]
#
#



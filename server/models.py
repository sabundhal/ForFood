from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()


# Таблица users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_yandex = Column(Integer, default=0)
    yandex_id = Column(Integer, unique=True)

    # Связи
    children = relationship("Child", back_populates="user")
    recipes = relationship("Recipe", back_populates="user")
    ratings = relationship("RecipeRating", back_populates="user")
    reviews = relationship("RecipeReview", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    devices = relationship("KitchenDevice", back_populates="user")
    favorites = relationship("RecipeFavorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    views = relationship("RecipeView", back_populates="user")  # До

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

# Таблица children
class Child(Base):
    __tablename__ = 'children'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    height = Column(Float)
    weight = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="children")

    def __repr__(self):
        return f"<Child(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Таблица recipes
class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    image_url = Column(String)
    video_url = Column(String)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    servings = Column(Integer)
    difficulty = Column(String)
    cuisine = Column(String)
    meal_type = Column(String)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")
    reviews = relationship("RecipeReview", back_populates="recipe")
    tags = relationship("RecipeTag", back_populates="recipe")
    meal_plans = relationship("MealPlanRecipe", back_populates="recipe")
    device_settings = relationship("RecipeDeviceSetting", back_populates="recipe")
    translations = relationship("Translation", back_populates="recipe")
    views = relationship("RecipeView", back_populates="recipe")
    favorites = relationship("RecipeFavorite", back_populates="recipe")

    def __repr__(self):
        return f"<Recipe(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Таблица ingredients
class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_allergen = Column(Boolean, default=False)

    # Связи
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name={self.name})>"

# Таблица recipe_ingredients
class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity = Column(Float)
    unit = Column(String)
    notes = Column(String)

    # Связи
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return f"<RecipeIngredient(id={self.id}, recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id})>"

# Таблица recipe_ratings
class RecipeRating(Base):
    __tablename__ = 'recipe_ratings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Связи
    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    def __repr__(self):
        return f"<RecipeRating(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"

# Таблица recipe_reviews
class RecipeReview(Base):
    __tablename__ = 'recipe_reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Связи
    recipe = relationship("Recipe", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<RecipeReview(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"

# Таблица categories
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"

# Таблица tags
class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Связи
    recipe_tags = relationship("RecipeTag", back_populates="tag")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"

# Таблица recipe_tags
class RecipeTag(Base):
    __tablename__ = 'recipe_tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)

    # Связи
    recipe = relationship("Recipe", back_populates="tags")
    tag = relationship("Tag", back_populates="recipe_tags")

    def __repr__(self):
        return f"<RecipeTag(id={self.id}, recipe_id={self.recipe_id}, tag_id={self.tag_id})>"

# Таблица meal_plans
class MealPlan(Base):
    __tablename__ = 'meal_plans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Связи
    user = relationship("User", back_populates="meal_plans")
    recipes = relationship("MealPlanRecipe", back_populates="meal_plan")

    def __repr__(self):
        return f"<MealPlan(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Таблица meal_plan_recipes
class MealPlanRecipe(Base):
    __tablename__ = 'meal_plan_recipes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_plan_id = Column(Integer, ForeignKey('meal_plans.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    day = Column(String)
    meal_type = Column(String)

    # Связи
    meal_plan = relationship("MealPlan", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meal_plans")

    def __repr__(self):
        return f"<MealPlanRecipe(id={self.id}, meal_plan_id={self.meal_plan_id}, recipe_id={self.recipe_id})>"

# Таблица kitchen_devices
class KitchenDevice(Base):
    __tablename__ = 'kitchen_devices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)
    settings = Column(String)

    # Связи
    user = relationship("User", back_populates="devices")
    recipe_settings = relationship("RecipeDeviceSetting", back_populates="device")

    def __repr__(self):
        return f"<KitchenDevice(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Таблица recipe_device_settings
class RecipeDeviceSetting(Base):
    __tablename__ = 'recipe_device_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('kitchen_devices.id'), nullable=False)
    settings = Column(String)

    # Связи
    recipe = relationship("Recipe", back_populates="device_settings")
    device = relationship("KitchenDevice", back_populates="recipe_settings")

    def __repr__(self):
        return f"<RecipeDeviceSetting(id={self.id}, recipe_id={self.recipe_id}, device_id={self.device_id})>"

# Таблица translations
class Translation(Base):
    __tablename__ = 'translations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    language_code = Column(String, nullable=False)
    translated_name = Column(String, nullable=False)
    translated_description = Column(Text)

    # Связи
    recipe = relationship("Recipe", back_populates="translations")

    def __repr__(self):
        return f"<Translation(id={self.id}, recipe_id={self.recipe_id}, language_code={self.language_code})>"

# Таблица recipe_views
class RecipeView(Base):
    __tablename__ = 'recipe_views'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    viewed_at = Column(DateTime, default=func.now())

    # Связи
    recipe = relationship("Recipe", back_populates="views")
    user = relationship("User", back_populates="views")

    def __repr__(self):
        return f"<RecipeView(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"

# Таблица recipe_favorites
class RecipeFavorite(Base):
    __tablename__ = 'recipe_favorites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    favorited_at = Column(DateTime, default=func.now())

    # Связи
    recipe = relationship("Recipe", back_populates="favorites")
    user = relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<RecipeFavorite(id={self.id}, recipe_id={self.recipe_id}, user_id={self.user_id})>"

# Таблица notifications
class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Связи
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, message={self.message})>"



class DrugsCategory(Base):
    __tablename__ = 'drugs_categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    # Добавляем отношение к Drug
    drugs = relationship("Drug", back_populates="category")

class CalculationHistory(Base):
    __tablename__ = 'calculation_history'
    id = Column(Integer, primary_key=True)
    calculation_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    drug_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    drug_name = Column(String)
    username = Column(String)
    weight = Column(Float, nullable=False)
    dosage_mls = Column(Float)
    dosage_mgs = Column(Float)
    totalMgs = Column(Float)
    totalhigh = Column(Float)
    totalhighsachets = Column(Float)
    maximumMgsPerDay = Column(Float)
    highMgs = Column(Float)
    loading_dose = Column(Integer)
    strep_drug = Column(Integer)
    suppositories_high = Column(String)
    suppositories_min = Column(String)
    calculation_type = Column(String)
    calculation_status = Column(String)
    calculation_version = Column(String)
    patient_id = Column(Integer)
    patient_name = Column(String)
    error_message = Column(String)
    calculation_time = Column(DateTime, default=datetime.now)
    age = Column(Float)

class Drug(Base):
    __tablename__ = 'drugs'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('drugs_categories.category_id'))
    name = Column(String, unique=True)
    tablet_only = Column(Integer)
    mls_var = Column(Float)
    mgs_var = Column(Float)
    number_of_times_a_day = Column(String)
    mls_max = Column(Float)
    mgs_max = Column(Float)
    loading_dose = Column(Integer)
    mls_var_loading = Column(Float)
    mgs_var_loading = Column(Float)
    mls_max_loading = Column(Float)
    mgs_max_loading = Column(Float)
    instructions = Column(String)
    nzf_link = Column(String)
    high_range = Column(Integer)
    high_modifier = Column(Float)
    mls_max_high = Column(Float)
    mgs_max_high = Column(Float)
    strep_drug = Column(Integer)
    strep_frequency = Column(String)
    mls_var_strep = Column(Float)
    mgs_var_strep = Column(Float)
    mls_strep_max = Column(Float)
    mgs_strep_max = Column(Float)
    weight_cutoff_1 = Column(Float)
    weight_cutoff_2 = Column(Float)
    range1_dose = Column(Float)
    range2_dose = Column(Float)
    form = Column(String)
    age_range = Column(Float)
    category = relationship("DrugsCategory", back_populates="drugs")

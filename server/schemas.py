from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class ChildCreate(BaseModel):
    name: str = Field(..., example="Иван")
    birth_date: date = Field(..., example="2020-01-01")
    gender: str = Field(..., example="male")
    height: Optional[float] = Field(None, example=90.5)
    weight: Optional[float] = Field(None, example=14.2)

    @validator("gender")
    def validate_gender(cls, value):
        if value not in ["male", "female"]:
            raise ValueError("Пол должен быть 'male' или 'female'")
        return value

    @validator("height", "weight")
    def validate_positive_values(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Значение должно быть положительным")
        return value
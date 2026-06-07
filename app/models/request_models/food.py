from pydantic import Field, field_validator

from app.models.pydantic_schemas.base import RequestModel


class CreateFoodRequestModel(RequestModel):
    food_type: str
    meal_type: str
    dietary_restriction: str
    mood: str
    additional_notes: str
    token_consumed: float = Field(gt=0)

    @field_validator("additional_notes")
    def validate_additional_notes(cls, value):
        if len(value.split()) > 100:
            raise ValueError("ADDITIONAL_NOTES MUST NOT EXCEED 100 WORDS.")
        return value

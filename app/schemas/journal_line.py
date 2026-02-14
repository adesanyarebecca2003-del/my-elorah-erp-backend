from pydantic import BaseModel, Field, model_validator
from uuid import UUID


class JournalLineCreate(BaseModel):
    account_code: str
    debit: float = Field(default=0)
    credit: float = Field(default=0)

    @model_validator(mode="after")
    def validate_amounts(self):
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Line cannot have both debit and credit")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("Line must have either debit or credit")
        return self


class JournalLinePost(BaseModel):
    account_id: UUID
    debit: float = Field(default=0)
    credit: float = Field(default=0)

    @model_validator(mode="after")
    def validate_amounts(self):
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Line cannot have both debit and credit")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("Line must have either debit or credit")
        return self
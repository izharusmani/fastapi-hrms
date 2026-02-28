from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Literal

class Employee(BaseModel):
    emp_id: str = Field(..., min_length=1, description="Employee ID (required)")
    name: str = Field(..., min_length=1, max_length=100, description="Employee name (required)")
    age: int = Field(..., ge=18, le=70, description="Employee age (18-70)")
    email: EmailStr = Field(..., description="Valid email address (required)")
    department: str = Field(..., min_length=1, max_length=100, description="Department (required)")
    created_at: int = int(datetime.timestamp(datetime.now()))
    updated_at: int = int(datetime.timestamp(datetime.now()))
    
    @validator('emp_id')
    def emp_id_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Employee ID must be alphanumeric')
        return v

class Attendance(BaseModel):
    emp_id: str = Field(..., min_length=1, description="Employee ID (required)")
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="Date in YYYY-MM-DD format (required)")
    status: Literal["Present", "Absent"] = Field(..., description="Attendance status (required)")
    created_at: int = int(datetime.timestamp(datetime.now()))
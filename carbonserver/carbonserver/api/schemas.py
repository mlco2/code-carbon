"""
https://fastapi.tiangolo.com/tutorial/sql-databases/

To avoid confusion between the SQLAlchemy models and the Pydantic models, we will have the file models.py with the SQLAlchemy models, and the file schemas.py with the Pydantic models.

These Pydantic models define more or less a "schema" (a valid data shape).

So this will help us avoiding confusion while using both.
"""

# TODO : Share this file with codecarbon package

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, SecretStr


class EmissionBase(BaseModel):
    timestamp: datetime
    experiment_id: str
    duration: int = Field(
        ..., gt=0, description="The duration must be greater than zero"
    )
    emissions: float = Field(
        ..., gt=0, description="The emissions must be greater than zero"
    )
    energy_consumed: float = Field(
        ..., gt=0, description="The energy_consumed must be greater than zero"
    )
    country_name: Optional[str] = None
    country_iso_code: Optional[str] = None
    region: Optional[str] = None
    on_cloud: bool
    cloud_provider: Optional[str] = None
    cloud_region: Optional[str] = None

    class Config:
        # orm_mode = True
        schema_extra = {
            "example": {
                "timestamp": "2021-04-04T08:43:00+02:00",
                "experiment_id": "40088f1a-d28e-4980-8d80-bf5600056a14",
                "duration": 98745,
                "emissions": 1.548444,
                "energy_consumed": 57.21874,
                "country_name": "France",
                "country_iso_code": "FRA",
                "region": "france",
                "on_cloud": True,
                "cloud_provider": "aws",
                "cloud_region": "eu-west-1a",
            }
        }


class EmissionCreate(EmissionBase):
    pass


class Emission(EmissionBase):
    id: int


# Experiment
class ExperimentBase(BaseModel):
    timestamp: datetime
    name: str
    description: str
    is_active: bool
    project_id: int


class ExperimentCreate(ExperimentBase):
    pass


class Experiment(ExperimentBase):
    id: int
    emissions: List[Emission] = []


# Project
class ProjectBase(BaseModel):
    name: str
    description: str
    team_id: int


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    experiments: List[Experiment] = []


# Team
class TeamBase(BaseModel):
    name: str
    description: str
    organization_id: int


class TeamCreate(TeamBase):
    pass


class Team(TeamBase):
    id: int
    projects: List[Project] = []


# Organization
class OrganizationBase(BaseModel):
    name: str
    description: str


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    teams: List[Team] = []


# User
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    name: str
    password: str
    is_active: bool


class User(UserBase):
    id: int
    name: str
    email: EmailStr
    password: SecretStr
    api_key: str
    is_active: bool

    class Config:
        orm_mode = False

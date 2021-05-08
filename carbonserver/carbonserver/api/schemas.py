"""
https://fastapi.tiangolo.com/tutorial/sql-databases/

To avoid confusion between the SQLAlchemy models and the Pydantic models, we will have the file models.py with the SQLAlchemy models, and the file schemas.py with the Pydantic models.

These Pydantic models define more or less a "schema" (a valid data shape).

So this will help us avoiding confusion while using both.
"""

# TODO : Move this file in codecarbon package ?
# TODO : move is_active from Experiment to Run

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EmissionBase(BaseModel):
    timestamp: datetime
    run_id: str
    duration: int = Field(
        ..., gt=0, description="The duration must be greater than zero"
    )
    emissions: float = Field(
        ..., gt=0, description="The emissions must be greater than zero"
    )
    energy_consumed: float = Field(
        ..., gt=0, description="The energy_consumed must be greater than zero"
    )

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2021-04-04T08:43:00+02:00",
                "run_id": "40088f1a-d28e-4980-8d80-bf5600056a14",
                "duration": 98745,
                "emissions": 1.548444,
                "energy_consumed": 57.21874,
            }
        }


class EmissionCreate(EmissionBase):
    pass


class Emission(EmissionBase):
    id: int


# Run
class RunBase(BaseModel):
    timestamp: datetime
    experiment_id: str

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2021-04-04T08:43:00+02:00",
                "experiment_id": "1",
            }
        }


class RunCreate(RunBase):
    pass


class Run(RunBase):
    id: int


# Experiment
class ExperimentBase(BaseModel):
    timestamp: datetime
    name: str
    description: str
    is_active: bool
    country_name: Optional[str] = None
    country_iso_code: Optional[str] = None
    region: Optional[str] = None
    on_cloud: bool
    cloud_provider: Optional[str] = None
    cloud_region: Optional[str] = None
    project_id: int

    class Config:
        # orm_mode = True
        schema_extra = {
            "example": {
                "name": "Run on AWS",
                "description": "AWS API for Code Carbon",
                "is_active": True,
                "timestamp": "2021-04-04T08:43:00+02:00",
                "country_name": "France",
                "country_iso_code": "FRA",
                "region": "france",
                "on_cloud": True,
                "cloud_provider": "aws",
                "cloud_region": "eu-west-1a",
                "project_id": "1",
            }
        }


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

    class Config:
        schema_extra = {
            "example": {
                "name": "API Code Carbon",
                "description": "API for Code Carbon",
                "team_id": "1",
            }
        }


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

    class Config:
        schema_extra = {
            "example": {
                "name": "Data For Good",
                "description": "Data For Good France",
                "organization_id": "1",
            }
        }


class TeamCreate(TeamBase):
    pass


class Team(TeamBase):
    id: int
    projects: List[Project] = []


# Organization
class OrganizationBase(BaseModel):
    name: str
    description: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Code Carbon",
                "description": "Save the world, one run at a time.",
            }
        }


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    teams: List[Team] = []


# User
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

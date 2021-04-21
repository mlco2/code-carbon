# read https://fastapi.tiangolo.com/tutorial/sql-databases/


# Put here the structure of the database
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .database import Base


class Emission(Base):
    __tablename__ = "emissions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    # experiment_id = Column(Integer)
    duration = Column(Float)
    emissions = Column(Float)
    energy_consumed = Column(Float)
    country_name = Column(String)
    country_iso_code = Column(String)
    region = Column(String)
    on_cloud = Column(Boolean, default=False)
    cloud_provider = Column(String)
    cloud_region = Column(String)
    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    experiment = relationship("Experiment", back_populates="emissions")


# Un experiment = un run
class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    name = Column(String)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    emissions = relationship("Emission", back_populates="experiment")
    project = relationship("Project", back_populates="experiments")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))
    experiments = relationship("Experiment", back_populates="project")
    team = relationship("Team", back_populates="projects")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    projects = relationship("Project", back_populates="team")
    organization = relationship("Organization", back_populates="teams")


# Organization
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    teams = relationship("Team", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    # TODO: Associate user with his entities

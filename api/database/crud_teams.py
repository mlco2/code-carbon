# from uuid import uuid4 as uuid
from . import models, schemas
from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the project data

"""


def save_team(db: Session, team: schemas.TeamCreate):
    # TODO : save Team in database and get her ID
    db_team = models.Team(
       name=team.name,
        description=team.description,
        team_id=team.team_id,
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def get_one_Team(team_id):
    # TODO : find the Team in database and return it

    return


def get_Project_from_Teams(team_id):
    # TODO : get Projects from Project id in database
    return

from typing import List

from carbonserver.api.domain.organization import Organization
from carbonserver.database import models, schemas

from sqlalchemy.orm import Session

# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

"""
Here there is all the method to manipulate the project data
"""


class SqlAlchemyRepository(Organization):
    def __init__(self, db: Session):
        self.db = db

    def save_organization(self, organization: schemas.OrganizationCreate):
        # TODO : save Organization in database and get her ID
        db_organization = models.Organization(
            name=organization.name, description=organization.description
        )
        self.db.add(db_organization)
        self.db.commit()
        self.db.refresh(db_organization)
        return db_organization

    def get_one_organization(self, organization_name: str):
        # TODO : find the Organization in database and return it
        pass

    def get_team_from_organizations(self, organization_name: str):
        # TODO : get Organization from team id in database
        pass


class InMemoryRepository(Organization):
    def __init__(self):
        self.organizations: List = []
        self.id: int = 0

    def save_organization(self, organization: schemas.OrganizationCreate):
        self.organizations.append(
            models.Experiment(
                id=self.id + 1,
                name=organization.name,
                description=organization.description,
            )
        )

    def get_one_organization(self, organization_name: str) -> schemas.Organization:
        organization = self.organizations[0]
        return schemas.Organization(
            id=organization.id,
            name=organization.name,
            description=organization.description,
        )

    def get_team_from_organizations(self, organization_name: str):
        organizations = []
        for organization in self.organizations:
            organizations.append(
                schemas.Organization(
                    id=organization.id,
                    name=organization.name,
                    description=organization.description,
                )
            )
        return organizations

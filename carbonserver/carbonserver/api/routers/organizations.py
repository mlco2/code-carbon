from carbonserver.database.schemas import OrganizationCreate
from carbonserver.api.infra.repositories.repository_organization import (
    SqlAlchemyRepository,
)
from carbonserver.api.dependencies import get_db, get_token_header
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter(
    dependencies=[Depends(get_token_header)],
)


organizations_temp_db = []


@router.put("/organization", tags=["organizations"])
def add_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    repository_organizations = SqlAlchemyRepository(db)
    repository_organizations.save_organization(organization)
    # TODO : return the id of the organization


@router.get("/organization/{organization_id}", tags=["organizations"])
async def read_organization(
    organization_id: str = Path(..., title="The ID of the organization to get")
):
    # TODO : call get_one_organization(organization_id)
    # organization = crud_organizations.get_one_organization(organization_id)
    # if organization_id is False:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # return organization
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/organizations/{organization_id}", tags=["organizations"])
async def read_teams_organizations(
    team_id: str = Path(..., title="The ID of the team to get")
):
    # team_organizations = crud_organizations.get_Team_from_Organizations(team_id)
    # # Remove next line when DB work
    # team_organizations = organizations_temp_db
    # return team_organizations
    raise HTTPException(status_code=501, detail="Not Implemented")

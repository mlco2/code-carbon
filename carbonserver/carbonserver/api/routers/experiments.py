from carbonserver.database.schemas import ExperimentCreate
from carbonserver.api.dependencies import get_db, get_token_header
from carbonserver.api.infra.repositories.repository_experiment import (
    SqlAlchemyRepository,
)

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter(
    dependencies=[Depends(get_token_header)],
)


@router.put("/experiment", tags=["experiments"])
def add_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    # crud_experiments.save_experiment(db, experiment)
    repository_experiment = SqlAlchemyRepository(db)
    repository_experiment.save_experiment(experiment)
    
    raise HTTPException(status_code=404, detail="Not Found")


@router.get("/experiment/{experiment_id}", tags=["experiments"])
async def read_experiment(
    experiment_id: str = Path(..., title="The ID of the experiment to get")
):
    # experiment = crud_experiments.get_one_experiment(experiment_id)
    # if experiment_id is False:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # return experiment
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/experiments/{experiment_id}", tags=["experiments"])
async def read_experiment_experiments(
    experiment_id: str = Path(..., title="The ID of the experiment to get")
):
    # experiment_experiments = crud_experiments.get_experiments_from_experiment(
    #     experiment_id
    # )
    # return experiment_experiments
    raise HTTPException(status_code=501, detail="Not Implemented")

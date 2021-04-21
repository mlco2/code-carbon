from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_token_header, get_db
from database import crud_experiments
from database.schemas import ExperimentCreate


router = APIRouter(
    dependencies=[Depends(get_token_header)],
)


@router.put("/experiment", tags=["experiments"])
def add_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    crud_experiments.save_experiment(db, experiment)


@router.get("/experiment/{experiment_id}", tags=["experiments"])
async def read_experiment(
    experiment_id: str = Path(..., title="The ID of the experiment to get")
):
    experiment = crud_experiments.get_one_experiment(experiment_id)
    if experiment_id is False:
        raise HTTPException(status_code=404, detail="Item not found")
    return experiment


@router.get("/experiments/{experiment_id}", tags=["experiments"])
async def read_experiment_experiments(
    experiment_id: str = Path(..., title="The ID of the experiment to get")
):
    experiment_experiments = crud_experiments.get_experiments_from_experiment(
        experiment_id
    )
    return experiment_experiments

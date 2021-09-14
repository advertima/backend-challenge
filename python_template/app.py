import models

from fastapi import FastAPI, Response, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": "Timeline API"}


@app.post("/enter_event")
def enter_event(db: Session = Depends(get_db)):
    # TODO: implementation
    return {}


@app.post("/exit_event")
def exit_event(db: Session = Depends(get_db)):
    # TODO: implementation
    return {}


@app.get("/timeline/{tracking_id}")
def timeline(tracking_id: str, db: Session = Depends(get_db)):
    # TODO: implementation
    return []

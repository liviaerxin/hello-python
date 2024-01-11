from typing import List

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy import event, DDL


class Point(BaseModel):
    x: int
    y: int


class NoteIn(BaseModel):
    text: str
    completed: bool
    data: Point


class Note(BaseModel):
    id: int
    text: str
    completed: bool
    data: Point


# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
    sqlalchemy.Column("data", sqlalchemy.JSON),
)


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(notes, "after_create")
def after_create_notes(target, connection, **kw):
    connection.execute(
        notes.insert(),
        NoteIn(text="abc", completed=True, data=Point(x=31, y=92)).dict(),
    )
    connection.execute(
        notes.insert(),
        NoteIn(text="csy", completed=True, data=Point(x=11, y=32)).dict(),
    )


metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes/", response_model=List[Note])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)


@app.post("/notes/", response_model=Note)
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

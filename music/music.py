from fastapi import FastAPI, HTTPException,  Header, Response, Depends
from pydantic import BaseModel, Field
import secrets
from itertools import count
from typing import List, Optional
from fastapi import Query


app = FastAPI()

registered_users = {}
tracks_by_id_ = {}
track_id_counter = count(start=1)

class RegisterUserRequest(BaseModel):
    name: str = Field(..., description="Имя пользователя")
    age: int = Field(..., description="Возраст пользователя", ge=0)

class RegisterUserResponse(BaseModel):
    token: str


class AddTrackRequest(BaseModel):
    name: str = Field(..., description="Название трека")
    artist: str = Field(..., description="Исполнитель")
    year: Optional[int] = Field(None, description="Год выпуска трека")
    genres: Optional[List[str]] = Field(list(), description="Жанры трека")

class AddTrackResponse(BaseModel):
    track_id: int

def validate_token(x_token: str = Header(None)):
    if not x_token:
        raise HTTPException(status_code=401, detail="Missing token")
    if x_token not in registered_users:
        raise HTTPException(status_code=401, detail="Incorrect token")
    return x_token

@app.post("/api/v1/registration/register_user")
def register_user(request: RegisterUserRequest):
    token = secrets.token_hex(20)

    registered_users[token] = {
        "name": request.name,
        "age": request.age
    }

    return RegisterUserResponse(token=token)


@app.post("/api/v1/tracks/add_track", response_model=AddTrackResponse, status_code=201)
def add_track(request: AddTrackRequest, token: str = Depends(validate_token)):
    track_id = next(track_id_counter)
    tracks_by_id_[track_id] = {
        "name": request.name,
        "artist": request.artist,
        "year": request.year,
        "genres": request.genres
    }
    return AddTrackResponse(track_id=track_id)

@app.delete("/api/v1/tracks/{track_id}")
def delete_track(track_id: int, token: str = Depends(validate_token)):
    if track_id not in tracks_by_id_:
        raise HTTPException(status_code=404, detail="Invalid track_id")
    del tracks_by_id_[track_id]
    return {"status": "track removed"}

@app.get("/api/v1/tracks/search")
def search_tracks(
    token: str = Depends(validate_token),
    name: Optional[str] = Query(None, description="Название трека"),
    artist: Optional[str] = Query(None, description="Исполнитель")
):
    validate_token(token)
    if name is None and artist is None:
        raise HTTPException(status_code=422, detail="You should specify at least one search argument")

    matching_ids = [
        track_id
        for track_id, track in tracks_by_id_.items()
        if (name and name.lower() in track["name"].lower()) or
           (artist and artist.lower() in track["artist"].lower())
    ]

    return {"track_ids": matching_ids}

@app.get("/api/v1/tracks/all", status_code=200)
def get_all_tracks(token: str = Depends(validate_token)):

    return [
        {"name": track["name"], "artist": track["artist"], "year": track["year"], "genres": track["genres"]}
        for track in tracks_by_id_.values()
    ]

@app.get("/api/v1/tracks/{track_id}")
def get_track(track_id: int, token: str = Depends(validate_token)):
    validate_token(token)
    if track_id not in tracks_by_id_:
        raise HTTPException(status_code=404, detail="Invalid track_id")

    return {"name": tracks_by_id_[track_id]["name"], "artist": tracks_by_id_[track_id]["artist"]}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
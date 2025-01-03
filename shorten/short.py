from fastapi import FastAPI, Path
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import List, Union, Optional
import uvicorn
import random
import string

class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None


class Shorted(BaseModel):

   url: str = Field(..., title="Url")
   key: str = Field(..., title="Key")



class ToShort(BaseModel):
    url: str = Field(..., title="Url")

app = FastAPI(
    title='FastAPI',
    version='0.1.0'
)

url_store = {
    "ed1De1": "https://example.com",
    "abc123": "https://google.com"
}

url_store_reverse = {}
urls = []

def get_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

@app.post("/shorten", summary="Short Url", response_model=Shorted, status_code=201)
async def short_url(to_short: ToShort):
    if to_short.url not in urls:
        urls.append(to_short.url)
        key = get_key()
        url_store[key] = to_short.url
        url_store_reverse[to_short.url] = key
        resp = Shorted(url=to_short.url, key=key)
    else:
        resp = Shorted(url=to_short.url, key=url_store_reverse[to_short.url])
    return resp

@app.get(
    "/go/{key}",
    summary="Redirect To Url",
    status_code=307,
    responses={
        307: {
            "description": "Successful Response",
            "content": {"application/json": {"schema": {}}}
        }})
async def redirect_to_url(key: str = Path(..., title="Key")):
    if key not in url_store:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=url_store[key], status_code=307)

def main():
    uvicorn.run(app)

if __name__ == "__main__":
    main()

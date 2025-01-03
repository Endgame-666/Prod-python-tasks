from fastapi import FastAPI, Request
from datetime import datetime
from middleware import jwt_middleware
from auth import router as auth_router
from middleware import rate_limiter_middleware

app = FastAPI()


app.middleware("http")(rate_limiter_middleware)
@app.middleware("http")
async def jwt_middleware_app(request: Request, call_next):
    return await jwt_middleware(request, call_next)

# Include auth router
app.include_router(auth_router)

@app.get("/api/protected")
async def protected_route(request: Request):
    username = request.state.username
    exp_time = request.state.exp
    
    remaining_time = exp_time - datetime.now()
    remaining_minutes = remaining_time.total_seconds() / 60
    
    return {
        "message": f"Hi, {username}, your token is valid for next {remaining_minutes:.2f} minutes!"
    }
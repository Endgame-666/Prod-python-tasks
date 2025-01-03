from fastapi import Request, Response
from datetime import datetime, timedelta
import jwt
from config import settings
from collections import defaultdict
import time
from main import app
# In-memory storage for rate limiting
request_counts = defaultdict(list)
RATE_LIMIT = 5
RATE_LIMIT_PERIOD = 2  # seconds


def rate_limiter_reset():
    global request_counts
    request_counts = defaultdict(list)


async def jwt_middleware(request: Request, call_next):
    if request.url.path in ["/auth/token", "/docs", "/openapi.json"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(content="Missing or invalid authorization header", status_code=401)

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        request.state.username = payload["sub"]
        request.state.exp = datetime.fromtimestamp(payload["exp"])
    except jwt.ExpiredSignatureError:
        return Response(content='Invalid or expired token', status_code=401)
    except jwt.InvalidTokenError:
        return Response(content='Invalid or expired token', status_code=401)
    except Exception as e:
        return Response(content=f"Unexpected error: {str(e)}", status_code=500)

    return await call_next(request)


@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    # Filter timestamps to only keep those within the sliding window
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts[client_ip]
        if timestamp > current_time - RATE_LIMIT_PERIOD
    ]

    # Check the rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        reset_time = int(RATE_LIMIT_PERIOD - (current_time - min(request_counts[client_ip])))
        headers = {
            "X-RateLimit-Limit": str(RATE_LIMIT),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
        }
        return Response(
            content=f"Rate limit exceeded. Try again in {reset_time} seconds",
            status_code=429,
            headers=headers
        )

    # Record the current request timestamp
    request_counts[client_ip].append(current_time)

    # Prepare rate limit headers
    remaining = RATE_LIMIT - len(request_counts[client_ip])
    headers = {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(RATE_LIMIT_PERIOD)),
    }

    # Process the request
    response = await call_next(request)
    for key, value in headers.items():
        response.headers[key] = value

    return response
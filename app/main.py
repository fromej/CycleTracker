import os

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.auth import create_access_token, SECRET_KEY, ALGORITHM
from app.crud import get_user_by_username, get_user_by_email, create_user, authenticate_user, get_user_events, \
    analyze_cycle_patterns, get_event_statistics, create_user_event
from app.models import User
from app.schemas import UserCreate, MenstrualEventCreate

from app.database import get_db

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join("templates"))

def get_bearer_token(request: Request):
    print("Checking Authorization Header manually")

    authorization: str = request.headers.get("Authorization")
    if not authorization:
        print("No Authorization header found")
        return None

    if not authorization.startswith("Bearer "):
        print("Authorization header doesn't start with Bearer")
        return None

    token = authorization.split(" ", 1)[1]
    print(f"Token found: {token}")
    return token


def get_token_from_request(
        request: Request,
        token: str = Depends(get_bearer_token)
) -> str:
    # print('get here')
    # # Check if token is present in the "Authorization" header
    # if token:
    #     print('returing token')
    #     return token

    # If no token in header, check for a cookie
    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        print('returning cookie')
        return token_cookie

    # If neither, raise an exception
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(get_token_from_request), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return create_user(db=db, user=user)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    print('logging in')
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    events = get_user_events(db, current_user.id)
    cycle_analysis = analyze_cycle_patterns(db, current_user.id)
    event_stats = get_event_statistics(db, current_user.id)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": {"id": current_user.id, "username": "ilona"},
        "events": events,
        "cycle_analysis": cycle_analysis,
        "event_stats": event_stats
    })


@app.post("/events")
async def create_event(
        event: MenstrualEventCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return create_user_event(db, event, current_user.id)


@app.get("/events/calendar")
async def get_calendar_events(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    events = get_user_events(db, current_user.id)

    calendar_events = [
        {
            "title": f"{event.event_type.value}: {event.event_value or ''}",
            "start": event.event_date.isoformat(),
            "allDay": True,
            "className": event.event_type.value.lower().replace(" ", "-")
        } for event in events
    ]

    return calendar_events


# Additional optional endpoints for analytics
@app.get("/events/statistics")
async def get_statistics(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    event_stats = get_event_statistics(db, current_user.id)
    cycle_analysis = analyze_cycle_patterns(db, current_user.id)

    return {
        "event_stats": event_stats,
        "cycle_analysis": cycle_analysis
    }

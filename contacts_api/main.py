from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi_limiter.depends import RateLimiter

from src.db.db import get_db
from src.routes import contacts, auth, users
from limiter import setup_limiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the whole application,
    like database connections or caches.
    
    :return: A coroutine, which means it's a function that
    """
    await setup_limiter()


@app.get("/", dependencies=[Depends(RateLimiter(times=3, seconds=5))])
async def root():
    """
    The root function returns a JSON object with the message &quot;Hi! I am FastAPI applicataion!&quot;
    
    
    :return: A dict, which is converted to a json response
    """
    return {"message": "Hi! I am FastAPI applicataion!"}


@app.get('/api/healthchecker')
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check if the database is correctly configured.
    It will return a 500 error code if something goes wrong, otherwise it will return a 200 OK.
    
    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database configured is not correctly!")
        return {"message": "Database correctly working!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
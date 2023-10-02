import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from main import app
from src.db.models import Base
from src.db.db import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    """
    The session function is a fixture that creates a new database session for
    a test to use. It's useful whenever you have code that uses the database,
    such as when testing models or API routes. The session function returns a 
    SessionLocal class instance, which provides access to the open database 
    session.
    
    :return: A testsessionlocal object
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session):
    """
    The client function is a fixture that creates an application instance
    for each test. The app instance is created with the testing configuration,
    and it has a context manager to handle database connections and sessions.
    The client function returns a TestClient object, which allows you to make HTTP requests in tests.

    :param session: Pass the database session to the client function
    :return: A test client that can be used to make requests
    """

    def override_get_db():
        """
        The override_get_db function is a fixture that allows us to override the get_db function
            in our app.py file so that we can use it with pytest. The yield statement will return the session object,
            and then close it when we are done using it.
        
        :return: A generator
        """
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """
    The user function returns a dictionary with the following keys:
        username, email, password.
    
    
    :return: A dictionary with the user details
    """
    return  {"username": "michail", "email": "michail_mayers@main.com", "password": "qwerty123"}
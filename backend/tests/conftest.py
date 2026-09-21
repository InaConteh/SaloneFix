import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db.session import Base, get_db
from app.db.init_db import init_db
from app.core.security import create_access_token
from app.models.entities import User
from app.models.enums import UserRole
from main import app

# Test database with StaticPool so all connections share the same in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # The limiter is in-process and keyed by client IP; every test shares the
    # TestClient address, so isolate tests from each other.
    from app.core.dependencies import _rate_limit_cache
    _rate_limit_cache.clear()
    yield
    _rate_limit_cache.clear()


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    init_db(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def citizen_token(db_session):
    user = db_session.query(User).filter(User.contact == "citizen@freetown.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})


@pytest.fixture
def moderator_token(db_session):
    user = db_session.query(User).filter(User.contact == "moderator@salonefix.gov.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})


@pytest.fixture
def officer_token(db_session):
    user = db_session.query(User).filter(User.contact == "officer.fcc@salonefix.gov.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})


@pytest.fixture
def slra_officer_token(db_session):
    user = db_session.query(User).filter(User.contact == "officer.slra@salonefix.gov.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})


@pytest.fixture
def admin_token(db_session):
    user = db_session.query(User).filter(User.contact == "admin@salonefix.gov.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})


@pytest.fixture
def auditor_token(db_session):
    user = db_session.query(User).filter(User.contact == "auditor@salonefix.gov.sl").first()
    return create_access_token({"sub": user.id, "role": user.role.value})

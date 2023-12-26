from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.db_url1,
)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

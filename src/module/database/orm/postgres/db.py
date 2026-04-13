from src.module.database.orm.postgres.models.base_model import BasePostgresModel
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine


class PostgresDB:

    def __init__(self, connection_url: str):
        if connection_url is None:
            raise ValueError('Missed required parameter [connection_url]')
        self._connection_url = connection_url
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        if self._engine is None:
            if not self._connection_url.startswith("postgres"):
                raise ValueError(f"Expected Postgres Connection URL, got: {self._connection_url}")

            self._engine = create_engine(self._connection_url)

        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = sessionmaker(self.engine)

        return self._session_factory

    def create_tables(self):
        BasePostgresModel.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.session_factory()

        # try:
        #     yield session
        #     session.commit()
        # except Exception:
        #     session.rollback()
        #     raise
        # finally:
        #     session.close()

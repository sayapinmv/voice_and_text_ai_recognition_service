from sqlalchemy.orm import DeclarativeBase


class BasePostgresModel(DeclarativeBase):
    # Можно написать базовые настройки
    # Этот класс хранит все модели, которые отнаследовались от него
    pass

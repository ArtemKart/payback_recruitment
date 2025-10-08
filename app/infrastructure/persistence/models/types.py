from datetime import datetime, timezone
from sqlalchemy import TypeDecorator, DateTime


class AwareDateTime(TypeDecorator):
    """
    SQLAlchemy type that:
    - Stores datetime as naive UTC in SQLite
    - Returns timezone-aware UTC datetime when reading
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
        return value

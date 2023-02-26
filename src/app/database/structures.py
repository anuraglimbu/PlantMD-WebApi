from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Table,
    MetaData
)
from sqlalchemy.sql import func

metadata = MetaData()

# inferences = Table(
#     "inferences",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("titles", String(50)),
#     Column("description", String(50), default=None, nullable=True),
#     Column("created_date", DateTime, default=func.now(), nullable=False),
# )
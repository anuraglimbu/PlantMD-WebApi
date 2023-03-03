from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Table,
    MetaData
)
from sqlalchemy.sql import func

metadata = MetaData()

verification_tokens = Table(
    "verification_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String(100),unique=True, nullable=False),
    Column("name", String(20)),
    Column("user_id", Integer, nullable=True),
    Column("disabled", Boolean, default=False, nullable=False),
    Column("created_date", DateTime, default=func.now(), nullable=False)
)

identifiers = Table(
    "identifiers",
    metadata,
    Column("identifier", String(100), primary_key=True),
    Column("verification_token_id", Integer, nullable=False),
    Column("disabled", Boolean, default=False, nullable=False),
    Column("created_date", DateTime, default=func.now(), nullable=False)
)

#INSERT INTO verification_tokens(token, name, disabled, created_date) VALUES ('517ed0198f0c32ff520348be', 'Test Token', 'f', '2023-03-04 00:21:21.748045');
#INSERT INTO identifiers(identifier, verification_token_id, disabled, created_date) VALUES ('3759c4aa', 1, 'f', '2023-03-04 00:21:21.748045');

# inferences = Table(
#     "inferences",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("identifier_id", String(100)),
#     Column("original_filename", String(50)),
#     Column("result_filename", String(50), nullable=True),
#     Column("created_date", DateTime, default=func.now(), nullable=False),
# )
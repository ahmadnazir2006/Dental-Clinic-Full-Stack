
from database import engine
from models import Patient

print("Model table name:", Patient.__tablename__)
print("Database engine:", engine.url.get_backend_name())
print("Patient columns:")

for column in Patient.__table__.columns:
    print(column.name, column.type)
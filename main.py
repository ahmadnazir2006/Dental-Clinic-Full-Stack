from fastapi import FastAPI

from routers import auth, patients, appointments, users


app = FastAPI()
app = FastAPI(
    title="Dental Clinic API",
    description="Backend API for managing dental clinic patients, appointments, users, and authentication.",
    version="1.0.0"
)
@app.get("/")
def root():
    return {
        "message": "Dental Clinic API is running"
    }
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(users.router)
app.include_router(auth.router)







    







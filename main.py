from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, patients, appointments, users



app = FastAPI(
    title="Dental Clinic API",
    description="Backend API for managing dental clinic patients, appointments, users, and authentication.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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







    







import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes.exam_routes import router as exam_router
from app.core.database import Base, engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="Question Paper Generator API",
    description="API for generating exam questions using Gemini AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(exam_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Question Paper Generator API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
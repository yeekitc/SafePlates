import logging
from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional, Dict
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from models import NewUser, User
import os
from datetime import datetime, timedelta, timezone
import bcrypt
from jwt import PyJWTError, decode, encode

# Google Maps API imports
from google_maps_api import search_restaurants_api

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables")
client = AsyncIOMotorClient(MONGO_URI)
db = client["sample_mflix"]

movies_collection = db["movies"]
users_collection = db["users"]

# AWS S3
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def movie_serializer(movie: Dict) -> Dict:
    return {
        "id": str(movie["_id"]),
        "title": movie.get("title"),
        "year": movie.get("year"),
        "cast": movie.get("cast"),
        "plot": movie.get("plot"),
    }

@app.post("/test-upload")
async def test_upload():
    try:
        # Path to your test image in assets
        image_path = "test.png"  # adjust path as needed
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test-uploads/{timestamp}_test-image.jpg"

        # Upload to S3
        s3_client.upload_file(
            image_path,
            AWS_BUCKET_NAME,
            filename,
            ExtraArgs={
                "ContentType": "image/"
            }
        )

        # Generate public URL
        image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
        return {"message": "Test image uploaded successfully", "image_url": image_url}

    except Exception as e:
        print(f"Error uploading image: {e}")  # For debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/{movie_id}")
async def get_movie(movie_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie_serializer(movie)
    except Exception as e:
        logging.error(f"Error fetching movie by ID {movie_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid movie ID")

@app.get("/movies/search/")
async def search_movies(title: str, limit: int = 10):
    try:
        cursor = movies_collection.find({"title": {"$regex": title, "$options": "i"}}).limit(limit)
        movies = await cursor.to_list(length=limit)
        return [movie_serializer(movie) for movie in movies]
    except Exception as e:
        logging.error(f"Error searching movies with title '{title}': {e}")
        raise HTTPException(status_code=500, detail="Error searching movies")

@app.get("/movies/")
async def list_movies(limit: int = 10):
    try:
        cursor = movies_collection.find().limit(limit)
        movies = await cursor.to_list(length=limit)
        return [movie_serializer(movie) for movie in movies]
    except Exception as e:
        logging.error(f"Error listing movies: {e}")
        raise HTTPException(status_code=500, detail="Error listing movies")



@app.post("/sign_up")
async def sign_up(new_user: NewUser):
    user_exist = await users_collection.find_one({"email": new_user.email})
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(new_user.password)

    user_data = {
        "name": new_user.name,
        "email": new_user.email,
        "password": hashed_password
    }

    await users_collection.insert_one(user_data)
    
    return {"message": "New user created successfully"}

@app.post("/login")
async def login(user_login: User):
    user = await users_collection.find_one({"email": user_login.email})
    if user and verify_password(user_login.password, user["password"]):
        access_token = create_access_token(data={"sub": user["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid email or password")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    

@app.get("/protected-route/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['name']}! This is a protected route."}

@app.get("/restaurants/search/")
async def search_restaurants(town: str, name: str, limit: int = 10):
    try:
        results = await search_restaurants_api(town, name)
        return results
    except Exception as e:
        logging.error(f"Error searching restaurants with name '{name}' in town '{town}': {e}")
        raise HTTPException(status_code=500, detail="Error searching restaurants") 

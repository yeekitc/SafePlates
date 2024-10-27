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
# db = client["sample_mflix"]
db = client["restaurant_allergy"]

# movies_collection = db["movies"]
# users_collection = db["users"]
restaurants_collection = db["restaurants"]
reviews_collection = db["reviews"]
dishes_collection = db["dishes"]
users_collection = db["users"]

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


# Serializers
####################################################
def restaurant_serializer(restaurant: Dict) -> Dict:
    return {
        "id": str(restaurant["_id"]),
        "name": restaurant.get("name"),
        "google_data": {
            "place_id": restaurant["google_data"].get("place_id"),
            "rating": restaurant["google_data"].get("rating"),
            "priceLevel": restaurant["google_data"].get("priceLevel"),
            "reviews": restaurant["google_data"].get("reviews"),
            "address": restaurant["google_data"].get("address"),
            "nationalPhoneNumber": restaurant["google_data"].get("nationalPhoneNumber")
        },
        "menu": [str(dish_id) for dish_id in restaurant.get("menu", [])]
    }

# def movie_serializer(movie: Dict) -> Dict:
#     return {
#         "id": str(movie["_id"]),
#         "title": movie.get("title"),
#         "year": movie.get("year"),
#         "cast": movie.get("cast"),
#         "plot": movie.get("plot"),
#     }

def review_serializer(review: Dict) -> Dict:
    return {
        "id": str(review["_id"]),
        "user_id": str(review["user_id"]),
        "dish_id": str(review["dish_id"]),
        "restaurant_id": str(review["restaurant_id"]),
        "allergies": review.get("allergies", []),
        "restrictions": review.get("restrictions", []),
        "comment": review.get("comment"),
        "created_at": review.get("created_at").isoformat() if review.get("created_at") else None
    }

def dish_serializer(dish: Dict) -> Dict:
    return {
        "id": str(dish["_id"]),
        "name": dish.get("name"),
        "image_url": dish.get("image_url"),
        "restaurant_id": str(dish["restaurant_id"]),
        "allergies": dish.get("allergies", []),
        "restrictions": dish.get("restrictions", []),
        "reviews": [str(review_id) for review_id in dish.get("reviews", [])],
        "created_at": dish.get("created_at").isoformat() if dish.get("created_at") else None,
        "updated_at": dish.get("updated_at").isoformat() if dish.get("updated_at") else None
    }

# User authentication
####################################################
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

# API endpoints
####################################################
# @app.get("/movies/{movie_id}")
# async def get_movie(movie_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
#     try:
#         movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
#         if not movie:
#             raise HTTPException(status_code=404, detail="Movie not found")
#         return movie_serializer(movie)
#     except Exception as e:
#         logging.error(f"Error fetching movie by ID {movie_id}: {e}")
#         raise HTTPException(status_code=400, detail="Invalid movie ID")

# @app.get("/movies/search/")
# async def search_movies(title: str, limit: int = 10):
#     try:
#         cursor = movies_collection.find({"title": {"$regex": title, "$options": "i"}}).limit(limit)
#         movies = await cursor.to_list(length=limit)
#         return [movie_serializer(movie) for movie in movies]
#     except Exception as e:
#         logging.error(f"Error searching movies with title '{title}': {e}")
#         raise HTTPException(status_code=500, detail="Error searching movies")

# @app.get("/movies/")
# async def list_movies(limit: int = 10):
#     try:
#         cursor = movies_collection.find().limit(limit)
#         movies = await cursor.to_list(length=limit)
#         return [movie_serializer(movie) for movie in movies]
#     except Exception as e:
#         logging.error(f"Error listing movies: {e}")
#         raise HTTPException(status_code=500, detail="Error listing movies")
    
# Endpoints for our app, delete the example endpoints above

# place_id not the id in mongodb, corresponds to place id got from google maps API
@app.get("/restaurants/{place_id}")
async def get_restaurant(place_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        restaurant = await restaurants_collection.find_one({"place_id": ObjectId(place_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant_serializer(restaurant)
    except Exception as e:
        logging.error(f"Error fetching restaurant by ID {place_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

@app.get("/restaurants/search/")
async def search_restaurants(town: str, name: str, limit: int = 10):
    try:
        results = await search_restaurants_api(town, name)
        return results
    except Exception as e:
        logging.error(f"Error searching restaurants with name '{name}' in town '{town}': {e}")
        raise HTTPException(status_code=500, detail="Error searching restaurants") 
    
@app.post("/restaurants/")
async def create_restaurant(restaurant: Dict):
    restaurant_data = {
        "name": restaurant.get("name"),
        "google_data": restaurant.get("google_data"),
        "menu": restaurant.get("menu", [])
    }
    result = await restaurants_collection.insert_one(restaurant_data)
    return {"message": "Restaurant created successfully", "id": str(result.inserted_id)}

# Reviews
####################################################
@app.get("/reviews/{review_id}")
async def get_review(review_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        review = await reviews_collection.find_one({"_id": ObjectId(review_id)})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review_serializer(review)
    except Exception as e:
        logging.error(f"Error fetching review by ID {review_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid review ID")

@app.get("/reviews/")
async def list_reviews(limit: int = 10):
    try:
        cursor = reviews_collection.find().limit(limit)
        reviews = await cursor.to_list(length=limit)
        return [review_serializer(review) for review in reviews]
    except Exception as e:
        logging.error(f"Error listing reviews: {e}")
        raise HTTPException(status_code=500, detail="Error listing reviews")
    
@app.post("/reviews/")
async def create_review(review: Dict, current_user: dict = Depends(get_current_user)):
    review_data = {
        "user_id": ObjectId(current_user["_id"]),
        "dish_id": ObjectId(review["dish_id"]),
        "restaurant_id": ObjectId(review["restaurant_id"]),
        "allergies": review.get("allergies", []),
        "restrictions": review.get("restrictions", []),
        "comment": review.get("comment"),
        "created_at": datetime.utcnow()
    }
    result = await reviews_collection.insert_one(review_data)
    return {"message": "Review created successfully", "id": str(result.inserted_id)}

# Dishes
####################################################
@app.get("/dishes/")
async def list_dishes():
    try:
        cursor = restaurants_collection.find().limit(10)
        dishes = await cursor.to_list(length=10)
        return [restaurant_serializer(dish) for dish in dishes]
    except Exception as e:
        logging.error(f"Error listing dishes: {e}")
        raise HTTPException(status_code=500, detail="Error listing dishes")
    
@app.post("/dishes/")
async def create_dish(dish: Dict):
    dish_data = {
        "name": dish.get("name"),
        "image_url": dish.get("image_url"),
        "restaurant_id": ObjectId(dish["restaurant_id"]),
        "allergies": dish.get("allergies", []),
        "restrictions": dish.get("restrictions", []),
        "reviews": [ObjectId(review_id) for review_id in dish.get("reviews", [])],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await dishes_collection.insert_one(dish_data)
    return {"message": "Dish created successfully", "id": str(result.inserted_id)}

@app.get("/dishes/{dish_id}")
async def get_dish(dish_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        dish = await restaurants_collection.find_one({"_id": ObjectId(dish_id)})
        if not dish:
            raise HTTPException(status_code=404, detail="Dish not found")
        return restaurant_serializer(dish)
    except Exception as e:
        logging.error(f"Error fetching dish by ID {dish_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid dish ID")

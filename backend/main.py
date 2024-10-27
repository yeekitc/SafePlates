import logging
import boto3
from fastapi import FastAPI, File, HTTPException, Path, Depends, UploadFile
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

# AWS S3
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-2')
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


# Serializers
####################################################

# def movie_serializer(movie: Dict) -> Dict:
#     return {
#         "id": str(movie["_id"]),
#         "title": movie.get("title"),
#         "year": movie.get("year"),
#         "cast": movie.get("cast"),
#         "plot": movie.get("plot"),
#     }

def restaurant_serializer(restaurant: Dict) -> Dict:
    google_data = restaurant.get("google_data")
    return {
        "id": str(restaurant["_id"]),
        "name": restaurant.get("name"),
        "google_data": {
            "place_id": google_data.get("place_id"),
            "rating": google_data.get("rating"),
            "priceLevel": google_data.get("priceLevel"),
            "reviews": google_data.get("reviews"),
            "address": google_data.get("address"),
            "nationalPhoneNumber": google_data.get("nationalPhoneNumber")
        } if google_data else None,
        "menu": [str(dish_id) for dish_id in restaurant.get("menu", [])]
    }

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
            print("Could not validate credentials - email is None")
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        user = await users_collection.find_one({"email": email})
        if user is None:
            print("User not found")
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except PyJWTError:
        print("Could not validate credentials")
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

# Restaurants
####################################################
# place_id not the id in mongodb, corresponds to place id got from google maps API
@app.get("/restaurants/{place_id}")
async def get_restaurant(place_id: str = Path(..., regex=r"^[a-zA-Z0-9_-]+$")):
    try:
        restaurant = await restaurants_collection.find_one({"google_data.place_id": place_id})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant_serializer(restaurant)
    except Exception as e:
        logging.error(f"Error fetching restaurant by place_id {place_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid restaurant place_id")

@app.get("/restaurants/id/{restaurant_id}")
async def get_restaurant_by_id(restaurant_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        restaurant = await restaurants_collection.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant_serializer(restaurant)
    except Exception as e:
        logging.error(f"Error fetching restaurant by ID {restaurant_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

@app.get("/restaurants/search-db/")
async def search_restaurants_db(name: str, limit: int = 10):
    try:
        cursor = restaurants_collection.find({"name": {"$regex": name, "$options": "i"}}).limit(limit)
        restaurants = await cursor.to_list(length=limit)
        print("restaurants", restaurants)
        print([restaurant_serializer(restaurant) for restaurant in restaurants])
        return [restaurant_serializer(restaurant) for restaurant in restaurants]
    except Exception as e:
        logging.error(f"Error searching restaurants with name '{name}': {e}")
        raise HTTPException(status_code=500, detail="Error searching restaurants")
    
@app.get("/restaurants/search/")
async def search_restaurants(town: str, name: str, limit: int = 10):
    results = [
        {
            'id': 'ChIJT6iVv1bxNIgRkn1QO2lEhiI',
            'nationalPhoneNumber': '(412) 224-5586',
            'formattedAddress': '211 Forbes Ave, Pittsburgh, PA 15222, USA',
            'rating': 3.4,
            'priceLevel': 'PRICE_LEVEL_INEXPENSIVE',
            'displayName': {'text': 'Chipotle Mexican Grill', 'languageCode': 'en'},
            'servesVegetarianFood': True
        },
        {
            'id': 'ChIJhQOupibyNIgReBoACHik1Jw',
            'nationalPhoneNumber': '(412) 904-3716',
            'formattedAddress': '4611 Forbes Ave, Pittsburgh, PA 15213, USA',
            'rating': 3.2,
            'priceLevel': 'PRICE_LEVEL_INEXPENSIVE',
            'displayName': {'text': 'Chipotle Mexican Grill', 'languageCode': 'en'},
            'servesVegetarianFood': True
        },
        {
            'id': 'ChIJVyjr-TvyNIgR_bA14kixa-0',
            'nationalPhoneNumber': '(412) 621-1993',
            'formattedAddress': '4800 Baum Blvd, Pittsburgh, PA 15213, USA',
            'rating': 3.9,
            'priceLevel': 'PRICE_LEVEL_INEXPENSIVE',
            'displayName': {'text': 'Chipotle Mexican Grill', 'languageCode': 'en'},
            'servesVegetarianFood': True
        },
        {
            'id': 'ChIJj5EwlUTzNIgRQJDZdRGUcb4',
            'nationalPhoneNumber': '(412) 746-0602',
            'formattedAddress': '1685 Smallman St, Pittsburgh, PA 15222, USA',
            'rating': 2.2,
            'priceLevel': 'PRICE_LEVEL_INEXPENSIVE',
            'displayName': {'text': 'Chipotle Mexican Grill', 'languageCode': 'en'},
            'servesVegetarianFood': True
        },
        {
            'id': 'ChIJ0VPq8RvtNIgRj5Ga8BZOeHA',
            'nationalPhoneNumber': '(412) 406-8538',
            'formattedAddress': '1027 Freeport Rd, Pittsburgh, PA 15238, USA',
            'rating': 3.2,
            'priceLevel': 'PRICE_LEVEL_INEXPENSIVE',
            'displayName': {'text': 'Chipotle Mexican Grill', 'languageCode': 'en'},
            'servesVegetarianFood': True
        }
    ]
    return results[:limit]
    # try:
    #     results = await search_restaurants_api(town, name)
    #     return results
    # except Exception as e:
    #     logging.error(f"Error searching restaurants with name '{name}' in town '{town}': {e}")
    #     raise HTTPException(status_code=500, detail="Error searching restaurants") 
    
# Make sure to add authentication header when calling this endpoint
@app.post("/restaurants/")
async def create_restaurant(restaurant: Dict, current_user: dict = Depends(get_current_user)):
    """
    Create a new restaurant from Google Places data
    """
    try:
        google_data = restaurant.get("google_data", {})
        restaurant_data = {
            "name": google_data.get("displayName", {}).get("text"),
            "google_data": {
                "id": google_data.get("id"),
                "address": google_data.get("formattedAddress"),
                "rating": google_data.get("rating"),
                "priceLevel": google_data.get("priceLevel"),
                "nationalPhoneNumber": google_data.get("nationalPhoneNumber")
            },
            "menu": []
        }
        
        result = await restaurants_collection.insert_one(restaurant_data)
        return {"message": "Restaurant created successfully", "id": str(result.inserted_id)}
    except Exception as e:
        logging.error(f"Error creating restaurant: {e}")
        raise HTTPException(status_code=500, detail="Could not create restaurant")

@app.get("/restaurants/")
async def list_restaurants(limit: int = 10):
    try:
        cursor = restaurants_collection.find().limit(limit)
        restaurants = await cursor.to_list(length=limit)
        return [restaurant_serializer(restaurant) for restaurant in restaurants]
    except Exception as e:
        logging.error(f"Error listing restaurants: {e}")
        raise HTTPException(status_code=500, detail="Error listing restaurants")
    
@app.put("/restaurants/{restaurant_id}")
async def update_restaurant(restaurant: Dict, restaurant_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        result = await restaurants_collection.update_one({"_id": ObjectId(restaurant_id)}, {"$set": restaurant})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return {"message": "Restaurant updated successfully"}
    except Exception as e:
        logging.error(f"Error updating restaurant by ID {restaurant_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

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

@app.put("/reviews/{review_id}")
async def update_review(review: Dict, review_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        result = await reviews_collection.update_one({"_id": ObjectId(review_id)}, {"$set": review})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"message": "Review updated successfully"}
    except Exception as e:
        logging.error(f"Error updating review by ID {review_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid review ID")
    
# @app.post("/upload")
# async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
#     """
#     Upload an image to S3 and return the URL
#     """
#     try:
#         # Read file content
#         file_content = await file.read()
        
#         # Generate unique filename with original extension
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         original_extension = os.path.splitext(file.filename)[1]
#         filename = f"dish-uploads/{timestamp}{original_extension}"

#         # Upload to S3
#         s3_client.put_object(
#             Bucket=AWS_BUCKET_NAME,
#             Key=filename,
#             Body=file_content,
#             ContentType=file.content_type
#         )

#         # Generate public URL
#         image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
#         return {"url": image_url}
#     except Exception as e:
#         logging.error(f"Error uploading file to S3: {e}")
#         raise HTTPException(status_code=500, detail="Could not upload file")

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
        dish = await dishes_collection.find_one({"_id": ObjectId(dish_id)})
        if not dish:
            raise HTTPException(status_code=404, detail="Dish not found")
        return dish_serializer(dish)
    except Exception as e:
        logging.error(f"Error fetching dish by ID {dish_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid dish ID")
    
@app.put("/dishes/{dish_id}")
async def update_dish(dish: Dict, dish_id: str = Path(..., regex=r"^[0-9a-fA-F]{24}$")):
    try:
        result = await dishes_collection.update_one({"_id": ObjectId(dish_id)}, {"$set": dish})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Dish not found")
        return {"message": "Dish updated successfully"}
    except Exception as e:
        logging.error(f"Error updating dish by ID {dish_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid dish ID")
    
@app.get("/dishes/search/")
async def search_dish_by_name_and_restaurant(name: str, restaurant_id: str):
    """
    Search for a dish by name within a specific restaurant
    """
    try:
        dish = await dishes_collection.find_one({
            "name": {"$regex": f"^{name}$", "$options": "i"},
            "restaurant_id": ObjectId(restaurant_id)
        })
        return dish_serializer(dish) if dish else None
    except Exception as e:
        logging.error(f"Error searching dish: {e}")
        raise HTTPException(status_code=500, detail="Error searching dish")
    
    

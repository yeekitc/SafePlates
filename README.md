# Technica 2024

## Backend
### Setup
Open the entire backend folder in an IDE. Then in that terminal, run the following commands:

 1. `python3 -m venv venv`
 2. `source venv/bin/activate`
 3. `pip install -r requirements.txt`
 4. Create a `.env` file at `backend/.env`
 5. Add `MONGO_URI=<connection_string>` to the `.env`

### To run the backend server
 Run the command `uvicorn main:app --reload`

## Frontend

### Setup
Navigate inside the frontend folder. Then in the terminal, run `npm install`

### To run the frontend
Run the command `npm run dev`


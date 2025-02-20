# SpeedyBots

An educational chatbot designed for German-speaking train drivers at Schweizerische Südostbahn AG (SOB). 
This chatbot assists drivers in learning and communicating in technical Italian, 
which is essential for railway operations in the Ticino region.

## Requirements

Backend:
*	Python 3.8 or higher
*	Flask
*	Ollama (running in http://localhost:11434)

Frontend:
*	Node.js 10.0 or higher
*	npm or yarn

Database:
*	SQLite

## How run the project
### Backend
Navigate to the backend directory:
#### `cd backend`
Create a virtual environment:
#### `python -m venv venv`
Activate the virtual environment:
•Windows:
#### `venv\Scripts\activate`
•Mac/Linux:
#### `source venv/bin/activate`
Install the dependencies:
#### `pip install -r requirements.txt`
Start the Flask server:
#### `python run.py`
Open [http://localhost:5000](http://localhost:3000) to view it in your browser.

### DB
!!! Optionally, there is also a demodb (app.db) in the repository.

Navigate to the backend directory:
#### `cd backend`
Initialize the database
#### `flask db init`
Apply existing migrations to create the database schema:
#### `flask db upgrade`

### Frontend
Navigate to the frontend directory:
#### `cd frontend`
Install the dependecies:
#### `npm install`
Start the frontend:
#### `npm start`
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.



## Next steps
* Improve the reliability of the LLM
* LLM integration to vary exercise feedback responses

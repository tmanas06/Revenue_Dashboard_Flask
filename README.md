# Flask + React Application

This is a full-stack application with a Flask backend and React frontend.

## Project Structure

```
ari/
├── backend/          # Flask backend
│   ├── app.py
│   └── requirements.txt
└── frontend/         # React frontend (created by create-react-app)
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup

1. Make sure you have Node.js and npm installed

2. Create a new React app in the frontend directory:
   ```bash
   npx create-react-app frontend
   cd frontend
   ```

3. Install axios for API calls:
   ```bash
   npm install axios
   ```

4. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## Postgres setup
backend > .env
   ```bash
   DATABASE_URL=postgresql://postgres:Manas@localhost:5432/revenue_db
   ```

## Development

- The Flask backend runs on port 5000
- The React frontend runs on port 3000
- The React app is configured to proxy API requests to the Flask backend

## Available Scripts

In the frontend directory, you can run:

- `npm start` - Start the development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from create-react-app (irreversible)

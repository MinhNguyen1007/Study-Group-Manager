#!/bin/bash
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Initializing database..."
python scripts/init_db.py

echo "Starting application..."
python main.py 
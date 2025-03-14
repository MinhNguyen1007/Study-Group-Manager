#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Making run script executable..."
chmod +x scripts/run.sh

echo "Setup completed!"
echo "You can now run the application using: ./scripts/run.sh" 
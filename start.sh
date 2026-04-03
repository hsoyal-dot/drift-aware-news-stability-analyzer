#!/bin/bash
# Start backend
source venv/bin/activate
python backend_main.py &

# Start frontend
cd web_ui
npm run dev

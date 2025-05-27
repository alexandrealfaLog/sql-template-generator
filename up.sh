#!/bin/bash

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual em ./venv ..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

pip install --no-cache-dir -r requirements.txt

python main.py
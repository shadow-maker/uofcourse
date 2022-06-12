#!/bin/bash

ip=$1

echo "\nSTARTING MYSQL SERVER"
mysql.server start

echo "\nACTIVATING VENV"
source .venv/bin/activate

echo "\nINSTALLING PIP REQUIREMENTS"
pip install -r requirements.txt

echo "\nRUNNING APP"
if [[ "$ip" == "" ]]; then
	flask run
	
else
	flask run --host=$ip
fi

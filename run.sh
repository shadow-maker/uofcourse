#!/bin/bash

ip=$1

echo "\nSTARTING MYSQL SERVER"
mysql.server start

echo "\nACTIVATING VENV"
source env/bin/activate

echo "\nINSTALLING PIP REQUIREMENTS"
pip install -r requirements.txt

#echo "\nEXPORTING FLASK ENV VARIABLES"
#export FLASK_APP=planner
#export FLASK_ENV=development

echo "\nRUNNING APP"
if [[ "$ip" == "" ]]; then
	flask run
	
else
	flask run --host=$ip
fi

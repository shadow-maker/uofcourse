#!/bin/bash

echo "\nEXPORTING PIP REQUIREMENTS"
pip freeze > requirements.txt

echo "\nDEACTIVATING VENV"
deactivate

echo "\nSTOPPING MYSQL SERVER"
mysql.server stop

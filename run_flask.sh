#!/bin/bash
source venv/bin/activate;
export FLASK_APP="luminance/luminance.py";
export FLASK_DEBUG=1;
flask run
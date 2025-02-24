@echo off
call .venv\Scripts\activate
python -m gevent.monkey app.py

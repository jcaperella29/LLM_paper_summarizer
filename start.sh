#!/bin/bash
ollama serve & sleep 10
exec gunicorn -b 0.0.0.0:8080 app:app

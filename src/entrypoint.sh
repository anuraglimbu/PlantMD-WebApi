#!/bin/bash

echo "================================ Sever is starting now  =================================="
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*
#!/bin/bash

exec streamlit run 0_Home.py \
    --server.port 8501 \
    --server.baseUrlPath /dash/ \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.headless=true

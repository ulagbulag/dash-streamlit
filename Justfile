default:
  @just run

run *ARGS:
  streamlit run 0_Home.py \
    --browser.gatherUsageStats=False \
    --server.address=0.0.0.0 \
    --server.baseUrlPath=/dev/dash/ \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true \
    --server.port=8501 \
    {{ ARGS }}

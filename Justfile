# Configure environment variables
export ALPINE_VERSION := env_var_or_default('ALPINE_VERSION', '3.17')
export OCI_IMAGE := env_var_or_default('OCI_IMAGE', 'quay.io/ulagbulag/openark-dash-management-tool')
export OCI_IMAGE_VERSION := env_var_or_default('OCI_IMAGE_VERSION', 'latest')

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

oci-build:
  docker build \
    --tag "${OCI_IMAGE}:${OCI_IMAGE_VERSION}" \
    --build-arg ALPINE_VERSION="${ALPINE_VERSION}" \
    .

oci-push: oci-build
  docker push "${OCI_IMAGE}:${OCI_IMAGE_VERSION}"

oci-push-and-update-dash: oci-push
  kubectl -n kiss delete pods --selector name=management-tool

IMAGE_TAG ?= $(shell date +%s)

PROJECT_ID=word-definer
BUCKET_NAME=word-definer-frontend
IMAGE_NAME=gcr.io/$(PROJECT_ID)/word-definer-api:$(IMAGE_TAG)

.PHONY: build-image push-image deploy clean update-frontend deploy-all

deploy-all:
	@export IMAGE_TAG=$$(date +%s) && \
	IMAGE_NAME=gcr.io/$(PROJECT_ID)/word-definer-api:$$IMAGE_TAG && \
	echo "Using image: $$IMAGE_NAME" && \
	make build-image IMAGE_TAG=$$IMAGE_TAG && \
	make deploy IMAGE_TAG=$$IMAGE_TAG && \
	make update-frontend

build-image:
	echo "Building image $(IMAGE_TAG)..."
	docker buildx create --use || true
	docker buildx build --platform linux/amd64 -t $(IMAGE_NAME) --push .

deploy: 
	cd infrastructure && terraform init && terraform apply \
	  -var="project_id=$(PROJECT_ID)" \
	  -var="bucket_name=$(BUCKET_NAME)" \
	  -var="api_image=$(IMAGE_NAME)"

# Destroy the infrastructure!
destroy:
	cd infrastructure && terraform destroy -auto-approve \
	  -var="project_id=$(PROJECT_ID)" \
	  -var="bucket_name=$(BUCKET_NAME)" \
	  -var="api_image=$(IMAGE_NAME)"

update-frontend:
	cd infrastructure && API_URL=$$(terraform output -raw api_url) && cd .. \
	&& sed "s|__API_URL__|$${API_URL}|g" frontend/index.html > frontend/index.deploy.html \
	&& gsutil cp frontend/index.deploy.html gs://$(BUCKET_NAME)/index.html \
	&& gsutil cp frontend/style.css gs://$(BUCKET_NAME)/style.css 

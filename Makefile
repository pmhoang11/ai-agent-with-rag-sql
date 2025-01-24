# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# Docker init
build:
	docker compose -f docker-compose.yml build

# Start
start: ## Start app service
	docker compose -f docker-compose.yml up -d

# Stop
stop: ## Stop app service
	docker compose -f docker-compose.yml down

#### SERVICES ####
build-service: ## Build a service
	cd service_${SERVICE} && bash build
start-service: ## Start a service
	cd service_${SERVICE} && bash run
stop-service: ## Start a service
	cd service_${SERVICE} && bash stop

.PHONY: local-infra-up local-infra-down

local-infra-up:
	cd deployment/local && docker compose --env-file ./local.env up -d db redis

local-infra-down:
	cd deployment/local && docker compose --env-file ./local.env down

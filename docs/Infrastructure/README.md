---
title: "Infrastructure & DevOps Index"
date: 2026-11-05
last_modified: 2026-11-05
tags:
  - infra
  - docker
  - aws
  - devops
type: index
status: active
---

# Infrastructure & DevOps

This directory documents deployment topologies, Docker Compose setups, AWS services (Cognito, S3, CloudFront), and environment configurations.

## Architecture Highlights
- **Local Dev:** `infra/docker-compose.yml` (symlinked at root `docker-compose.yml`)
- **Containers:**
  - `core-aairi-api`: PHP 8.4-fpm / Laravel 12
  - `core-aairi-nginx`: Nginx reverse proxy
  - `core-aairi-db`: PostgreSQL / MariaDB database service
- **Authentication:** AWS Cognito User Pools & Identity Pools

Back to [[00 - Index|Vault Index]].


# CMS System

A Django-based Content Management System with service oriented architecture.

## Project Structure

- **cms**: Content Management System module
- **discovery**: Content Discovery and Search module  
- **users**: User Management and Authentication module
- **external_sources**: Connecter (Plug and Play) with external services module

## Requirements
- **Docker**
- **Docker Compose**

## Run the Project

1- Start dependencies (Postgres, Redis, Kafka, Zookeeper, OpenSearch):

**docker-compose up -d zookeeper postgres redis opensearch kafka --build**

Wait until OpenSearch is ready. Look for this log before continuing:
[cms-node] publish_address {172.21.0.4:9300}, bound_addresses {[::]:9300}

2- Start the app services (Django server, Celery workers, Discovery indexer/web) - all tests will run automatically in the Django server before starting it:

**docker-compose up -d server celery discovery_indexer discovery_web --build**

## API Documentation
OpenAPI (ReDoc): http://localhost:8000/api/redoc



# Portfolio Tracker Server

## Setup

### Set up python environment and install prequisite packages

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

### Local environment variables

`export FLASK_APP='portfolio.py'`

`export FLASK_ENV=development`

`export PORTFOLIO_CONFIG_FILE='dev.py'`

### Database setup

Set up database for tests

`psql -c 'create database portfoliotest;'`

Set up database for local development

`psql -c 'create database portfolio;'`

Initialize database schema

`flask db upgrade`

## Commands

Run the app

`flask run`

Run tests

`pytest`


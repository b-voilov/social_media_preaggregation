# youtube data preaggregation

## Installation

```bash
pip install -r requirements.txt
./install.sh
```

## Running

Uses **postgres** as storage for precomputed metrics.
Use `schema.sql` to initiate necessary tables.
Set following envs

```bash
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_DATABASE
```

Then run

```bash
python main.py
```

## Dev

The following sets up `python3.9` docker container with mounted `.`. Intended to use with [VS Code In Docker](https://code.visualstudio.com/docs/devcontainers/containers) feature

```bash
docker-compose up -d
```

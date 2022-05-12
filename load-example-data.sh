#!/bin/bash

# Load:
# - Example signal groups from Hamburg
# - (Composer) Example routes from Hamburg
# - (Composer) Manually picked bindings for routes through Hamburg
docker exec -t -i sg-selector-backend bash -c "
  poetry run python backend/manage.py migrate && \
  poetry run python backend/manage.py load_sgs /examples/sgs_hamburg.json && \
  poetry run python backend/manage.py load_example_routes /examples/example_routes.json && \
  poetry run python backend/manage.py load_bindings /examples/bindings/ && \
  poetry run python backend/manage.py load_visualization
"
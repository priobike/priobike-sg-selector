# PrioBike SG Selector

## Overlook

This module is split into two components, the `backend` service that selects signal groups and the `frontend` service that is used to visualize the algorithms of the `backend` service. Additionally, the `frontend` service is used to manually create route-sg-mappings which can be used to validate the `backend` service. To realize this, the `backend` service provides additional subcomponents to communicate with the `frontend` via REST endpoints. However, these components are stripped in the deployed `backend` service since they are only used for development.

The `routing`-subcomponent ([`backend/backend/routing`](backend/backend/routing)) is the only one being used in production and thus deployed.

### Other Backend-Subcomponents

- `analytics` ([`backend/backend/analytics`](backend/backend/analytics))
  - Used to analyze different matching approaches.
  - With the management command ([see](#Custom-Management-Commands)) `run_analysis.py` ([`backend/backend/analytics/management/commands/run_analysis.py`](backend/backend/analytics/management/commands/run_analysis.py)) different approaches can be set as values in the `strategies`-dict and thus tested against the whole ground truth dataset.
- `composer` ([`backend/backend/composer`](backend/backend/composer))
  - Used to create the ground truth dataset.
- `demo` ([`backend/backend/demo`](backend/backend/demo))
  - Used to test the matching approaches visually with some example routes.
- `jiggle_vis` ([`backend/backend/jiggle_vis`](backend/backend/jiggle_vis))
  - Used to try out a jiggle-/data-augmentation-feature visually with different MAP topologies.
- `ml_evaluation` ([`backend/backend/ml_evaluation`](backend/backend/ml_evaluation))
  - Used to evaluate different ML-models, feature subsets, projection methods and feature transformation methods as well as to perform hyperparameter tuning.
    - Thus it contains for example management commands for the following things:
        - Train models.
        - Tune hyperparameters.
        - Generate dataset with features from ground truth with labeled route and MAP topology samples.
        - Compute feature selection metrics such as transinformation, correlations and timings and perform RFE.
  - Configs for different configurations of features, feature transformations and other things can be found here: [`backend/backend/ml_evaluation/configs`](backend/backend/ml_evaluation/configs)
    - Those are also referenced in all kind of scripts and thus perform in dependence of the things set there.
    - To use a config in production it needs to be copied to [`backend/backend/routing/matching/ml/configs_production`](backend/backend/routing/matching/ml/configs_production). Additionally, the created and to the configs corresponding models (ML models and feature transformation models) need to get copied from  [`backend/backend/ml_evaluation/models`](backend/backend/ml_evaluation/models) to [`backend/backend/routing/matching/ml/models`](backend/backend/routing/matching/ml/models). The seperation has been done, because during evaluation a lot of configs and models can get created which would take up a lot of space in production and also make it very convoluted.
- `projection_vis` ([`backend/backend/projection_vis`](backend/backend/projection_vis))
  - Used to visualize different route-segment-selection strategies
  - Currently there exist two projection strategies and one alternative strategy. The strategies are implemented here: ([`backend/backend/routing/matching/projection.py`](backend/backend/routing/matching/projection.py))


## Getting started

Run the development setup with

```bash
docker-compose up
```

On the very first startup, this will build the containers (can take some time). You may have to make the entrypoint scripts executable.

## Custom Management Commands

If you wish to perform more advanced actions, there are several custom management commands. It is recommended to execute the management commands from the Docker container with `docker exec -t -i sg-selector-backend /bin/bash` and then `poetry run python backend/manage.py <your_command_name>`.

## REST Endpoint

### *POST* `/routing/select`

#### Request format

Select signal groups along a given route. The body of the POST request should contain a route as follows:

```json
{
    "route": [
        { "lon": <longitude>, "lat": <latitude>, "alt": <altitude> },
        ...
    ]
}
```

#### Response format

Perform an example request with the example preset route:

```bash
curl --data "@backend/data/priobike_route_ost_west.json" http://localhost:8000/routing/select
```

Note that with this payload, all other fields than `"route"` and its associated coordinate pairs will be ignored by the service. The response can be used in a comparison with the example payload to check the validity of results. Results are in the following structure:

```json
{
  "route": [
    {
      "lon": 9.990909,
      "lat": 53.560863,
      "alt": 9.99,
      "distanceToNextSignal": 152.0200566720922,
      "signalGroupId": "hamburg/271_31"
    },
    ...
    {
      "lon": 9.978001,
      "lat": 53.564378,
      "alt": 20.22,
      "distanceToNextSignal": null,
      "signalGroupId": null
    }
  ],
  "signalGroups": {
    "hamburg/271_31": {
      "label": "Radfahrer",
      "position": {
        "lon": 9.9901167,
        "lat": 53.5614852
      },
      "id": "hamburg/271_31"
    },
    "hamburg/279_24": {
      "label": "Radfahrer",
      "position": {
        "lon": 9.9848618,
        "lat": 53.5640752
      },
      "id": "hamburg/279_24"
    },
    "hamburg/279_25": {
      "label": "Radfahrer",
      "position": {
        "lon": 9.9846914,
        "lat": 53.5640837
      },
      "id": "hamburg/279_25"
    }
  }
}
```

## Frontend-URLs

After running `docker-compose up` (in debug-mode such that the additional subcomponents also are runnning) under the following URLs sites are accessible:

- Frontend for the `composer`-backend (to create the ground truth dataset): `http://localhost:3000/composer?route_id=1`
  - Composer-Overview for statistics of all the samples as well as functions to perform a check whether all the samples in the database as well as in the `.json`-files (e.g. for persistent storate in repo) are the same: `http://localhost:3000/composer/overview`
- Frontend for the `demo`-backend: `localhost:3000/demo?route_id=999&matcher=ml`
- Frontend for the `jiggle_vis`-backend: `http://localhost:3000/jiggle_vis?route_id=1`
- Frontend for the `projection_vis`-backend: `http://localhost:3000/projection_vis?route_id=1&lsa_id=2182&method=extended`

## Disclaimer

In the code `lsa` (german: LichtSignalAnlage, english: light signal system) is being used synonymously to `sg` (signal group).

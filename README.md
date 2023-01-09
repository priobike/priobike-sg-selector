# PrioBike SG Selector

## Overlook

This module is split into two components, the `backend` service that selects signal groups and the `frontend` service that is used to visualize the algorithms of the `backend` service. Additionally, the `frontend` service is used to manually create route-sg-mappings which can be used to validate the `backend` service. To realize this, the `backend` service provides additional subcomponents to communicate with the `frontend` via REST endpoints. However, these components are stripped in the deployed `backend` service since they are only used for development.

## Getting started

Run the development setup with

```bash
docker-compose up
```

On the very first startup, this will build the containers (can take some time). You may have to make the entrypoint scripts executable.

## Custom Management Commands

If you wish to perform more advanced actions, there are several custom management commands. It is recommended to execute the management commands from the Docker container with `docker exec -t -i backend /bin/bash` and then `poetry run python backend/manage.py <your_command_name>`.

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

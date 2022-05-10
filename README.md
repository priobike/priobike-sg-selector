# SG Selector Library

## Quickstart

### 1. Build and run the development setup

Run the development setup with

```bash
docker-compose up
```

On the very first startup, this will download the base Docker images and build the containers (can take some time). 

### 2. Load the example signal groups into the database

We provide an example JSON which you can load into the database. This JSON is inherited from the Urban Data Platform Hamburg, which uses a [FROST](https://github.com/FraunhoferIOSB/FROST-Server) API.
However, the service is not limited to this specific data format. See [backend/routing/models.py](backend/routing/models.py) for the basic model structure.

```bash
docker exec -t -i sg-selector-backend poetry run python backend/manage.py load_sgs /examples/sgs_hamburg.json
```

### 3. Send a request to the REST Endpoint at *POST* `/routing/select`

#### Request format

Select signal groups along a given route. The body of the POST request should contain a route as follows:

```
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
curl --data "@examples/route_hamburg.json" http://localhost:8000/routing/select
```

Results are in the following structure:

```
{
  "waypoints": [
    {
      "lon": 9.990909,
      "lat": 53.560863,
      "alt": 9.99,
      "distanceToNextSignal": 152.0200566720922,
      "nextSignal": "1814"
    },
    ... [ Truncated ]
    {
      "lon": 9.978001,
      "lat": 53.564378,
      "alt": 20.22,
      "distanceToNextSignal": null,
      "nextSignal": null
    }
  ],
  "signals": [
    {
      "id": "1814",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [
            9.9901167,
            53.5614852
          ],
          [
            9.9900136,
            53.5615304
          ]
        ]
      }
    },
    ... [ Truncated ]
  ]
}
```

### Troubleshooting

You may have to make the entrypoint scripts executable with `chmod +x path/to/entrypoint.sh`.

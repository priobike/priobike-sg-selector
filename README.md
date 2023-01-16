# Signal Group (SG) Selector

![screenshot](https://user-images.githubusercontent.com/27271818/211346111-7f059454-eee2-4444-ba16-52c90bffb865.png)

With the signal group (sg) selector service, it is possible to match traffic lights to routes. This is done by matching linestring geometries (MAP topologies) of traffic lights to the route geometry. In our application we often use the term LSA synonymously for SG/Traffic Light. LSA means Lichtsignalanlage in German.

## Algorithmic Selection

![algorithm](https://user-images.githubusercontent.com/27271818/211346186-c9f262fb-7271-4b3b-8bf7-fae42c19e4a4.png)

This matching is achieved using above filtering pipeline. The filtering pipeline consists of these steps:

1. Proximity matching – Exclude all signal groups that are too far away from the route.
2. Bearing matching - Exclude all signal groups that have too much angle difference with regards to the route.
3. Length matching - Exclude all signal groups which can not be projected onto the route without a too big length difference.
4. Overlap matching - Under the remaining signal groups, find overlaps and decide for the better matches.
5. Adding the crossings that are not connected (have no MAP-Topologies) from this dataset: https://metaver.de/trefferanzeige?docuuid=C498DEED-985C-11D5-889E-000102B6A10E

This filtering pipeline is defined as a hypermodel and tuned by Optuna on a training dataset. The best configuration is available with a RESTful API.

## ML Selection

![ml](https://user-images.githubusercontent.com/27271818/211346535-b0479808-806c-4716-a689-75c5c3161a46.png)

This matching is achieved using a machine learning model, as shown above. This filtering includes the following steps:

1. Proximity matching – Exclude all signal groups that are too far away from the route.
2. ML matching – Extract features for each MAP topology with regards to the route, and make a binary classification ("match" or "no match").
3. Overlap Cleanup – Detect overlaps and only select the topologies with the highest class probability for "match".
4. Adding the crossings that are not connected (have no MAP-Topologies) from this dataset: https://metaver.de/trefferanzeige?docuuid=C498DEED-985C-11D5-889E-000102B6A10E

## Quickstart

1. Build and run the development setup

Run the development setup with

```
docker-compose up
```

On the very first startup, this will download the base Docker images and build the containers (can take some time). We provide example data so that you can understand our data format and try it out for yourself. This data is inherited from the Urban Data Platform Hamburg, which uses a FROST API. With the running docker-compose setup, this data is included in the PostGIS (running in the background) - see backend/run-preheating.sh.

2. Send a request to the REST Endpoint at POST /routing/select

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
```
curl --data "@backend/data/priobike_route_ost_west.json" 'http://localhost:8000/routing/select'
```

To select the OSM-specific algorithmic matcher, use:
```
curl --data "@backend/data/priobike_route_ost_west.json" 'http://localhost:8000/routing/select?matcher=legacy&routing=osm'
```

To select the DRN-specific algorithmic matcher, use:
```
curl --data "@backend/data/priobike_route_ost_west.json" 'http://localhost:8000/routing/select?matcher=legacy&routing=drn'
```

To select the OSM-specific machine learning matcher, use:
```
curl --data "@backend/data/priobike_route_ost_west.json" 'http://localhost:8000/routing/select?matcher=ml&routing=osm'
```

To select the DRN-specific machine learning matcher, use:
```
curl --data "@backend/data/priobike_route_ost_west.json" 'http://localhost:8000/routing/select?matcher=ml&routing=drn'
```

Results are in the following structure:
```
{
  "route": [
    {
      "lon": 9.990909,
      "lat": 53.560863,
      "alt": 9.99,
      "signalGroupId": "hamburg/271_14",
      "distanceOnRoute": 0,
      "distanceToNextSignal": 80.0591490111176
    },
    [...],
    {
      "lon": 9.978001,
      "lat": 53.564378,
      "alt": 20.22,
      "signalGroupId": null,
      "distanceOnRoute": 1011.180699223152,
      "distanceToNextSignal": null
    }
  ],
  "signalGroups": {
    "hamburg/271_14": {
      "label": "hamburg/271_14",
      "position": {
        "lon": 9.9902099,
        "lat": 53.5614479
      },
      "id": "hamburg/271_14",
      "lsaId": "271_14",
      "connectionId": "14",
      "laneType": "Radfahrer",
      "datastreamDetectorCar": null,
      "datastreamDetectorCyclists": null,
      "datastreamCycleSecond": "12864",
      "datastreamPrimarySignal": "12399",
      "datastreamSignalProgram": "9579"
    },
    [...]
  },
  "crossings": [
    {
      "name": "Rentzelstraße / An Der Verbindungsbahn",
      "position": {
        "lon": 9.978001,
        "lat": 53.564378
      },
      "connected": true
    },
  ]
}
```

Response Structure:

- route: The waypoints of the route, with the signal groups and the current distance to the next signal, if exists.
- signalGroups: A more detailled dictionary with information about all the signal groups, including datastream (FROST) ids.
- crossings: A list of intersections along the route, including intersections that are not connected (and have no MAP-Topologies).

## Specifig matching in dependence of the routing data basis
In our app, we initially only supported routing based on OpenStreetMap (OSM) data. For this we also developed and studied our two matching approaches (algorithmic and ML). During the evaluation we came to the conclusion that routes based on OSM-data contain a lot of routing errors with respect to a cycling-specific-routing. Later we implemented routing based on an other data source than OSM. Specifically we used the so called [Digitales Radverkehrsnetz (DRN) Hamburg](https://metaver.de/trefferanzeige?docuuid=EA847D9F-6403-4B75-BCDB-73F831F960C7) providing us a much more detailed and correct representation of the cycle paths in Hamburg. With the new data source we were able to achieve much better results with respect to a cycling-specific-routing which manifests itself, for example, in the following points:
- Available cycle paths are used a lot more
- Fewer unnecessary and incorrect detours on or off the cycle path

As a result the routes based on DRN differ from the routes based on OSM. Since our two matching algorithms were tuned/trained on the characteristics of OSM-routes in comparison to the turn topologies, we also re-tuned/-trained them for the new DRN-based routes. To choose the routing specific matching approaches, append the query parameter `routing=osm`/`routing=drn` to the `/select`-endpoint (as shown here: [Response Format](#Response-format))

## Contributing

This library is available under MIT License. Contributions are welcome. Here is our current progress:

- Publish usable library with our topologic feature matching pipeline
- Incorporate Python scripts for random route generation
- Polish and push management commands for hypermodel training and testing
- Add Route Composer web application which is used for training dataset generation
- Include experimental matching approaches (ML-Model, Dijkstra, Probabilistic)
- Advance experimental ML-based feature matching approach

Planned research on this topic is completed. Currently we focus on using the DRN dataset for routing and re-tuning our matching approaches.

### Route Composer

<img width="1604" alt="composer" src="https://user-images.githubusercontent.com/27271818/211347052-e17a3bf4-1f45-4a1e-9c07-76cb2ff30649.png">


After running docker-compose up (in debug-mode such that the additional subcomponents also are runnning) under the following URLs sites are accessible:

- Frontend for the composer-backend (to create the ground truth dataset): http://localhost:3000/composer?route_id=1
- Composer-Overview for statistics of all the samples as well as functions to perform a check whether all the samples in the database as well as in the .json-files (e.g. for persistent storate in repo) are the same: http://localhost:3000/composer/overview
- Frontend for the demo-backend: localhost:3000/demo?route_id=999&matcher=ml
- Frontend for the jiggle_vis-backend: http://localhost:3000/jiggle_vis?route_id=1
- Frontend for the projection_vis-backend: http://localhost:3000/projection_vis?route_id=1&lsa_id=2182&method=extended

In the route composer we used Carto (CARTO Basemaps Terms of Service: https://drive.google.com/file/d/1P7bhSE-N9iegI398QYDjKeVhnbS7-Ilk/view) in combination with OpenStreetMap (available under the Open Data Commons Open Database License, https://www.openstreetmap.org/copyright) for the map tiles.

### Project Structure

This module is split into two components, the `backend` service that selects signal groups and the `frontend` service that is used to visualize the algorithms of the `backend` service. Additionally, the `frontend` service is used to manually create route-sg-mappings which can be used to validate the `backend` service. To realize this, the `backend` service provides additional subcomponents to communicate with the `frontend` via REST endpoints. However, these components are stripped in the deployed `backend` service since they are only used for development.

The `routing`-subcomponent ([`backend/backend/routing`](backend/backend/routing)) is the only one being used in production and thus deployed.

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

## Anything unclear?

Help us improving this documentation. If you have any problems or unclarities, feel free to open an issue.

## Citing

If you (re)use our work, please cite us:

```bibtex
@inproceedings{matthes2022matching,
  title={Matching Traffic Lights to Routes for Real-World Deployments of Mobile GLOSA Apps},
  author={Matthes, Philipp and Springer, Thomas},
  booktitle={2022 IEEE International Smart Cities Conference (ISC2)},
  pages={1--7},
  year={2022},
  organization={IEEE}
}
```

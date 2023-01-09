CONTAINER_ALREADY_STARTED="osm-data-already-imported-to-postgis-flag"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    echo "-- First container startup --"
    echo "-- Create hstore extension --"
    PGPASSWORD=${POSTGRES_PASSWORD} psql -d ${POSTGRES_NAME} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -W -c 'create extension if not exists hstore'
    echo "-- Import OSM data --"
    PGPASSWORD=${POSTGRES_PASSWORD} osm2pgsql -c -d ${POSTGRES_NAME} -U ${POSTGRES_USER} -H ${POSTGRES_HOST} -P ${POSTGRES_PORT} -W data/osm/hamburg-latest.osm.pbf  
else
    echo "-- Not first container startup --"
fi
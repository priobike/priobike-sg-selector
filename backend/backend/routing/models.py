from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.functional import cached_property


class LSA(models.Model):
    """ A LSA. """

    id = models.CharField(max_length=10, primary_key=True)

    # The geometry of the ingress line
    ingress_geometry = models.LineStringField(
        srid=settings.LONLAT, geography=True)

    # The geometry of the connection line
    geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    # The geometry of the egress line
    egress_geometry = models.LineStringField(
        srid=settings.LONLAT, geography=True)

    @cached_property
    def start_point(self) -> Point:
        """
        The start point of the LSA.

        The start point is defined as the first point of the geometry.
        """
        return Point(*self.geometry.coords[0], srid=self.geometry.srid)

    @cached_property
    def end_point(self) -> Point:
        """
        The end point of the LSA.

        The end point is defined as the last point of the geometry.
        """
        return Point(*self.geometry.coords[-1], srid=self.geometry.srid)

    def __str__(self):
        return f"{self.id}"


class LSAMetadata(models.Model):
    """ Metadata for a LSA. """

    lsa = models.OneToOneField(LSA, on_delete=models.CASCADE, primary_key=True)
    topic = models.TextField()
    asset_id = models.TextField()
    lane_type = models.TextField()
    language = models.TextField()
    owner_thing = models.TextField()
    info_last_update = models.DateTimeField()

    connection_id = models.CharField(max_length=10)
    egress_lane_id = models.CharField(max_length=10)
    ingress_lane_id = models.CharField(max_length=10)
    traffic_lights_id = models.CharField(max_length=10)
    signal_group_id = models.CharField(max_length=25)

    # The datastream id for a car detector, if exists
    # (layerType == detector_car).
    datastream_detector_car_id = models.CharField(max_length=25, null=True)

    # The datastream id for a cyclists detector, if exists
    # (layerType == detector_cyclists).
    datastream_detector_cyclists_id = models.CharField(
        max_length=25, null=True)

    # The datastream id for the cycle second, if exists
    # (layerType == cycle_second).
    datastream_cycle_second_id = models.CharField(max_length=25, null=True)

    # The datastream id for the primary signal, if exists
    # (layerType == primary_signal).
    datastream_primary_signal_id = models.CharField(max_length=25, null=True)

    # The datastream id for the signal program, if exists
    # (layerType == signal_program).
    datastream_signal_program_id = models.CharField(max_length=25, null=True)

    def __str__(self):
        return f"{self.lsa.id}"


class LSACrossing(models.Model):
    """
    A crossing where we may find traffic lights.

    See: https://metaver.de/trefferanzeige?cmd=doShowDocument&docuuid=C498DEED-985C-11D5-889E-000102B6A10E#detail_links
    And: https://api.hamburg.de/datasets/v1/lichtsignalanlagen/api#/Data/feature-lsa_knotengrunddaten
    And: https://geoportal-hamburg.de/geo-online/?Map/layerIds=12883,12884,16101,19969,398&visibility=true,true,true,true,true&transparency=0,0,0,0,0&Map/center=%5B565212.5420238541,5934028.87506001%5D&Map/zoomLevel=6
    """

    # The name of the crossing as given by the app:LSA_Name attribute in the data.
    # This is a string of the form "Osterstraße / Eppendorfer Weg".
    name = models.CharField(max_length=255)

    # The point geometry of the crossing as given by the gml:pos attribute in the data.
    # In the data, this is a string of the form "563664.000 5936542.000" in the EPSG:25832 projection.
    point = models.PointField(srid=settings.LONLAT, geography=True)

    # If the crossing contains a traffic light.
    # Some crossings may not contain any connected traffic lights at all.
    connected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} ({self.name})"


class PlanetOsmLine(models.Model):
    osm_id = models.BigIntegerField(primary_key=True, blank=True, null=False)
    access = models.TextField(blank=True, null=True)
    # Field renamed to remove unsuitable characters.
    addr_housename = models.TextField(
        db_column='addr:housename', blank=True, null=True)
    # Field renamed to remove unsuitable characters.
    addr_housenumber = models.TextField(
        db_column='addr:housenumber', blank=True, null=True)
    # Field renamed to remove unsuitable characters.
    addr_interpolation = models.TextField(
        db_column='addr:interpolation', blank=True, null=True)
    admin_level = models.TextField(blank=True, null=True)
    aerialway = models.TextField(blank=True, null=True)
    aeroway = models.TextField(blank=True, null=True)
    amenity = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    barrier = models.TextField(blank=True, null=True)
    bicycle = models.TextField(blank=True, null=True)
    brand = models.TextField(blank=True, null=True)
    bridge = models.TextField(blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    construction = models.TextField(blank=True, null=True)
    covered = models.TextField(blank=True, null=True)
    culvert = models.TextField(blank=True, null=True)
    cutting = models.TextField(blank=True, null=True)
    denomination = models.TextField(blank=True, null=True)
    disused = models.TextField(blank=True, null=True)
    embankment = models.TextField(blank=True, null=True)
    foot = models.TextField(blank=True, null=True)
    # Field renamed to remove unsuitable characters.
    generator_source = models.TextField(
        db_column='generator:source', blank=True, null=True)
    harbour = models.TextField(blank=True, null=True)
    highway = models.TextField(blank=True, null=True)
    historic = models.TextField(blank=True, null=True)
    horse = models.TextField(blank=True, null=True)
    intermittent = models.TextField(blank=True, null=True)
    junction = models.TextField(blank=True, null=True)
    landuse = models.TextField(blank=True, null=True)
    layer = models.TextField(blank=True, null=True)
    leisure = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    man_made = models.TextField(blank=True, null=True)
    military = models.TextField(blank=True, null=True)
    motorcar = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    natural = models.TextField(blank=True, null=True)
    office = models.TextField(blank=True, null=True)
    oneway = models.TextField(blank=True, null=True)
    operator = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)
    population = models.TextField(blank=True, null=True)
    power = models.TextField(blank=True, null=True)
    power_source = models.TextField(blank=True, null=True)
    public_transport = models.TextField(blank=True, null=True)
    railway = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    religion = models.TextField(blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    service = models.TextField(blank=True, null=True)
    shop = models.TextField(blank=True, null=True)
    sport = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    toll = models.TextField(blank=True, null=True)
    tourism = models.TextField(blank=True, null=True)
    # Field renamed to remove unsuitable characters.
    tower_type = models.TextField(
        db_column='tower:type', blank=True, null=True)
    tracktype = models.TextField(blank=True, null=True)
    tunnel = models.TextField(blank=True, null=True)
    water = models.TextField(blank=True, null=True)
    waterway = models.TextField(blank=True, null=True)
    wetland = models.TextField(blank=True, null=True)
    width = models.TextField(blank=True, null=True)
    wood = models.TextField(blank=True, null=True)
    z_order = models.IntegerField(blank=True, null=True)
    way_area = models.FloatField(blank=True, null=True)
    way = models.LineStringField(srid=3857, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planet_osm_line'

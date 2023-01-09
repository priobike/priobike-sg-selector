from xml.etree import ElementTree

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from routing.models import LSACrossing


class Command(BaseCommand):
    """
    Load crossings from a GML file. The GML file structure is as follows:

    <?xml version='1.0' encoding='UTF-8'?>
    <wfs:FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd http://www.deegree.org/app https://geodienste.hamburg.de/HH_WFS_Lichtsignalanlagen?SERVICE=WFS&amp;VERSION=2.0.0&amp;REQUEST=DescribeFeatureType&amp;OUTPUTFORMAT=application%2Fgml%2Bxml%3B+version%3D3.2&amp;TYPENAME=app:lsa_knotengrunddaten&amp;NAMESPACES=xmlns(app,http%3A%2F%2Fwww.deegree.org%2Fapp)" xmlns:wfs="http://www.opengis.net/wfs/2.0" timeStamp="2022-10-05T06:56:21Z" xmlns:gml="http://www.opengis.net/gml/3.2" numberMatched="unknown" numberReturned="0">
        <!--NOTE: numberReturned attribute should be 'unknown' as well, but this would not validate against the current version of the WFS 2.0 schema (change upcoming). See change request (CR 144): https://portal.opengeospatial.org/files?artifact_id=43925.-->
        <wfs:member>
            <app:lsa_knotengrunddaten xmlns:app="http://www.deegree.org/app" gml:id="APP_LSA_KNOTENGRUNDDATEN_1747">
            <app:knoten>2</app:knoten>
            <app:art>K    </app:art>
            <app:LSA_Name>Osterstraße / Eppendorfer Weg                                                                         </app:LSA_Name>
            <app:geom>
                <!--Inlined geometry 'APP_LSA_KNOTENGRUNDDATEN_1747_APP_GEOM'-->
                <gml:MultiPoint gml:id="APP_LSA_KNOTENGRUNDDATEN_1747_APP_GEOM" srsName="EPSG:25832">
                <gml:pointMember>
                    <gml:Point gml:id="GEOMETRY_d391aef8-2556-4bc9-861e-859b7006975e" srsName="EPSG:25832">
                    <gml:pos>563664.000 5936542.000</gml:pos>
                    </gml:Point>
                </gml:pointMember>
                </gml:MultiPoint>
            </app:geom>
            </app:lsa_knotengrunddaten>
        </wfs:member>
        ...
    </wfs:FeatureCollection>

    We convert each of the <wfs:member> elements into a Crossing object.
    This contains the fields: id, name, node, point.
    """

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        gml_file = options['file']
        with open(gml_file, 'r') as f:
            gml = f.read()

        # Parse the GML file
        root = ElementTree.fromstring(gml)

        # Delete all existing crossings
        LSACrossing.objects.all().delete()

        # Get all <wfs:member> elements
        members = root.findall('{http://www.opengis.net/wfs/2.0}member')

        # Persist each <wfs:member> element as a Crossing object
        print(f'Loading {len(members)} crossings...')
        for member in members:
            crossing = LSACrossing()
            node_data_element = member.find('{http://www.deegree.org/app}lsa_knotengrunddaten')
            crossing.name = node_data_element.find('{http://www.deegree.org/app}LSA_Name').text.strip()
            # The gml position is in EPSG:25832 format x y and needs to be converted to EPSG:4326 format y x
            gml_pos = node_data_element \
                .find('{http://www.deegree.org/app}geom') \
                .find('{http://www.opengis.net/gml/3.2}MultiPoint') \
                .find('{http://www.opengis.net/gml/3.2}pointMember') \
                .find('{http://www.opengis.net/gml/3.2}Point') \
                .find('{http://www.opengis.net/gml/3.2}pos') \
                .text.strip()
            x, y = gml_pos.split(' ')
            # Convert to WKT format
            crossing.point = Point(float(x), float(y), srid=25832).transform(settings.LONLAT, clone=True)
            crossing.save()
        print(f'Loaded {len(members)} crossings.')

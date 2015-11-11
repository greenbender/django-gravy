from django.contrib.gis.geos import Point, LinearRing, Polygon
from django.contrib.gis.geoip import GeoIP
from django.conf import settings
import os
import math


__all__ = ['geoip', 'bearing', 'GeoVector', 'GeoCoord', 'GeoPolygon']


import logging
log = logging.getLogger('gravy.geo')


geoip = GeoIP()


# geoip2
try:
    from geoip2.database import Reader
    from geoip2.errors import AddressNotFoundError

    __all__.extend(['geoip2', 'AddressNotFoundError'])

    # TODO: how much work is it to make this GeoIP compatible?
    class GeoIP2(object):
        path = '/usr/share/GeoIP'
        filenames = {
            'city': 'GeoIP2-City.mmdb',
            'country': 'GeoIP2-Country.mmdb',
            'isp': 'GeoIP2-ISP.mmdb',
        }

        def __init__(self, raw=True):
            self.raw = raw
            self.readers = {}

        def __getattr__(self, name):
            if name not in self.readers:
                if name not in self.filenames:
                    return super(GeoIP2, self).__getattr__(name)
                filename = os.path.join(
                    getattr(settings, 'GEOIP_PATH', self.path),
                    getattr(settings, 'GEOIP2_' + name.upper(), self.filenames[name])
                )
                self.readers[name] = Reader(filename)
            return getattr(self.readers[name], name)

    geoip2 = GeoIP2()
except ImportError:
    pass


EARTH_RADIUS = 6378137
COS = [math.cos(math.radians(a)) for a in range(360)]
SIN = [math.sin(math.radians(a)) for a in range(360)]


def _degrees(azimuth):
    return (810 - azimuth) % 360;


def bearing(lat1, lon1, lat2, lon2):
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    rlon1 = math.radians(lon1)
    rlon2 = math.radians(lon2)
    dlon = math.radians(lon2-lon1) 
    b = math.atan2(
        math.sin(dlon) * math.cos(rlat2),
        math.cos(rlat1) * math.sin(rlat2) - \
        math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    )
    bd = math.degrees(b)
    bn = (bd+360)%360
    return bn


class GeoVector(object):
    """
    GeoVector in cartesian space.

    Typical used to represent a distance in metres from the origin when used
    for geographical operations. Can be thought of as the flat earth cartesian
    coordinates, as in, East 2m and North 5m.
    """
    def __init__(self, east, north):
        self.east = east
        self.north = north

    @classmethod
    def OnCircle(cls, radius, angle):
        a = angle % 360
        return cls(radius * COS[a], radius * SIN[a])

    @classmethod
    def OnEllipse(cls, semimajor, semiminor, alpha, beta):
        a = alpha % 360
        b = beta % 360
        return cls(
            semimajor * COS[a] * COS[b] + semiminor * SIN[a] * SIN[b],
            semiminor * SIN[a] * COS[b] - semimajor * COS[a] * SIN[b]
        )


class GeoCoord(object):
    """
    Coordinate on the earth.
    """
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return '(%f, %f)' % (self.latitude, self.longitude)

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def FromGeosPoint(cls, point):
        return cls(point.y, point.x)

    def ToGeosPoint(self):
        return Point(self.longitude, self.latitude)

    def travel(self, vector):
        """
        Get the destination coordinate that results in traveling along the
        given vector from this coordinate.
        """
        latitude = self.latitude + math.degrees(math.asin(vector.north / EARTH_RADIUS))
        longitude = self.longitude + math.degrees(math.asin(vector.east / math.cos(math.radians(latitude)) / EARTH_RADIUS))
        return self.__class__(latitude, longitude)

    def bearing(self, other):
        return bearing(self.latitude, self.longitude, other.latitude, other.longitude)


class GeoPolygon(object):
    """
    Polygon on the earth.
    """
    def __init__(self, *vertices):
        self.vertices = vertices

    def __iter__(self):
        return iter(self.vertices)

    @classmethod
    def FromCircle(cls, origin, radius, step=10):
        vertices = []
        for d in range(0, 360, step):
            vertices.append(origin.travel(GeoVector.OnCircle(radius, _degrees(d))))
        vertices.append(vertices[0])
        return cls(*vertices)

    @classmethod
    def FromEllipse(cls, origin, semimajor, semiminor, angle, step=10):
        vertices = []
        for d in range(360, 0, -step):
            vertices.append(origin.travel(GeoVector.OnEllipse(semimajor, semiminor, _degrees(d), angle)))
        vertices.append(vertices[0])
        return cls(*vertices)

    @classmethod
    def FromArc(cls, origin, inradius, outradius, startangle, stopangle, step=10):
        vertices = []
        align = stopangle + step
        if inradius:
            for d in range(startangle, stopangle, step):
                vertices.append(origin.travel(GeoVector.OnCircle(inradius, _degrees(d))))
            align = d
            vertices.append(origin.travel(GeoVector.OnCircle(inradius, _degrees(stopangle))))
        else:
            vertices.append(origin)
        vertices.append(origin.travel(GeoVector.OnCircle(outradius, _degrees(stopangle))))
        for d in range(align, startangle, -step):
            vertices.append(origin.travel(GeoVector.OnCircle(outradius, _degrees(d))))
        vertices.append(origin.travel(GeoVector.OnCircle(outradius, _degrees(startangle))))
        vertices.append(vertices[0])        
        return cls(*vertices)

    def ToGeosPolygon(self):
        return Polygon(LinearRing([v.ToGeosPoint() for v in self.vertices]))

    def _split_into_chunks(self, value):
        while value >= 32: #2^5, while there are at least 5 bits
            # first & with 2^5-1, zeros out all the bits other than the first five
            # then OR with 0x20 if another bit chunk follows
            yield (value & 31) | 0x20 
            value >>= 5
        yield value

    def _encode_value(self, value):
        # Step 2 & 4
        value = ~(value << 1) if value < 0 else (value << 1)
        # Step 5 - 8
        chunks = self._split_into_chunks(value)
        # Step 9-10
        return (chr(chunk + 63) for chunk in chunks)

    def encode(self):
        """
        Encodes a polyline using Google"s polyline algorithm
        
        See http://code.google.com/apis/maps/documentation/polylinealgorithm.html 
        for more information.
        """
        result = []
        prev_lat = 0
        prev_lng = 0
        for vertex in self:        
            lat, lng = int(vertex.latitude * 1e5), int(vertex.longitude * 1e5)
            d_lat = self._encode_value(lat - prev_lat)
            d_lng = self._encode_value(lng - prev_lng)
            prev_lat, prev_lng = lat, lng
            result.append(d_lat)
            result.append(d_lng)
        return ''.join(c for r in result for c in r)

    def centroid(self):
        result = GeoCoord(0.0, 0.0)
        signedArea = 0.0
        v0 = self.vertices[0]
        for i, v1 in enumerate(self.vertices[1:]):
            a = v0.latitude * v1.longitude - v0.longitude * v1.latitude
            signedArea += a
            result.latitude += (v0.latitude + v1.latitude) * a
            result.longitude += (v0.longitude + v1.longitude) * a
            v0 = v1
        signedArea *= 0.5
        result.latitude /= (6.0 * signedArea)
        result.longitude /= (6.0 * signedArea)
        return result

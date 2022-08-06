var map;

function init(accessToken, minLongitude, maxLongitude, minLatitude, maxLatitude, locations) {
    mapboxgl.accessToken = accessToken

    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/outdoors-v11',
        center: [(minLongitude+maxLongitude)/2, (minLatitude+maxLatitude)/2],
        zoom: 12,
        pitch: 60,
        bearing: 0
    });

    map.addControl(new mapboxgl.NavigationControl());

    map.on('load', function () {
        map.addSource('mapbox-dem', {
            'type': 'raster-dem',
            'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
            'tileSize': 512,
            'maxzoom': 14
        });

        map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.0 });

        map.addLayer({
            'id': 'sky',
            'type': 'sky',
            'paint': {
                'sky-opacity': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    0,
                    0,
                    5,
                    0.3,
                    8,
                    1
                ],
                'sky-type': 'atmosphere',
                'sky-atmosphere-sun': getSunPosition(),
                'sky-atmosphere-sun-intensity': 5
            }
        });

        map.fitBounds([
            [minLongitude, minLatitude], 
            [maxLongitude, maxLatitude]
        ]);

        addTrack(locations);

    });
}

function getSunPosition() {
    var center = map.getCenter();
    var sunPos = SunCalc.getPosition(
        Date.now(),
        center.lat,
        center.lng
    );
    var sunAzimuth = 180 + (sunPos.azimuth * 180) / Math.PI;
    var sunAltitude = 90 - (sunPos.altitude * 180) / Math.PI;
    return [sunAzimuth, sunAltitude];
}

function addTrack(locations) {
    mapTracks = [];
    mapCoordinates = [];
    
    locations.forEach(function(location) {
        mapCoordinates.push('['+location[0]+','+ location[1]+']');
    })

    mapTracks.push(JSON.parse('{"type": "Feature", "properties": {}, "geometry": {"type": "LineString", "coordinates": ['+mapCoordinates+']}}'));

    if (map.getLayer('route')) map.removeLayer('route');
    if (map.getSource('route')) map.removeSource('route');

    map.addSource('route', {
        'type': 'geojson',
        'data': {
            "type": "FeatureCollection",
            "features": mapTracks
        }
    });

    map.addLayer({
        'id': 'route',
        'type': 'line',
        'source': 'route',
        'layout': {
        'line-join': 'round',
        'line-cap': 'round'
        },
        'paint': {
            'line-width': {stops: [[0, 1], [5, 2.5], [10, 5]]},
            'line-color': '#808080'
        }
    });
}
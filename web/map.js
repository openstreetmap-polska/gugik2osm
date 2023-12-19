mapboxgl.accessToken = 'pk.eyJ1IjoidG9tYXN6dCIsImEiOiJjazg2Nno3ZWswZDZ5M2ZvdHdxejFnbGNmIn0.P4_K-eykAt7kpVVq0GrESQ';
var updatesLayerURL = "https://budynki.openstreetmap.org.pl/updates.geojson";
var vectorTilesURL = "https://budynki.openstreetmap.org.pl/tiles/{z}/{x}/{y}.pbf";
var overpass_layers_url = "https://budynki.openstreetmap.org.pl/overpass-layers.json";
var downloadable_layers_url = "https://budynki.openstreetmap.org.pl/layers/";

const defaultCenter = [19.76231, 52.51863];
const defaultZoom = 13;
var initialZoom = defaultZoom;
var initialCenter = defaultCenter;
if (document.cookie.search("map_position") !== -1) {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('map_position='))
      .split('=')[1];
    const obj = JSON.parse(cookieValue);
    initialCenter = obj.center;
    initialZoom = obj.zoom;
    console.log('Found location in cookie from last session. Will use it.')
}

var map = new mapboxgl.Map({
    "container": "map",
    "hash": "map",
    "zoom": initialZoom,
    "center": initialCenter,
    "minZoom": 6,
    "maxZoom": 19,
    "maxPitch": 0,
    "dragRotate": false,
    "style": {
        "version": 8,
        "sources": {
            "raster-tiles": {
                "type": "raster",
                "tiles": [
                    "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                ],
                "tileSize": 256,
                "minzoom": 0,
                "maxzoom": 19,
                "attribution": "dane <a class=\"text-primary\" href=https://www.openstreetmap.org/copyright>OpenStreetMap ©</a>"
            },
            "pol-raster-tiles": {
                "type": "raster",
                "tiles": [
                    "https://tiles.osmapa.pl/hot/{z}/{x}/{y}.png"
                ],
                "tileSize": 256,
                "attribution": "dane <a class=\"text-primary\" href=https://www.openstreetmap.org/copyright>OpenStreetMap ©</a>; mapa <a class=\"text-primary\" href=https://tiles.osmapa.pl>tiles.osmapa.pl</a>"
            },
            "geoportal": {
                "type": "raster",
                "tileSize": 256,
                "tiles": [
                    "https://budynki.openstreetmap.org.pl/orto?bbox={bbox-epsg-3857}&FORMAT=image/jpeg&STYLES=&service=WMS&version=1.3.0&request=GetMap&crs=EPSG:3857&width=256&height=256&LAYERS=Raster"
                ],
                "attribution": "© <a href=https://geoportal.gov.pl>geoportal.gov.pl</a>"
            },
            "mvt-tiles": {
                "type": "vector",
                "maxzoom": 14,
                "tiles": [
                    vectorTilesURL
                ]
            },
            "updates": {
                "type": "geojson",
                "data": updatesLayerURL
            }
        },
        "glyphs": "https://fonts.openmaptiles.org/{fontstack}/{range}.pbf",
        "layers": [
            {
                "id": "simple-tiles",
                "type": "raster",
                "source": "raster-tiles"
//            }, {
//                "id": "polish-tiles",
//                "type": "raster",
//                "source": "pol-raster-tiles",
//                "minzoom": 5,
//                "maxzoom": 20
            }, {
                "id": "buildings",
                "type": "fill",
                "source": "mvt-tiles",
                "source-layer": "buildings",
                "minzoom": 13,
                "paint": {
                    "fill-color": "red",
                    "fill-opacity": 0.7
                }
            }, {
                "id": "buildings-as-points",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "buildings_centroids",
                "minzoom": 11,
                "maxzoom": 13,
                "paint": {
                    "circle-radius": [
                        "step",
                        ["zoom"],
                            2,
                        12, 3,
                    ],
                    "circle-color": "red",
                    "circle-opacity": 0.5
                },
            }, {
                "id": "buildings-clustered-6-7",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "buildings_clustered",
                "minzoom": 6,
                "maxzoom": 7,
//                "layout":{
//                    "circle-sort-key": ["get", "no_of_points"],
//                },
                "paint": {
                    "circle-radius": [
                        "step",
                        ["get", "no_of_points"],
                                2,
                           50,  3,
                          100,  5,
                          200,  7,
                          400,  9,
                          800, 11,
                         1600, 13,
                         3200, 15,
                         6400, 17,
                        12800, 19,
                        25600, 21,
                        51200, 23,
                    ],
                    "circle-color": "red",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 0.2,
                    "circle-opacity": 0.5
                },
                "filter": [">", "no_of_points", 4],
            }, {
                "id": "buildings-clustered-8-10",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "buildings_clustered",
                "minzoom": 7,
                "maxzoom": 11,
                "layout":{
                    "circle-sort-key": ["get", "no_of_points"],
                },
                "paint": {
                    "circle-radius": [
                        "step",
                        ["get", "no_of_points"],
                                2,
                           10,  3,
                           30,  5,
                           75,  7,
                          100,  9,
                          200, 11,
                          300, 13,
                          400, 15,
                          500, 17,
                          600, 19,
                          700, 21,
                          800, 23,
                    ],
                    "circle-color": "red",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.5
                }
            }, {
                "id": "addresses-clustered-6",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "addresses_clustered",
                "minzoom": 6,
                "maxzoom": 7,
//                "layout":{
//                    "circle-sort-key": ["get", "no_of_points"],
//                },
                "paint": {
                    "circle-radius": [
                        "step",
                        ["get", "no_of_points"],
                                2,
                           50,  3,
                          100,  5,
                          200,  7,
                          400,  9,
                          800, 11,
                         1600, 13,
                         3200, 15,
                         6400, 17,
                        12800, 19,
                        25600, 21,
                        51200, 23,
                    ],
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 0.2,
                    "circle-opacity": 0.5
                },
                "filter": [">", "no_of_points", 4],
            }, {
                "id": "addresses-clustered-7-10",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "addresses_clustered",
                "minzoom": 7,
                "maxzoom": 11,
                "layout":{
                    "circle-sort-key": ["get", "no_of_points"],
                },
                "paint": {
                    "circle-radius": [
                        "step",
                        ["get", "no_of_points"],
                                2,
                           10,  3,
                           30,  5,
                           75,  7,
                          100,  9,
                          200, 11,
                          300, 13,
                          400, 15,
                          500, 17,
                          600, 19,
                          700, 21,
                          800, 23,
                    ],
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.5
                }
            }, {
                "id": "addresses-clustered-label-7",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "addresses_clustered",
                "minzoom": 7,
                "maxzoom": 8,
                "layout": {
                    "text-field": "{no_of_points}",
                    "text-font": ["Metropolis Regular"],
                    "text-size": [
                        "step",
                        ["get", "no_of_points"],
                               6,
                          30,  9,
                          50, 12,
                         250, 14,
                        1000, 16,
                    ],
                    "text-variable-anchor": ["center"],
                    "text-justify": "center",
                    "symbol-sort-key": ["*", -1, ["get", "no_of_points"]],
                },
                "paint": {
                    "text-halo-color": "white",
                    "text-halo-width": [
                        "step",
                        ["get", "no_of_points"],
                             1,
                        500, 2,
                    ],
                    "text-halo-blur": 1,
                },
                "filter": [">", "no_of_points", 1000],
            }, {
                "id": "addresses-clustered-label-8-10",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "addresses_clustered",
                "minzoom": 8,
                "maxzoom": 11,
                "layout": {
                    "text-field": "{no_of_points}",
                    "text-font": ["Metropolis Regular"],
                    "text-size": [
                        "step",
                        ["get", "no_of_points"],
                               6,
                          30,  9,
                          50, 12,
                         250, 14,
                        1000, 16,
                    ],
                    "text-variable-anchor": ["center"],
                    "text-justify": "center",
                    "symbol-sort-key": ["*", -1, ["get", "no_of_points"]],
                },
                "paint": {
                    "text-halo-color": "white",
                    "text-halo-width": [
                        "step",
                        ["get", "no_of_points"],
                             1,
                        500, 2,
                    ],
                    "text-halo-blur": 1,
                },
                "filter": [">", "no_of_points", 100],
            }, {
                "id": "buildings-clustered-label-7",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "buildings_clustered",
                "minzoom": 7,
                "maxzoom": 8,
                "layout": {
                    "text-field": "{no_of_points}",
                    "text-font": ["Metropolis Regular"],
                    "text-size": [
                        "step",
                        ["get", "no_of_points"],
                               6,
                          30,  9,
                          50, 12,
                         250, 14,
                        1000, 16,
                    ],
                    "text-variable-anchor": ["center"],
                    "text-justify": "center",
                    "symbol-sort-key": ["*", -1, ["get", "no_of_points"]],
                },
                "paint": {
                    "text-halo-color": "white",
                    "text-halo-width": [
                        "step",
                        ["get", "no_of_points"],
                             1,
                        500, 2,
                    ],
                    "text-halo-blur": 1,
                },
                "filter": [">", "no_of_points", 1000],
            }, {
                "id": "buildings-clustered-label-8-10",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "buildings_clustered",
                "minzoom": 8,
                "maxzoom": 11,
                "layout": {
                    "text-field": "{no_of_points}",
                    "text-font": ["Metropolis Regular"],
                    "text-size": [
                        "step",
                        ["get", "no_of_points"],
                               6,
                          30,  9,
                          50, 12,
                         250, 14,
                        1000, 16,
                    ],
                    "text-variable-anchor": ["center"],
                    "text-justify": "center",
                    "symbol-sort-key": ["*", -1, ["get", "no_of_points"]],
                },
                "paint": {
                    "text-halo-color": "white",
                    "text-halo-width": [
                        "step",
                        ["get", "no_of_points"],
                             1,
                        500, 2,
                    ],
                    "text-halo-blur": 1,
                },
                "filter": [">", "no_of_points", 100],
            }, {
                "id": "addresses-geomonly",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "addresses_geomonly",
                "minzoom": 11,
                "maxzoom": 13,
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 0,
                    "circle-opacity": 0.5
                }
            }, {
                "id": "addresses",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "addresses",
                "minzoom": 13,
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.9
                }
            }, {
                "id": "addresses-house-numbers",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "addresses",
                "minzoom": 15,
                "layout": {
                    "text-field": "{nr}",
                    "text-font": ["Metropolis Regular"],
                    "text-size": 12,
                    "text-variable-anchor": ["bottom"],
                    "text-justify": "center"
                },
                "paint": {
                    "text-halo-color": "white",
                    "text-halo-width": 2
                }
            }, {
                "id": "osm-updates",
                "type": "fill",
                "source": "updates",
                "paint": {
                "fill-color": "#0099ff",
                "fill-opacity": 0.4
                },
                "filter": ["==", "dataset", "osm"]
            }, {
                "id": "gugik2osm-exports",
                "type": "fill",
                "source": "updates",
                "paint": {
                "fill-color": "#ff6600",
                "fill-opacity": 0.4
                },
                "filter": ["==", "dataset", "exports"]
            }
        ]
    }
});
console.log('Mapbox GL JS library version: ' + map.version);

map.scrollZoom.setWheelZoomRate(1/100);

map.addControl(
    new MapboxGeocoder({
            accessToken: mapboxgl.accessToken,
            mapboxgl: mapboxgl,
            countries: 'pl',
            language: 'pl-PL',
            types: 'country,region,postcode,district,place,locality,neighborhood,address',
            limit: 10,
            localGeocoder: customGeocode
        })
);

map.addControl(new mapboxgl.NavigationControl());

map.addControl(new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    }
}));

var draw = new MapboxDraw({
    displayControlsDefault: false,
    controls: {
        polygon: true,
        trash: true
    }
});
map.addControl(draw);

map.on('draw.create', openDownloadModalUsingPolygon);
map.on('draw.update', openDownloadModalUsingPolygon);
map.on('draw.delete', openDownloadModalUsingPolygon);

// When a click event occurs on a feature in the states layer, open a popup at the
// location of the click, with description HTML from its properties.
map.on("click", "addresses", function (e) {
    console.log(e.features[0].properties);
    printDebugTileInfo(e.lngLat);
    new mapboxgl.Popup({"maxWidth": "320px"})
    .setLngLat(e.lngLat)
    .setHTML(getAddressPopupHTML(e))
    .addTo(map);
    e.preventDefault();
});
map.on("click", "buildings", function (e) {
    printDebugTileInfo(e.lngLat);
    new mapboxgl.Popup({"maxWidth": "320px"})
    .setLngLat(e.lngLat)
    .setHTML(getBuildingPopupHTML(e))
    .addTo(map);
});

// Change the cursor to a pointer when the mouse is over the states layer.
map.on("mouseenter", "addresses", function () {
    map.getCanvas().style.cursor = "pointer";
});
map.on("mouseenter", "buildings", function () {
    map.getCanvas().style.cursor = "pointer";
});
map.on("mouseenter", "osm-updates", function () {
    map.getCanvas().style.cursor = "pointer";
});
map.on("mouseenter", "gugik2osm-exports", function () {
    map.getCanvas().style.cursor = "pointer";
});

// Change it back to a pointer when it leaves.
map.on("mouseleave", "addresses", function () {
    map.getCanvas().style.cursor = "";
});
map.on("mouseleave", "buildings", function () {
    map.getCanvas().style.cursor = "";
});
map.on("mouseleave", "osm-updates", function () {
    map.getCanvas().style.cursor = "";
});
map.on("mouseleave", "gugik2osm-exports", function () {
    map.getCanvas().style.cursor = "";
});

// https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#ECMAScript_.28JavaScript.2FActionScript.2C_etc..29
function lon2tile(lon,zoom) {
    return (Math.floor((lon+180)/360*Math.pow(2,zoom)));
}
function lat2tile(lat,zoom)  {
    return (Math.floor((1-Math.log(Math.tan(lat*Math.PI/180) + 1/Math.cos(lat*Math.PI/180))/Math.PI)/2 *Math.pow(2,zoom)));
}
function latlon2tileatz18(lngLat) {
    const z = 18;
    const x = lon2tile(lngLat.lng, z);
    const y = lat2tile(lngLat.lat, z);
    return {z: z, x: x, y: y}
}
function printDebugTileInfo(lngLat) {
    const zxy = latlon2tileatz18(lngLat);
    console.log(zxy);
    console.log('For debugging purposes. Object that you clicked is on tile: ' + zxy.z + '/' + zxy.x + '/' + zxy.y);
    console.log('Jeżeli obiekt nie zniknął z mapy po odświeżeniu po kilku minutach od dodania możesz spróbować ' +
                'poprosić o aktualizację tego kafelka jeszcze raz używając linku: ' +
                'https://budynki.openstreetmap.org.pl/tiles/'+ zxy.z + '/' + zxy.x + '/' + zxy.y + '/reload');
}

function getAddressLayers() {
    return map.getStyle().layers.filter(layer => layer.id.startsWith('address'))
}

function getBuildingLayers() {
    return map.getStyle().layers.filter(layer => layer.id.startsWith('building'))
}

// Create a popup, but don't add it to the map yet.
var updates_popup = new mapboxgl.Popup({
    closeButton: false,
    maxWidth: "420px"
});

// Add popup when hovering over updates layer
function prepareUpdatesLayerPopupHTML(features) {
    var popup_text = "";
    var osm_changesets_links = "";
    var last_export_update_ts = "";
    var osm_notification = 0;
    var export_notification = 0;
    features.forEach(function(f){
        if (f.properties.dataset === "osm") {
            osm_notification = 1;
            JSON.parse(f.properties.changesets).forEach(c => {
                const ts = new Date(c.closed_at);
                const formatted_ts = `${ts.getFullYear()}-${String(ts.getMonth()+1).padStart(2,'0')}-${String(ts.getDate()).padStart(2,'0')} ${String(ts.getHours()).padStart(2,'0')}:${String(ts.getMinutes()).padStart(2,'0')}`;
                osm_changesets_links += `<tr><td><a href="https://osm.org/changeset/${c.changeset_id}" `
                osm_changesets_links += `target="_blank" rel="noopener">${c.changeset_id}</a></td>`;
                osm_changesets_links += `<td>${formatted_ts}</td>`
                osm_changesets_links += `<td>${c.osm_user}</td></tr>`
            });
        }
        if (f.properties.dataset === "exports") {
            export_notification = 1;
            if (f.properties.created_at > last_export_update_ts) last_export_update_ts = f.properties.created_at;
        }
    });
    if ((osm_notification + export_notification) > 1) {
        popup_text = "Ktoś niedawno eksportował paczkę danych w tym miejscu! (" + last_export_update_ts + ") <br>";
        popup_text += "Ktoś niedawno modyfikował OSM w tym miejscu! <br>";
        if (osm_changesets_links !== "") {
            popup_text += "<table><tr><th class=\"px-1\">Changeset</th><th class=\"pl-1 pr-5\">Zamknięty</th><th class=\"px-1\">Użytkownik</th></tr>";
            popup_text += osm_changesets_links;
            popup_text += "</table>"
        }
    } else if (osm_notification > 0) {
        popup_text = "Ktoś niedawno modyfikował OSM w tym miejscu! <br>";
        if (osm_changesets_links !== "") {
            popup_text += "<table><tr><th>Changeset</th><th>Zamknięty</th><th>Użytkownik</th></tr>";
            popup_text += osm_changesets_links;
            popup_text += "</table>"
        }
    } else if (export_notification > 0) {
        popup_text = "Ktoś niedawno eksportował paczkę danych w tym miejscu! (" + last_export_update_ts + ")";
    }
    return popup_text
}

function onUpdatesLayerEnterPopup(e) {
    var features = map.queryRenderedFeatures(e.point, {
        layers: ['osm-updates', 'gugik2osm-exports']
    });

    popup_text = prepareUpdatesLayerPopupHTML(features);

    updates_popup
    .setLngLat(e.lngLat)
    .trackPointer()
    .setHTML(popup_text)
    .addTo(map);
}

function onUpdatesLayerClickPopup(e) {
    var features = map.queryRenderedFeatures(e.point, {
        layers: ['osm-updates', 'gugik2osm-exports']
    });

    popup_text = prepareUpdatesLayerPopupHTML(features);

    new mapboxgl.Popup({maxWidth: "420px"})
    .setLngLat(e.lngLat)
    .setHTML(popup_text)
    .addTo(map);
}

function onUpdatesLayerLeavePopup(e) {
    var features = map.queryRenderedFeatures(e.point, {
        layers: ['osm-updates', 'gugik2osm-exports']
    });

    if (!features.length) {
        updates_popup.remove();
        return;
    }

    popup_text = prepareUpdatesLayerPopupHTML(features);

    updates_popup
    .setLngLat(e.lngLat)
    .trackPointer()
    .setText(popup_text)
    .addTo(map);
}

//map.on('mouseenter', 'osm-updates', onUpdatesLayerEnterPopup);
//map.on('mouseleave', 'osm-updates', onUpdatesLayerLeavePopup);

map.on("click", "osm-updates", function (e) {
    printDebugTileInfo(e.lngLat);
    onUpdatesLayerClickPopup(e);
});
map.on("click", "gugik2osm-exports", function (e) {
    printDebugTileInfo(e.lngLat);
    onUpdatesLayerClickPopup(e);
});

//map.on('mouseenter', 'gugik2osm-exports', onUpdatesLayerEnterPopup);
//map.on('mouseleave', 'gugik2osm-exports', onUpdatesLayerLeavePopup);

window.onload = function() {

  var overpassLayersLoaded = false;
  document.getElementById("layerButton").onclick = function() {
    if (!overpassLayersLoaded) {
      // add overpass layers
      fetch(overpass_layers_url)
          .then(response => response.json())
          .then(addOverpassSources)
          .then(insertLayersTogglesIntoDOM);

      overpassLayersLoaded = true;
    }
  }

  document.getElementById("randomLocationButton").onclick = goToRandomLocation;
  document.getElementById("downloadDataForJOSM").onclick = openDownloadModalUsingBbox;
  document.getElementById("addressesLayerToggle").onclick = toggleAddressLayers;
  document.getElementById("buildingsLayerToggle").onclick = toggleBuildingLayers;
  document.getElementById("updatesLayerToggle").onclick = toggleUpdatesLayer;
  document.getElementById("ortoLayerToggle").onclick = toggleOrtoLayer;

  // add layers to layer picker in download modal
  fetch(downloadable_layers_url)
    .then(response => response.json())
    .then(
        data => {
            console.log("Preparing layers for bbox-modal");
            insertDownloadableLayersIntoDOM(data, "layerPicker");
            $("input[name='layerPicker']")
              .on('change', () => {checkLayerPickerAndSetDownloadButtonUrl("layerPicker", "downloadButton", "bbox")});
            console.log("Preparing layers for polygon-modal");
            insertDownloadableLayersIntoDOM(data, "layerPicker2");
            $("input[name='layerPicker2']")
              .on('change', () => {checkLayerPickerAndSetDownloadButtonUrl("layerPicker2", "downloadButton2", "polygon")});
        }
    );
}

async function goToRandomLocation() {
    const o = document.getElementById("ortoLayerToggle");
    var response = await fetch('/random/');
    var location = await response.json();
    console.log(location);
    //disable orto layer if present
    if (o.checked) {
        map.removeLayer("orto");
        toggleMapLayer({id: "simple-tiles", toggle: "on"});
        o.removeAttribute("checked");
    }

    map.flyTo({"center": location, "zoom": 14});
  }

function toggleAddressLayers() {
    const toggleValue = document.getElementById("addressesLayerToggle").checked ? 'on' : 'off';
    getAddressLayers().map(l => ({"id": l.id, "toggle": toggleValue})).forEach(toggleMapLayer);
}

function toggleBuildingLayers() {
    const toggleValue = document.getElementById("buildingsLayerToggle").checked ? 'on' : 'off';
    getBuildingLayers().map(l => ({"id": l.id, "toggle": toggleValue})).forEach(toggleMapLayer);
}

function toggleUpdatesLayer() {
    const toggleValue = document.getElementById("updatesLayerToggle").checked ? 'on' : 'off';

    [
        {id: 'osm-updates', toggle: toggleValue},
        {id: 'gugik2osm-exports', toggle: toggleValue}
    ].forEach(toggleMapLayer);
}

function toggleOrtoLayer() {
    const ortoLayerDefinition = {
        "id": "orto",
        "type": "raster",
        "source": "geoportal",
        "minzoom": 0,
        "maxzoom": 21,
        "visibility": "none"
    };

    // seems like mapbox gl js library still requests tiles even if layer
    // is not visible so we'll just add and remove the layer as needed
    if (document.getElementById("ortoLayerToggle").checked) {
        map.addLayer(ortoLayerDefinition, "simple-tiles");
        toggleMapLayer({id: "simple-tiles", toggle: "off"});
    } else {
        map.removeLayer(ortoLayerDefinition.id);
        toggleMapLayer({id: "simple-tiles", toggle: "on"});
    }
}

function checkLayerPickerAndSetDownloadButtonUrl(layerPickerId, downloadButtonId, modalType) {
    const selector = `input[name="${layerPickerId}"]:checked`;
    if (!$(selector).length) {
        setDummyUrlForDownloadButton(downloadButtonId);
    } else if (modalType === "polygon") {
        setDownloadButtonURlWithPolygon(layerPickerId, downloadButtonId);
    } else if (modalType === "bbox") {
        setDownloadButtonURlWithBbox(layerPickerId, downloadButtonId);
    }
}

function setDummyUrlForDownloadButton(downloadButtonId) {
    document.getElementById(downloadButtonId).href = "javascript:void(0)";
    document.getElementById(downloadButtonId).target = "";
    document.getElementById(downloadButtonId).className = "btn btn-outline-success btn-lg btn-block mt-4";
}

function createUUID() {
    // from https://www.tutorialspoint.com/how-to-create-guid-uuid-in-javascript
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
}

function prepareDownloadableLayerHTML (layer, parentName) {

    var uuid = createUUID();

    var temp = "<div class=\"ml-2 custom-control custom-switch custom-switch-md\">";
    temp += "<input type=\"checkbox\" class=\"custom-control-input\" layerId=\"";
    temp += layer.id + "\" id=\"" + uuid + "\" name=\"" + parentName + "\"";
    if (layer.default) temp += " checked ";
    temp += "><label class=\"custom-control-label pt-1\" for=\"" + uuid + "\">"+ layer.name + " ";
    if (layer.warning != "") {
        temp += "<i class=\"fa fa-exclamation-triangle\" style=\"color:orange\" aria-hidden=\"true\"></i><em class=\"text-muted\">";
        temp += " " + layer.warning + "</em></label>";
    }
    temp += "</div>";
    return temp
}

function insertDownloadableLayersIntoDOM (data, htmlElementId) {
    var raw_html = data.available_layers.map(layer => prepareDownloadableLayerHTML(layer, htmlElementId)).join("\n");
    var html_element = document.getElementById(htmlElementId);
    html_element.innerHTML = raw_html;
}

function insertLayersTogglesIntoDOM (data) {
    var html_element = document.getElementById("overpass-layers-placeholder");
    html_element.insertAdjacentHTML("beforeend", data.html);
    data.layers.forEach(addListenerToLayerToggle);
}

function addListenerToLayerToggle(data) {
    var x = document.getElementById(data.htmlId);
    x.onclick = function(e) {
        var toggleValue = x.checked ? 'on' : 'off';
        data.layersIds.map(id => {return {"id": id, "toggle": toggleValue}}).forEach(toggleMapLayer);
    }
}

function prepareLayersIds(source) {
    return {
        "htmlId": source.id,
        "layersIds": source.layers.map(x => x.id)
    }
}

function addOverpassSources(s) {
    s.sources.forEach(addOverpassSource);
    s.sources.forEach(addOverpassLayers);
    return {
        "html": s.sources.map(prepareSourceHTML).join("\n"),
        "layers": s.sources.map(prepareLayersIds)
    }
}

function addOverpassSource(data) {
    // todo: add support for other values for source parameters (cluster etc)
    var definition = {
        "type": "geojson",
        "data": data.url
    };
    map.addSource(data.id, definition);
}

function addOverpassLayers(data) {
    data.layers.forEach(addOverpassLayer);
}

function addOverpassLayer(layer) {
    map.addLayer(layer);
    map.setLayoutProperty(layer.id, 'visibility', 'none');
}

function prepareSourceHTML(el) {
    var temp = "<br><label class=\"switch\"><input id=" + el.id + " type=\"checkbox\">";
    temp += "<span class=\"slider round\"></span></label>";
    temp += "<label for=" + el.id + ">" + el.name + "</label>";
    return temp
}

function toggleMapLayer(params){
    var layerId = params.id;
    var toggle = params.toggle;

    if (toggle === 'off') {
        map.setLayoutProperty(layerId, 'visibility', 'none');
    } else {
        map.setLayoutProperty(layerId, 'visibility', 'visible');
    }
}

function getBuildingPopupHTML(e) {
    var s = "<table>"
    s += "<tr><td>lokalnyid:</td><td>" + e.features[0].properties.lokalnyid + "</td></tr>"
    s += "<tr><td>status_bdot:</td><td>" + e.features[0].properties.status_bdot + "</td></tr>"
    s += "<tr><td>kategoria_bdot:</td><td>" + e.features[0].properties.kategoria_bdot + "</td></tr>"
    if (e.features[0].properties.funkcja_ogolna_budynku) {
        s += "<tr><td>funkcja_ogolna_budynku:</td><td>" + e.features[0].properties.funkcja_ogolna_budynku + "</td></tr>"
    }
    if (e.features[0].properties.funkcja_szczegolowa_budynku) {
        s += "<tr><td>funkcja_szczegolowa_budynku:</td><td>" + e.features[0].properties.funkcja_szczegolowa_budynku + "</td></tr>"
    }
    if (e.features[0].properties.aktualnosc_geometrii) {
        s += "<tr><td>aktualnosc_geometrii:</td><td>" + e.features[0].properties.aktualnosc_geometrii + "</td></tr>"
    }
    if (e.features[0].properties.aktualnosc_atrybutow) {
        s += "<tr><td>aktualnosc_atrybutow:</td><td>" + e.features[0].properties.aktualnosc_atrybutow + "</td></tr>"
    }
    if (e.features[0].properties.building) {
        s += "<tr><td>building:</td><td>" + e.features[0].properties.building + "</td></tr>"
    }
    if (e.features[0].properties.amenity) {
        s += "<tr><td>amenity:</td><td>" + e.features[0].properties.amenity + "</td></tr>"
    }
    if (e.features[0].properties.man_made) {
        s += "<tr><td>man_made:</td><td>" + e.features[0].properties.man_made + "</td></tr>"
    }
    if (e.features[0].properties.leisure) {
        s += "<tr><td>leisure:</td><td>" + e.features[0].properties.leisure + "</td></tr>"
    }
    if (e.features[0].properties.historic) {
        s += "<tr><td>historic:</td><td>" + e.features[0].properties.historic + "</td></tr>"
    }
    if (e.features[0].properties.tourism) {
        s += "<tr><td>tourism:</td><td>" + e.features[0].properties.tourism + "</td></tr>"
    }
    if (e.features[0].properties.building_levels) {
        s += "<tr><td>building_levels:</td><td>" + e.features[0].properties.building_levels + "</td></tr>"
    }
    s += "</table>"

    s += "<div class=\"accordion\" id=\"accordionBuildingTags\">"
    s += "  <div class=\"card my-2\">"
    s += "    <div class=\"card-header p-0\" id=\"headingBuildingTags\">"
    s += "      <h2 class=\"mb-0\">"
    s += "        <button class=\"btn btn-link btn-block text-left\" type=\"button\" data-toggle=\"collapse\" data-target=\"#collapseBuildingTags\" aria-expanded=\"true\" aria-controls=\"collapseBuildingTags\">"
    s += "          Tagi do skopiowania"
    s += "        </button>"
    s += "      </h2>"
    s += "    </div>"
    s += "    <div id=\"collapseBuildingTags\" class=\"collapse\" aria-labelledby=\"headingBuildingTags\" data-parent=\"#accordionBuildingTags\">"
    s += "      <div class=\"card-body\">"

    if (e.features[0].properties.building) {
        s += "building=" + e.features[0].properties.building + "<br>"
    }
    if (e.features[0].properties.amenity) {
        s += "amenity=" + e.features[0].properties.amenity + "<br>"
    }
    if (e.features[0].properties.man_made) {
        s += "man_made=" + e.features[0].properties.man_made + "<br>"
    }
    if (e.features[0].properties.leisure) {
        s += "leisure=" + e.features[0].properties.leisure + "<br>"
    }
    if (e.features[0].properties.historic) {
        s += "historic=" + e.features[0].properties.historic + "<br>"
    }
    if (e.features[0].properties.tourism) {
        s += "tourism=" + e.features[0].properties.tourism + "<br>"
    }
    if (e.features[0].properties.building_levels) {
        s += "building:levels=" + e.features[0].properties.building_levels + "<br>"
    }
    s += "source:building=BDOT<br>"

    s += "      </div>"
    s += "    </div>"
    s += "  </div>"
    s += "</div>"

    s += "<h6>Jeżeli obiekt nie istnieje lub nie nadaje się do importu zgłoś go:</h6>"
    s += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportBuilding(\""
    s += e.features[0].properties.lokalnyid
    s += "\"); >Zgłoś</button>"
    return s
}

function getAddressPopupHTML(element) {
    var s = "<table>"
    s += "<tr><td>lokalnyid:</td><td>" + element.features[0].properties.lokalnyid + "</td></tr>"
    s += "<tr><td>kod miejscowości:</td><td>" + element.features[0].properties.teryt_simc + "</td></tr>"
    s += "<tr><td>miejscowość:</td><td>" + element.features[0].properties.teryt_msc + "</td></tr>"
    if (element.features[0].properties.teryt_ulica) {
        s += "<tr><td>kod_ulic:</td><td>" + element.features[0].properties.teryt_ulic + "</td></tr>"
        s += "<tr><td>ulica:</td><td>" + element.features[0].properties.teryt_ulica + "</td></tr>"
    }
    s += "<tr><td>numer porządkowy:</td><td>" + element.features[0].properties.nr + "</td></tr>"
    if (element.features[0].properties.pna) {
        s += "<tr><td>kod pocztowy:</td><td>" + element.features[0].properties.pna + "</td></tr>"
    }
    s += "</table>"

    s += "<div class=\"accordion\" id=\"accordionAddressTags\">"
    s += "  <div class=\"card my-2\">"
    s += "    <div class=\"card-header p-0\" id=\"headingAddressTags\">"
    s += "      <h2 class=\"mb-0\">"
    s += "        <button class=\"btn btn-link btn-block text-left\" type=\"button\" data-toggle=\"collapse\" data-target=\"#collapseAddressTags\" aria-expanded=\"true\" aria-controls=\"collapseAddressTags\">"
    s += "          Tagi do skopiowania"
    s += "        </button>"
    s += "      </h2>"
    s += "    </div>"
    s += "    <div id=\"collapseAddressTags\" class=\"collapse\" aria-labelledby=\"headingAddressTags\" data-parent=\"#accordionAddressTags\">"
    s += "      <div class=\"card-body\">"

    s += "addr:city:simc=" + element.features[0].properties.teryt_simc + "<br>"
    if (element.features[0].properties.teryt_ulic) {
        s += "addr:city=" + element.features[0].properties.teryt_msc + "<br>"
        s += "addr:street=" + element.features[0].properties.teryt_ulica + "<br>"
    } else {
        s += "addr:place=" + element.features[0].properties.teryt_msc + "<br>"
    }
    s += "addr:housenumber=" + element.features[0].properties.nr + "<br>"
    if (element.features[0].properties.pna) {
        s += "addr:postcode=" + element.features[0].properties.pna + "<br>"
    }
    s += "source:addr=gugik.gov.pl<br>"

    s += "      </div>"
    s += "    </div>"
    s += "  </div>"
    s += "</div>"

    s += "<h6>Jeżeli obiekt nie istnieje lub nie nadaje się do importu zgłoś go:</h6>"
    s += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportPRG(\""
    s += element.features[0].properties.lokalnyid
    s += "\"); >Zgłoś</button>"
    return s
}

function activateReportButton(){
    $("#reportButton").prop("disabled", false)
}

function onReportComplete(r, status){
    $("#modalSelected").modal('hide');
    if (r.status === 201) {
        $("#modalExclude").modal();
    } else {
        $("#modalExcludeFail").modal();
        console.log(status);
        console.log(r);
    }
}

function reportPRG(id){
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({"prg_ids": [id,]}),
        contentType: "application/json",
        complete: onReportComplete
    })
}

function reportBuilding(id){
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({"bdot_ids": [id,]}),
        contentType: "application/json",
        complete: onReportComplete
    })
}

function reportBoth(encodedStringifiedPayload){
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: decodeURIComponent(encodedStringifiedPayload),
        contentType: "application/json",
        complete: onReportComplete
    })
}

function reportAddressUsingGeom() {
    var unioned = getUnionedDrawnGeometry();
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({
            "exclude_prg_addresses": true,
            "exclude_bdot_buildings": false,
            "geom": JSON.stringify(unioned['geometry'])
        }),
        contentType: "application/json",
        complete: onReportComplete
    });
}

function reportBuildingUsingGeom() {
    var unioned = getUnionedDrawnGeometry();
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({
            "exclude_prg_addresses": false,
            "exclude_bdot_buildings": true,
            "geom": JSON.stringify(unioned['geometry'])
        }),
        contentType: "application/json",
        complete: onReportComplete
    })
}

function reportBothUsingGeom() {
    var unioned = getUnionedDrawnGeometry();
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({
            "exclude_prg_addresses": true,
            "exclude_bdot_buildings": true,
            "geom": JSON.stringify(unioned['geometry'])
        }),
        contentType: "application/json",
        complete: onReportComplete
    })
}

function getUnionedDrawnGeometry() {
    var data = draw.getAll();
    var unioned = data['features'].reduce((previousValue, currentValue, index, array) => {
        return turf.union(previousValue, currentValue)
    });
    return unioned
}

function openDownloadModalUsingBbox(e) {

    // set URL for downloadButton
    setDownloadButtonURlWithBbox("layerPicker", "downloadButton");

    // show modal
    $("#modalDownload").modal();
}

function openDownloadModalUsingPolygon(e) {

    // delete selected feature if delete button was clicked and single feature was selected
    if (e.type === "draw.delete" && e.features.length === 1) {
        draw.delete(e.features[0].id);
        return
    }

    // set URL for downloadButton
    setDownloadButtonURlWithPolygon("layerPicker2", "downloadButton2");

    // show modal
    $("#modalSelected").modal();
}

function getLayerIds(layerPickerId) {
    var layerIds = [];
    var html_elements = document.getElementById(layerPickerId).getElementsByTagName("input");
    for (i = 0; i < html_elements.length; i++) {
        var temp = html_elements.item(i);
        if (temp.checked) layerIds.push(temp.getAttribute("layerId"));
    }
    return layerIds
}

function setDownloadButtonUrlAndStyle(downloadButtonId, theUrl, classes) {
    document.getElementById(downloadButtonId).href = theUrl;
    document.getElementById(downloadButtonId).target = "_blank";
    document.getElementById(downloadButtonId).className = classes;
}

function setDownloadButtonURlWithBbox(layerPickerId, downloadButtonId) {
    var bounds = map.getBounds().toArray();
    var xmin = bounds[0][0];
    var xmax = bounds[1][0];
    var ymin = bounds[0][1];
    var ymax = bounds[1][1];
    var layerIds = getLayerIds(layerPickerId);
    var theUrl = "/josm_data?filter_by=bbox&layers="+layerIds.join(",") + "&xmin="+xmin+"&ymin="+ymin+"&xmax="+xmax+"&ymax="+ymax;
    console.log(theUrl);
    setDownloadButtonUrlAndStyle(downloadButtonId, theUrl, "btn btn-success btn-lg btn-block mt-4")
}

function setDownloadButtonURlWithPolygon(layerPickerId, downloadButtonId) {
    var unioned = getUnionedDrawnGeometry();
    var layerIds = getLayerIds(layerPickerId);
    var theUrl = "/josm_data?filter_by=geojson_geometry&layers="+layerIds.join(",") +"&geom="+ encodeURIComponent(JSON.stringify(unioned['geometry']));
    console.log(theUrl);
    setDownloadButtonUrlAndStyle(downloadButtonId, theUrl, "btn btn-success btn-lg btn-block mt-4")
}

function coordinateFeature(lng, lat) {
    return {
        center: [lng, lat],
        geometry: {
            type: 'Point',
            coordinates: [lng, lat]
        },
        place_name: `Współrzędne: ${lat} ${lng}`,
        place_type: ['coordinate'],
        properties: {},
        type: 'Feature'
    };
}

function prepareCoordinateList(x, y){
    if (x >= 14.0 && x <= 25.0 && y >= 49.0 && y <= 55.0) {
        // x = longitude, y = latitude
        return [coordinateFeature(x, y)]
    } else if (y >= 14.0 && y <= 25.0 && x >= 49.0 && x <= 55.0) {
        // y = longitude, x = latitude
        return [coordinateFeature(y, x)]
    } else {
        // if we can't determine order present both options to the user
        return [coordinateFeature(x, y), coordinateFeature(y, x)]
    }
}

function customGeocode(query) {
    // match anything which looks like a decimal degrees coordinate pair
    // try matching numbers that are a pair of decimal numbers (with comma) separated by space
    var matchesCommaSeparated = query.match(
        /^[ ]*(?:Współrzędne: )?(\d{2}(?:,\d+)?){1}[ ]+(\d{2}(?:,\d+)?){1}[ ]*$/
    );
    // try matching numbers that are a pair of decimal numbers (with period) separated by space or comma
    var matchesPeriodSeparated = query.match(
        /^[ ]*(?:Współrzędne: )?(\d{2}(?:\.\d+)?){1}[, ]+(\d{2}(?:\.\d+)?){1}[ ]*$/
    );
    var matches = matchesPeriodSeparated ? matchesPeriodSeparated : matchesCommaSeparated;
    if (matches) {
        var coord1 = Number(matches[1]);
        var coord2 = Number(matches[2]);
        return prepareCoordinateList(coord1, coord2)
    }

    // in case nothing matches patterns return empty list
    return []

}

// refresh updates layer every 60s
window.setInterval(
    function () {
        console.log("Refreshing layers with updates...")
        map.getSource('updates').setData(updatesLayerURL);
    },
    60000
);

// link to osm that should get updated when user moves around on the map
var osm_link = "https://www.openstreetmap.org/";
window.setInterval(
    function () {
        $("#osm-link")[0].href = osm_link + window.location.hash;
        $("#osm-link-edit-id")[0].href = osm_link + "edit?editor=id" + window.location.hash;
        $("#osm-link-edit-remote")[0].href = osm_link + "edit?editor=remote" + window.location.hash;
        document.cookie = "map_position=" + JSON.stringify({'zoom': map.getZoom(), 'center': map.getCenter()}) + ";max-age="+ 60*60*24*365;
    },
    333
);
//window.addEventListener('hashchange', function() {
//    console.log('TEST');
//    console.log(window.location.hash);
//}, false);

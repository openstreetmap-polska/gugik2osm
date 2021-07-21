mapboxgl.accessToken = 'pk.eyJ1IjoidG9tYXN6dCIsImEiOiJjazg2Nno3ZWswZDZ5M2ZvdHdxejFnbGNmIn0.P4_K-eykAt7kpVVq0GrESQ';
var updatesLayerURL = "https://budynki.openstreetmap.org.pl/updates.geojson";
var vectorTilesURL = "https://budynki.openstreetmap.org.pl/tiles/{z}/{x}/{y}.pbf";
var overpass_layers_url = "https://budynki.openstreetmap.org.pl/overpass-layers.json";
var downloadable_layers_url = "https://budynki.openstreetmap.org.pl/layers/";
var map = new mapboxgl.Map({
    "container": "map",
    "hash": "map",
    "zoom": 13,
    "center": [19.76231, 52.51863],
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
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© <a href=https://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors"
            },
            "pol-raster-tiles": {
            "type": "raster",
            "tiles": [
                "https://tiles.osmapa.pl/hot/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© <a href=https://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors"
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
//                "id": "simple-tiles",
//                "type": "raster",
//                "source": "raster-tiles",
//                "minzoom": 0,
//                "maxzoom": 21
//            }, {
                "id": "polish-tiles",
                "type": "raster",
                "source": "pol-raster-tiles",
                "minzoom": 5,
                "maxzoom": 20
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
                "id": "prg2load_general",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "prg2load_geomonly",
                "minzoom": 6,
                "maxzoom": 13,
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.5
                }
            }, {
                "id": "prg2load",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "prg2load",
                "minzoom": 13,
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "purple",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.9
                }
            }, {
                "id": "house-numbers",
                "type": "symbol",
                "source": "mvt-tiles",
                "source-layer": "prg2load",
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
                "id": "buildings-highlighted",
                "type": "fill",
                "source": "mvt-tiles",
                "source-layer": "buildings",
                "paint": {
                    "fill-outline-color": "#484896",
                    "fill-color": "#6e599f",
                    "fill-opacity": 0.75
                },
                "filter": ["in", "id", ""]
            }, {
                "id": "addresses-highlighted",
                "type": "circle",
                "source": "mvt-tiles",
                "source-layer": "prg2load",
                "paint": {
                    "circle-radius": 3,
                    "circle-color": "yellow",
                    "circle-stroke-color": "white",
                    "circle-stroke-width": 1,
                    "circle-opacity": 0.9
                },
                "filter": ["in", "lokalnyid", ""]
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

map.on('draw.create', selectFeaturesWithPolygon);
map.on('draw.update', selectFeaturesWithPolygon);
map.on('draw.delete', selectFeaturesWithPolygon);

// When a click event occurs on a feature in the states layer, open a popup at the
// location of the click, with description HTML from its properties.
map.on("click", "prg2load", function (e) {
    console.log(e.features[0].properties);
    new mapboxgl.Popup({"maxWidth": "320px"})
    .setLngLat(e.lngLat)
    .setHTML(getPopupText(e))
    .addTo(map);
    e.preventDefault();
});
map.on("click", "buildings", function (e) {
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
        s += "building_levels=" + e.features[0].properties.building_levels + "<br>"
    }
    s += "source=www.geoportal.gov.pl<br>"

    s += "      </div>"
    s += "    </div>"
    s += "  </div>"
    s += "</div>"

    s += "<h6>Jeżeli obiekt nie istnieje lub nie nadaje się do importu zgłoś go:</h6>"
    s += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportBuilding(\""
    s += e.features[0].properties.lokalnyid
    s += "\"); >Zgłoś</button>"
    new mapboxgl.Popup({"maxWidth": "320px"})
    .setLngLat(e.lngLat)
    .setHTML(s)
    .addTo(map);
});

// Change the cursor to a pointer when the mouse is over the states layer.
map.on("mouseenter", "prg2load", function () {
    map.getCanvas().style.cursor = "pointer";
});
map.on("mouseenter", "buildings", function () {
    map.getCanvas().style.cursor = "pointer";
});

// Change it back to a pointer when it leaves.
map.on("mouseleave", "prg2load", function () {
    map.getCanvas().style.cursor = "";
});
map.on("mouseleave", "buildings", function () {
    map.getCanvas().style.cursor = "";
});

// Create a popup, but don't add it to the map yet.
var updates_popup = new mapboxgl.Popup({
    closeButton: false
});

// Add popup when hovering over updates layer
map.on('mousemove', function (e) {
    // update less frequently for less cpu load
    if (Date.now() % 2 === 0) return;

    var features = map.queryRenderedFeatures(e.point, {
        layers: ['osm-updates', 'gugik2osm-exports']
    });

    if (!features.length) {
        updates_popup.remove();
        return;
    }

    var popup_text = "";
    var osm_notification = 0;
    var export_notification = 0;
    features.forEach(function(f){
        if (f.properties.dataset === "osm") osm_notification = 1;
        if (f.properties.dataset === "exports") export_notification = 1;
    });
    if (osm_notification > 0) popup_text += "Ktoś niedawno modyfikował OSM w tym miejscu!\n";
    if (export_notification > 0) popup_text += "Ktoś niedawno eksportował paczkę danych w tym miejscu!\n";

    updates_popup
    .setLngLat(e.lngLat)
    .setText(popup_text)
    .addTo(map);
});
//

map.scrollZoom.setWheelZoomRate(1/100);

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

  var c = document.getElementById("randomLocationButton");
  var d = document.getElementById("downloadButton");

  c.onclick = async function() {
    var response = await fetch('/random/');
    var location = await response.json();
    console.log(location);
    //disable orto layer if present
    var o = document.getElementById("ortoLayerToggle");
    if (o.checked) {
        map.removeLayer("orto");
        toggleMapLayer({id: "simple-tiles", toggle: "on"});
        o.removeAttribute("checked");
    }

    map.flyTo({"center": location, "zoom": 14});
  }
  d.onclick = function() {
    var bounds = map.getBounds().toArray();
    var xmin = bounds[0][0];
    var xmax = bounds[1][0];
    var ymin = bounds[0][1];
    var ymax = bounds[1][1];
    var html_elements = document.getElementById("layerPicker").getElementsByTagName("input");
    var layerIds = [];
    for (i = 0; i < html_elements.length; i++) {
        var temp = html_elements.item(i);
        if (temp.checked) layerIds.push(temp.getAttribute("id"));
    }
    console.log(layerIds);
    var theUrl = "/josm_data?filter_by=bbox&xmin="+xmin+"&ymin="+ymin+"&xmax="+xmax+"&ymax="+ymax+"&layers="+layerIds.join(",");
    console.log(theUrl);
    window.open(theUrl);
  }

  var a = document.getElementById("addressesLayerToggle");
  var b = document.getElementById("buildingsLayerToggle");
  var o = document.getElementById("ortoLayerToggle");
  var u = document.getElementById("updatesLayerToggle");

  a.onclick = function(e) {
    var toggleValue = a.checked ? 'on' : 'off';

    [
        {id: 'prg2load', toggle: toggleValue},
        {id: 'prg2load_general', toggle: toggleValue},
        {id: 'addresses-highlighted', toggle: toggleValue},
        {id: 'house-numbers', toggle: toggleValue}
    ].forEach(toggleMapLayer);
  }
  b.onclick = function(e) {
    var toggleValue = b.checked ? 'on' : 'off';

    [
        {id: 'buildings', toggle: toggleValue},
        {id: 'buildings-highlighted', toggle: toggleValue}
    ].forEach(toggleMapLayer);
  }
  u.onclick = function(e) {
    var toggleValue = u.checked ? 'on' : 'off';

    [
        {id: 'osm-updates', toggle: toggleValue},
        {id: 'gugik2osm-exports', toggle: toggleValue}
    ].forEach(toggleMapLayer);
  }
  o.onclick = function(e) {
    var ortoLayerDefinition = {
        "id": "orto",
        "type": "raster",
        "source": "geoportal",
        "minzoom": 0,
        "maxzoom": 21,
        "visibility": "none"
    };

    // seems like mapbox gl js library still requests tiles even if layer
    // is not visible so we'll just add and remove the layer as needed
    if (o.checked) {
        map.addLayer(ortoLayerDefinition, "simple-tiles");
        toggleMapLayer({id: "simple-tiles", toggle: "off"});
    } else {
        map.removeLayer(ortoLayerDefinition.id);
        toggleMapLayer({id: "simple-tiles", toggle: "on"});
    }
  }

  // add layers to layer picker in download modal
  fetch(downloadable_layers_url)
    .then(response => response.json())
    .then(insertDownloadableLayersIntoDOM);

}

function prepareDownloadableLayerHTML (layer) {
//    var temp = "<br><label class=\"switch\"><input id=" + layer.id + " type=\"checkbox\"";
//    if (layer.default) temp += " checked ";
//    temp += "><span class=\"slider round\"></span></label>";
//    temp += "<label for=" + layer.id + ">" + layer.name + "</label>";

    var temp = "<div class=\"ml-2 custom-control custom-switch custom-switch-md\">";
    temp += "<input type=\"checkbox\" class=\"custom-control-input\" id=\"" + layer.id + "\"";
    if (layer.default) temp += " checked ";
    temp += "><label class=\"custom-control-label pt-1\" for=\"" + layer.id + "\">"+ layer.name + " ";
    if (layer.warning != "") {
        temp += "<i class=\"fa fa-exclamation-triangle\" style=\"color:orange\" aria-hidden=\"true\"></i><em class=\"text-muted\">";
        temp += " " + layer.warning + "</em></label>";
    }
    temp += "</div>";
    return temp
}

function insertDownloadableLayersIntoDOM (data) {
    var raw_html = data.available_layers.map(prepareDownloadableLayerHTML).join("\n");
    var html_element = document.getElementById("layerPicker");
    html_element.insertAdjacentHTML("beforeend", raw_html);
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


function getPopupText(element) {
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
    s += "source=gugik.gov.pl<br>"

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

function downloadByIds(encodedStringifiedPayload){
    $.ajax({
        type: "POST",
        url: "/josm_data?filter_by=id",
        data: decodeURIComponent(encodedStringifiedPayload),
        contentType: "application/json",
        dataType: "text",
        success: function(response, status, xhr) {
            // from: https://stackoverflow.com/questions/16086162/handle-file-download-from-ajax-post
            // check for a filename
            var filename = "";
            var disposition = xhr.getResponseHeader('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }

            var type = xhr.getResponseHeader('Content-Type');
            var blob = new Blob([response], { type: type });

            if (typeof window.navigator.msSaveBlob !== 'undefined') {
                // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                window.navigator.msSaveBlob(blob, filename);
            } else {
                var URL = window.URL || window.webkitURL;
                var downloadUrl = URL.createObjectURL(blob);

                if (filename) {
                    // use HTML5 a[download] attribute to specify filename
                    var a = document.createElement("a");
                    // safari doesn't support this yet
                    if (typeof a.download === 'undefined') {
                        window.location.href = downloadUrl;
                    } else {
                        a.href = downloadUrl;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                    }
                } else {
                    window.location.href = downloadUrl;
                }

                setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
            }
        }
    })
}

function selectFeaturesWithPolygon(e) {
    // get polygons drawn
    var data = draw.getAll();

    if (e.type === "draw.delete" && e.features.length === 1){
        draw.delete(e.features[0].lokalnyid);
        return
    }

    var filterBuildings = ["in", "lokalnyid"];
    var tempSetBuildings = new Set();
    var filterAddresses = ["in", "lokalnyid"];
    var tempSetAddresses = new Set();

    // for each drawn polygon
    data.features.forEach(function(userPolygon){
        // generate bounding box from polygon the user drew
        var polygonBoundingBox = turf.bbox(userPolygon);

        var southWest = [polygonBoundingBox[0], polygonBoundingBox[1]];
        var northEast = [polygonBoundingBox[2], polygonBoundingBox[3]];

        var northEastPointPixel = map.project(northEast);
        var southWestPointPixel = map.project(southWest);

        // first select features by bounding box
        var featuresBuildings = map.queryRenderedFeatures([southWestPointPixel, northEastPointPixel], { layers: ['buildings'] });
        var featuresAddresses = map.queryRenderedFeatures([southWestPointPixel, northEastPointPixel], { layers: ['prg2load'] });

        // then for each selected feature verify if it intersects the polygon and add it's id to the list of selected features
        var temp = featuresBuildings.reduce(function(memo, feature) {
            if (!turf.booleanDisjoint(feature, userPolygon)) {
                memo.push(feature.properties.lokalnyid);
            }
            return memo;
        }, []);
        temp.forEach(function(e){tempSetBuildings.add(e)});

        var temp = featuresAddresses.reduce(function(memo, feature) {
            if (!turf.booleanDisjoint(feature, userPolygon)) {
                memo.push(feature.properties.lokalnyid);
            }
            return memo;
        }, []);
        temp.forEach(function(e){tempSetAddresses.add(e)});
    });

    // prepare filters for the highlight layers
    filterBuildings = filterBuildings.concat(...tempSetBuildings);
    filterAddresses = filterAddresses.concat(...tempSetAddresses);

    // apply filters showing selected objects via the highlight layers
    map.setFilter("buildings-highlighted", filterBuildings);
    map.setFilter("addresses-highlighted", filterAddresses);

    // set modal's content
    var noOfBuildingsHTML = "<p>Zaznaczono " + tempSetBuildings.size + " budynków.</p>"
    var noOfAddressesHTML = "<p>Zaznaczono " + tempSetAddresses.size + " adresów.</p>"
    var downloadSelectedButton = "<br><button id=\"downloadSelectedButton\" type=\"button\" class=\"btn btn-primary\" onclick=downloadByIds(\""
        downloadSelectedButton += encodeURIComponent(JSON.stringify({
            "addresses_ids": [...tempSetAddresses],
            "buildings_ids": [...tempSetBuildings]
        }))
        downloadSelectedButton += "\"); >Pobierz paczkę JOSM</button><br>"
    var reportButton = "<br><h6>Jeżeli obiekty nie istnieją lub nie nadają się do importu zgłoś je:</h6>"
        reportButton += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportBoth(\""
        reportButton += encodeURIComponent(JSON.stringify({
            "prg_ids": [...tempSetAddresses],
            "bdot_ids": [...tempSetBuildings]
        }))
        reportButton += "\"); >Zgłoś</button>"
    $("#modalSelectedBody").html(noOfBuildingsHTML + noOfAddressesHTML + downloadSelectedButton + reportButton);
    // show modal
    $("#modalSelected").modal();
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
    },
    333
);
//$(window).on('hashchange', function() {
//    console.log('TEST');
//    console.log(window.location.hash);
//});

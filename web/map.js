mapboxgl.accessToken = 'pk.eyJ1IjoidG9tYXN6dCIsImEiOiJjazg2Nno3ZWswZDZ5M2ZvdHdxejFnbGNmIn0.P4_K-eykAt7kpVVq0GrESQ';
var reCaptchaPublicToken = "6Lfwg6kZAAAAAAh5yX3y0Nk4XWK-i9tMThhhHgRW";
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
            "mvt-tiles": {
                "type": "vector",
                "tiles": [
                    "https://budynki.openstreetmap.org.pl/tiles/{z}/{x}/{y}.pbf"
                ]
            }
        },
        "glyphs": "https://fonts.openmaptiles.org/{fontstack}/{range}.pbf",
        "layers": [
            {
                "id": "simple-tiles",
                "type": "raster",
                "source": "raster-tiles",
                "minzoom": 0,
                "maxzoom": 21
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
                "id": "buildings",
                "type": "fill",
                "source": "mvt-tiles",
                "source-layer": "lod1_buildings",
                "minzoom": 13,
                "paint": {
                    "fill-color": "red",
                    "fill-opacity": 0.7
                }
            }, {
                "id": "buildings-highlighted",
                "type": "fill",
                "source": "mvt-tiles",
                "source-layer": "lod1_buildings",
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
    grecaptcha.render(
        "recaptcha4addresses", {
        "sitekey": reCaptchaPublicToken,
        "callback": activateReportButton
    });
    e.preventDefault();
    e.stopPropagation();
});
map.on("click", "buildings", function (e) {
    var s = "<h6>Jeżeli obiekt nie istnieje lub nie nadaje się do importu zgłoś go:</h6>"
    s += "<div id=\"recaptcha4buildings\"></div>"
    s += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportLOD1(\""
    s += e.features[0].properties.id
    s += "\"); disabled>Zgłoś</button>"
    new mapboxgl.Popup({"maxWidth": "320px"})
    .setLngLat(e.lngLat)
    .setHTML(s)
    .addTo(map);
    grecaptcha.render(
        "recaptcha4buildings", {
        "sitekey": reCaptchaPublicToken,
        "callback": activateReportButton
    });
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

map.scrollZoom.setWheelZoomRate(1/100);

window.onload = function() {

  var c = document.getElementById("randomLocationButton");
  var d = document.getElementById("downloadButton");

  c.onclick = async function() {
    var response = await fetch('/random/');
    var location = await response.json();
    console.log(location);
    //changed the way view is moved to the new location to flyTo method instead of jumpTo
    //map.jumpTo({"center": location});
    //map.setZoom(14);
    map.flyTo({"center": location, "zoom": 14});
  }
  d.onclick = function() {
    var bounds = map.getBounds().toArray();
    var xmin = bounds[0][0];
    var xmax = bounds[1][0];
    var ymin = bounds[0][1];
    var ymax = bounds[1][1];
    var theUrl = "/josm_data?filter_by=bbox&xmin="+xmin+"&ymin="+ymin+"&xmax="+xmax+"&ymax="+ymax
    console.log(theUrl);
    window.open(theUrl);
  }

  var a = document.getElementById("addressesLayerToggle");
  var b = document.getElementById("buildingsLayerToggle");

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
    if (element.features[0].properties.teryt_ulic) {
        s += "<tr><td>kod_ulic:</td><td>" + element.features[0].properties.teryt_ulic + "</td></tr>"
        s += "<tr><td>ulica:</td><td>" + element.features[0].properties.teryt_ulica + "</td></tr>"
    }
    s += "<tr><td>numer porządkowy:</td><td>" + element.features[0].properties.nr + "</td></tr>"
    if (element.features[0].properties.pna) {
        s += "<tr><td>kod pocztowy:</td><td>" + element.features[0].properties.pna + "</td></tr>"
    }
    s += "</table>"
    s += "<br><h6>Jeżeli obiekt nie istnieje lub nie nadaje się do importu zgłoś go:</h6>"
    s += "<div id=\"recaptcha4addresses\"></div>"
    s += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportPRG(\""
    s += element.features[0].properties.lokalnyid
    s += "\"); disabled>Zgłoś</button>"
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
        headers: {"reCaptchaUserToken": grecaptcha.getResponse()},
        complete: onReportComplete
    })
}

function reportLOD1(id){
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: JSON.stringify({"lod1_ids": [id,]}),
        contentType: "application/json",
        headers: {"reCaptchaUserToken": grecaptcha.getResponse()},
        complete: onReportComplete
    })
}

function reportBoth(encodedStringifiedPayload){
    $.ajax({
        type: "POST",
        url: "/exclude/",
        data: decodeURIComponent(encodedStringifiedPayload),
        contentType: "application/json",
        headers: {"reCaptchaUserToken": grecaptcha.getResponse()},
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
        draw.delete(e.features[0].id);
        return
    }

    var filterBuildings = ["in", "id"];
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
                memo.push(feature.properties.id);
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
        reportButton += "<div id=\"recaptcha4multiselect\"></div>"
        reportButton += "<button id=\"reportButton\" type=\"button\" class=\"btn btn-primary\" onclick=reportBoth(\""
        reportButton += encodeURIComponent(JSON.stringify({
            "prg_ids": [...tempSetAddresses],
            "lod1_ids": [...tempSetBuildings]
        }))
        reportButton += "\"); disabled>Zgłoś</button>"
    $("#modalSelectedBody").html(noOfBuildingsHTML + noOfAddressesHTML + downloadSelectedButton + reportButton);
    grecaptcha.render(
        "recaptcha4multiselect", {
        "sitekey": reCaptchaPublicToken,
        "callback": activateReportButton
    });
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

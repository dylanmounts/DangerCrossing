// Initialize the map
var map = new ol.Map({
    target: 'map',
    controls: ol.control.defaults().extend([new ol.control.FullScreen()]),
    layers: [
        new ol.layer.Tile({
            source: new ol.source.XYZ({
                attributions: [ol.source.OSM.ATTRIBUTION],
                url: "/tile?zoom={z}&x_coord={x}&y_coord={y}.png"
            })
        })
    ],
    view: new ol.View({
        center: ol.proj.fromLonLat([-92.89, 38.525]),
        zoom: 6.45
    })
});

// Initialize the data and point feature
var data = new ol.source.Vector();
var coord;
var lonLat;
var pointFeature;

// Add features from coord list
for (var i = 0; i < coords_list.length; i++) {
    coord = ol.proj.fromLonLat([coords_list[i][0], coords_list[i][1]]);
    lonLat = new ol.geom.Point(coord);
    pointFeature = new ol.Feature({ geometry: lonLat });
    data.addFeature(pointFeature);
}

// Add heatmap layer to the map
var heatMapLayer = new ol.layer.Heatmap({
    source: data,
    opacity: 0.45,
    blur: 20,
    radius: 10
});
map.addLayer(heatMapLayer);

// Set pinch-rotate interaction to false
var interactions = map.getInteractions().getArray();
var pinchRotateInteraction = interactions.filter(function(interaction) {
    return interaction instanceof ol.interaction.PinchRotate;
})[0];
pinchRotateInteraction.setActive(false);

// Define the clustering parameters
var clusterSource = new ol.source.Cluster({
    distance: 60,
    threshold: 2,
    source: data
});

// Add the clusters to the map
map.once('postcompose', function(e) {
    document.querySelector('canvas').style.filter="invert(90%)"; // Dark mode
    var styleCache = {};
    var clusters = new ol.layer.Vector({
        source: clusterSource,
        style: function (feature) {
            var size = feature.get('features').length;
            var style = styleCache[size];
            if (!style) {
                style = new ol.style.Style({
                    image: new ol.style.Circle({  
                        radius: 9,
                        stroke: new ol.style.Stroke({
                            color: '#fff',
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(255, 255, 255, 0.01)',
                        })
                    }),
                    text: new ol.style.Text({
                        text: size.toString(),
                        scale: 0.75,
                        stroke: new ol.style.Stroke({
                            width: 4
                        }),
                        fill: new ol.style.Fill({
                            color: '#fff'
                        })
                    })
                });
                styleCache[size] = style;
            }
            return style;
        }
    });
    map.addLayer(clusters);
});

// Zoom the map in slightly after it loads
map.once('postcompose', function(e) {
    map.getView().animate({
        zoom: map.getView().getZoom() + .55,
        duration: 2000
    });
});
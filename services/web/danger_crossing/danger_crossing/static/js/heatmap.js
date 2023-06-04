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
                if (size === 1) {
                    style = new ol.style.Style({
                        image: new ol.style.Circle({  
                            radius: 10,
                            stroke: new ol.style.Stroke({
                                color: '#007bff',
                            }),
                            fill: new ol.style.Fill({
                                color: 'rgba(0, 123, 255, 0.25)', 
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
                } else {
                    style = new ol.style.Style({
                        image: new ol.style.Circle({  
                            radius: 10,
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
                }
                styleCache[size] = style;
            }
            return style;
        }
    });
    map.addLayer(clusters);

    // Define select interaction
    var select = new ol.interaction.Select({
        layers: function (layer) {
            return layer === clusters; // Only apply the interaction to the cluster layer
        },
        multi: false
    });
    map.addInteraction(select);


    // Add listener for select event on cluster
    select.on('select', function (event) {
        var feature = event.selected[0]; // Get selected feature (the cluster)

        if (feature) {
            // Get the features of the cluster
            var clusterFeatures = feature.get('features');
            
            // Only show the modal if the cluster contains a single item
            if (clusterFeatures.length === 1) {
                // Show the modal
                var myModal = new bootstrap.Modal(document.getElementById('accidentInfoModal'), {});
                myModal.show();
            }
        }
    });

    // Set up pointermove event handler
    map.on('pointermove', function(e) {
        var pixel = map.getEventPixel(e.originalEvent);
        var hit = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            return true;
        });
        if (hit) {
            var features = map.getFeaturesAtPixel(pixel);
            if (features.length > 0 && features[0].get('features')) {
                var size = features[0].get('features').length;
                map.getTargetElement().style.cursor = size === 1 ? 'pointer' : '';
            } else {
                map.getTargetElement().style.cursor = '';
            }
        } else {
            map.getTargetElement().style.cursor = '';
        }
    });
    
});

// Zoom the map in slightly after it loads
map.once('rendercomplete', function(e) {
    map.getView().animate({
        zoom: map.getView().getZoom() + .55,
        duration: 2000
    });
});

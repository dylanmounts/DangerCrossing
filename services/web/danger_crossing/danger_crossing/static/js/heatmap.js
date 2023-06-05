class MapManager {
    constructor() {
        this.data = new ol.source.Vector();
        this.map = this.initializeMap();
        this.addHeatmapLayer();
        this.disablePinchRotate();
        this.clusterPoints();
        this.zoomOnLoad();
    }

    initializeMap() {
        return new ol.Map({
            target: 'map',
            controls: ol.control.defaults().extend([new ol.control.FullScreen()]),
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.XYZ({
                        attributions: [ol.source.OSM.ATTRIBUTION],
                        url: "/get_tile?zoom={z}&x_coord={x}&y_coord={y}.png"
                    })
                })
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([-92.89, 38.525]),
                zoom: 6.45
            })
        });
    }
    addFeatures(coords_dict) {
        this.data.clear()
        console.log("here")
        console.log(Object.keys(coords_dict).length)
        for (let [accident_id, accident_data] of Object.entries(coords_dict)) {
            let coord = ol.proj.fromLonLat([accident_data.lon, accident_data.lat])
            let lonLat = new ol.geom.Point(coord)
            let dateTime = accident_data.date_time
            let pointFeature = new ol.Feature({
                geometry: lonLat,
                accident_id: accident_id,
                date_time: dateTime
            });
            this.data.addFeature(pointFeature);
        }
    }
    addHeatmapLayer() {
        var heatMapLayer = new ol.layer.Heatmap({
            source: this.data,
            opacity: 0.45,
            blur: 20,
            radius: 10
        });
        this.map.addLayer(heatMapLayer);
    }
    disablePinchRotate() {
        var interactions = this.map.getInteractions().getArray();
        var pinchRotateInteraction = interactions.find(function (interaction) {
            return interaction instanceof ol.interaction.PinchRotate;
        });
        pinchRotateInteraction.setActive(false);
    }
    clusterPoints() {
        var clusterSource = new ol.source.Cluster({
            distance: 50,
            threshold: 5,
            source: this.data
        });
    
        // Variable to store the currently selected feature
        var selectedFeature = null;
    
        this.map.once('postcompose', function (e) {
            document.querySelector('canvas').style.filter = "invert(90%)"; // Dark mode
            var styleCache = {};
            var clusters = new ol.layer.Vector({
                source: clusterSource,
                style: function (feature) {
                    var size = feature.get('features').length;
                    var style = styleCache[size];
                    if (!style) {
                        if (size === 1) {
                            style = [
                                new ol.style.Style({
                                    image: new ol.style.RegularShape({
                                        points: 8,
                                        radius: 8,
                                        rotation: Math.PI / 8,
                                        stroke: new ol.style.Stroke({
                                            color: 'rgb(255, 255, 255)',
                                            width: .5
                                        }),
                                        fill: new ol.style.Fill({
                                            color: 'rgb(162, 33, 20)',
                                        }),
                                    }),
                                }),
                                new ol.style.Style({
                                    text: new ol.style.Text({
                                        text: "!",
                                        scale: .9,
                                        textAlign: 'center',
                                        stroke: new ol.style.Stroke({
                                            width: 3
                                        }),
                                        fill: new ol.style.Fill({
                                            color: 'rgb(185, 179, 170)'
                                        })
                                    })
                                })
                            ];
                        } else {
                            style = new ol.style.Style({
                                image: new ol.style.Circle({
                                    radius: 10,
                                    stroke: new ol.style.Stroke({
                                        color: 'rgb(232, 230, 2237)',
                                    }),
                                    fill: new ol.style.Fill({
                                        color: 'rgba(255, 255, 255, .01)'
                                    })
                                }),
                                text: new ol.style.Text({
                                    text: size.toString(),
                                    textAlign: 'center',
                                    stroke: new ol.style.Stroke({
                                        width: 4
                                    }),
                                    fill: new ol.style.Fill({
                                        color: 'rgb(185, 179, 170)'
                                    })
                                })
                            });
                        }
                        styleCache[size] = style;
                    }
                    return style;
                }
            });
            this.addLayer(clusters);
    
            // Define select interaction
            var select = new ol.interaction.Select({
                layers: function (layer) {
                    return layer === clusters; // Only apply the interaction to the cluster layer
                },
                multi: false
            });
            this.addInteraction(select);
    
            // Add listener for select event on cluster
            select.on('select', function (event) {
                var feature = event.selected[0]; // Get selected feature (the cluster)
        
                if (feature) {
                    // Get the features of the cluster
                    var clusterFeatures = feature.get('features');
    
                    // Determine which modal to show based of how many features are in the cluster
                    if (clusterFeatures.length === 1) {
                        selectedFeature = feature;
                        var accident_id = clusterFeatures[0].get("accident_id");
                        $('#accidentInfoModal')
                            .data('accident-id', accident_id)
                            .data('from-cluster-modal', false)
                            .modal('show');
                    } else {
                        selectedFeature = feature;
                        $('#accidentClusterModal')
                            .data('cluster-features', clusterFeatures)
                            .modal('show');
                    }
                }
            });
    
            // Set up pointermove event handler
            this.on('pointermove', function (e) {
                var pixel = this.getEventPixel(e.originalEvent);
                var hit = this.forEachFeatureAtPixel(pixel, function (feature, layer) {
                    return true;
                });
                if (hit) {
                    var features = this.getFeaturesAtPixel(pixel);
                    if (features.length > 0 && features[0].get('features')) {
                        var size = features[0].get('features').length;
                        this.getTargetElement().style.cursor = 'pointer';
                    } else {
                        this.getTargetElement().style.cursor = '';
                    }
                } else {
                    this.getTargetElement().style.cursor = '';
                }
            });
    
            // Event handler for when the modal is dismissed
            $('#accidentInfoModal').on('hidden.bs.modal', function () {
                if (selectedFeature) {
                    // Unselect the selected cluster
                    clusters.getSource().refresh();
                    selectedFeature = null;
                }
            });
            $('#accidentClusterModal').on('hidden.bs.modal', function () {
                if (selectedFeature) {
                    // Unselect the selected cluster
                    clusters.getSource().refresh();
                    selectedFeature = null;
                }
            });
    
            // Event handler for when the modal backdrop is clicked
            $('#accidentInfoModal').on('click', function (e) {
                if (e.target === this && this.selectedFeature) {
                    // Unselect the selected cluster
                    clusters.getSource().refresh();
                    selectedFeature = null;
                }
            });
        });
    }
    zoomOnLoad() {
        this.map.once('rendercomplete', function (e) {
            this.getView().animate({
                zoom: this.getView().getZoom() + 0.55,
                duration: 2000
            });
        });
    }
    submitForm() {
        var $form = $("#date-picker");
        var _this = this;
        $form.on("submit", function(event) {
            event.preventDefault();
            var formData = $form.serialize();
            $.post("/get_map", formData)
                .done(function(response) {
                    _this.addFeatures(response)
                })
                .fail(function() {
                    console.error("Error while updating map");
                })
        });
        $form.trigger("submit");
    }
}

// Instantiate MapManager
let mapManager = new MapManager();

// Attach form submission event
mapManager.submitForm();

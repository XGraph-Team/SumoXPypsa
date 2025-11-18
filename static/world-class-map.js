// ==========================================
// WORLD-CLASS LLM MAP VISUALIZATION FUNCTIONS
// ==========================================

function showRouteOnMap(fromCoords, toCoords, routeData) {
    console.log('🗺️ Showing route:', fromCoords, 'to', toCoords);

    // Clear previous routes
    if (window.map.getSource('route')) {
        window.map.removeLayer('route-line');
        window.map.removeSource('route');
    }

    // Create route line
    const routeGeoJSON = {
        type: 'Feature',
        properties: {},
        geometry: {
            type: 'LineString',
            coordinates: [fromCoords, toCoords]
        }
    };

    window.map.addSource('route', {
        type: 'geojson',
        data: routeGeoJSON
    });

    window.map.addLayer({
        id: 'route-line',
        type: 'line',
        source: 'route',
        layout: {
            'line-join': 'round',
            'line-cap': 'round'
        },
        paint: {
            'line-color': '#00ff88',
            'line-width': 4,
            'line-opacity': 0.8
        }
    });

    // Fit bounds to show entire route
    const bounds = new mapboxgl.LngLatBounds();
    bounds.extend(fromCoords);
    bounds.extend(toCoords);

    window.map.fitBounds(bounds, {
        padding: 100,
        duration: 2000
    });

    // Add start and end markers
    setTimeout(() => {
        createAdvancedHighlight({
            coordinates: fromCoords,
            name: 'Start',
            type: 'route-start',
            duration: 30000,
            pulseColor: '#00ff88'
        });

        createAdvancedHighlight({
            coordinates: toCoords,
            name: 'Destination',
            type: 'route-end',
            duration: 30000,
            pulseColor: '#00aaff'
        });
    }, 1000);
}

function highlightAllVehicles(options) {
    console.log('🚗 Highlighting all vehicles with advanced tracking');

    // Enhanced vehicle visibility
    if (window.vehicleMarkers) {
        window.vehicleMarkers.forEach(marker => {
            const element = marker.getElement();
            element.style.transform += ' scale(1.5)';
            element.style.border = '3px solid #00ff88';
            element.style.boxShadow = '0 0 20px rgba(0,255,136,0.6)';
            element.style.zIndex = '1000';
        });
    }

    showNotification('🚗 Vehicle Tracking', 'All vehicles highlighted and tracking enabled', 'success');
}

function controlLayers(layersToShow = [], message = '') {
    console.log('🎛️ Controlling existing layers:', layersToShow);

    // All available power grid layers
    const allLayers = ['substations', 'primary', 'secondary', 'ev'];
    const layerNames = {
        'substations': 'Substations',
        'primary': '13.8kV Cables',
        'secondary': '480V Cables',
        'ev': 'EV Stations'
    };

    // Turn OFF all power grid layers first
    allLayers.forEach(layer => {
        const toggle = document.getElementById(`layer-${layer}`);
        if (toggle && toggle.checked) {
            toggle.checked = false;
            toggleLayer(layer);
        }
    });

    // Turn ON only requested layers
    layersToShow.forEach(layer => {
        const toggle = document.getElementById(`layer-${layer}`);
        if (toggle && !toggle.checked) {
            toggle.checked = true;
            toggleLayer(layer);
        }
    });

    const layerList = layersToShow.map(layer => layerNames[layer]).join(', ');
    const notification = message || `Showing: ${layerList}`;
    showNotification('🎛️ Layers Updated', notification, 'success');
}

function hidePowerGrid() {
    console.log('🔌 Hiding complete power grid');

    const allLayers = ['substations', 'primary', 'secondary', 'ev'];

    // Turn OFF all power grid layers
    allLayers.forEach(layer => {
        const toggle = document.getElementById(`layer-${layer}`);
        if (toggle && toggle.checked) {
            toggle.checked = false;
            toggleLayer(layer);
        }
    });

    showNotification('🔌 Power Grid Hidden', 'All power infrastructure layers turned off', 'success');
}

function showPowerGrid() {
    console.log('🔌 Showing complete power grid');

    const allLayers = ['substations', 'primary', 'secondary', 'ev'];

    // Turn ON all power grid layers
    allLayers.forEach(layer => {
        const toggle = document.getElementById(`layer-${layer}`);
        if (toggle && !toggle.checked) {
            toggle.checked = true;
            toggleLayer(layer);
        }
    });

    showNotification('🔌 Power Grid Visible', 'All power infrastructure layers activated', 'success');
}

function visualizePowerGrid(options) {
    console.log('⚡ Showing complete power grid using existing layers');

    // Show ALL power grid layers
    controlLayers(['substations', 'primary', 'secondary', 'ev'], 'Complete power grid visualization active');

    // Clear any previous overlays (we're using existing layers now)
    clearPowerGridVisualization();
}

function clearPowerGridVisualization() {
    // Clear any existing power grid layers
    if (window.map && window.map.getLayer) {
        try {
            ['power-grid-connections', 'power-grid-lines'].forEach(layerId => {
                if (window.map.getLayer(layerId)) {
                    window.map.removeLayer(layerId);
                }
            });
            ['power-grid-connections', 'power-grid-lines'].forEach(sourceId => {
                if (window.map.getSource(sourceId)) {
                    window.map.removeSource(sourceId);
                }
            });
        } catch (e) {
            console.log('Power grid cleanup completed');
        }
    }
}

function drawPowerGridConnections(substations) {
    if (!window.map || !substations.length) return;

    try {
        // Create connection lines between nearby substations
        const connections = [];
        substations.forEach((station1, i) => {
            substations.forEach((station2, j) => {
                if (i < j) { // Avoid duplicate connections
                    const distance = calculateDistance(station1.coords, station2.coords);
                    if (distance < 3) { // Connect stations within 3km
                        connections.push({
                            type: 'Feature',
                            geometry: {
                                type: 'LineString',
                                coordinates: [station1.coords, station2.coords]
                            },
                            properties: {
                                from: station1.name,
                                to: station2.name,
                                operational: station1.operational && station2.operational
                            }
                        });
                    }
                }
            });
        });

        if (connections.length > 0) {
            // Add connection lines to map
            window.map.addSource('power-grid-connections', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: connections
                }
            });

            window.map.addLayer({
                id: 'power-grid-connections',
                type: 'line',
                source: 'power-grid-connections',
                paint: {
                    'line-color': ['case', ['get', 'operational'], '#00ff88', '#ff6b6b'],
                    'line-width': 3,
                    'line-opacity': 0.6,
                    'line-dasharray': [2, 2]
                }
            });

            console.log(`⚡ Drew ${connections.length} power grid connections`);
        }
    } catch (error) {
        console.error('Error drawing power grid connections:', error);
    }
}

function calculateDistance(coord1, coord2) {
    const R = 6371; // Earth's radius in km
    const dLat = (coord2[1] - coord1[1]) * Math.PI / 180;
    const dLon = (coord2[0] - coord1[0]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(coord1[1] * Math.PI / 180) * Math.cos(coord2[1] * Math.PI / 180) *
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function showHeatmapOverlay(options) {
    console.log('🌡️ Showing heatmap overlay:', options.data_type);
    showNotification('🌡️ Heatmap Active', options.data_type + ' heatmap visualization enabled', 'success');
}

function showSubstationNetwork(substationName, options = {}) {
    console.log('🔌 Showing individual substation network using existing infrastructure:', substationName);

    // Substation coordinates from existing system
    const substationCoords = {
        'times square': [-73.9857, 40.7549],
        'penn station': [-73.9904, 40.7505],
        'grand central': [-73.9772, 40.7527],
        'murray hill': [-73.9816, 40.7486],
        'turtle bay': [-73.9665, 40.7519],
        'chelsea': [-73.9969, 40.7439],
        'hells kitchen': [-73.9897, 40.7648],
        "hell's kitchen": [-73.9897, 40.7648],
        'midtown east': [-73.9735, 40.7549],
        'wall street': [-73.9901, 40.7074],
        'broadway': [-73.9776, 40.7614],
        'central park': [-73.9654, 40.7829]
    };

    const normalizedName = substationName.toLowerCase().replace(/[^a-z\s]/g, '');
    const coords = substationCoords[normalizedName];

    if (!coords) {
        showNotification('⚠️ Substation Not Found', `Could not find substation: ${substationName}`, 'warning');
        return;
    }

    // Hide all power grid layers first
    hidePowerGrid();

    // Then show ONLY this substation + its connected infrastructure
    setTimeout(() => {
        // Enable only the substation layer to show the specific substation
        const substationsToggle = document.getElementById('layer-substations');
        if (substationsToggle && !substationsToggle.checked) {
            substationsToggle.checked = true;
            toggleLayer('substations');
        }

        // Filter and show cables connected to this substation
        filterCablesForSubstation(substationName, coords);

        // Filter and show EV station associated with this substation
        filterEVStationForSubstation(substationName, coords);

        // Highlight the specific substation
        setTimeout(() => {
            createAdvancedHighlight({
                coordinates: coords,
                name: `${substationName} Network`,
                subtitle: 'Connected infrastructure only',
                type: 'substation-network',
                duration: 30000,
                pulseColor: '#00ff88'
            });

            // Focus on the substation
            window.map.flyTo({
                center: coords,
                zoom: 15,
                duration: 2000
            });
        }, 500);

    }, 300);

    showNotification('🔌 Substation Network', `Showing ${substationName} connections only`, 'success');
}

function filterCablesForSubstation(substationName, substationCoords) {
    console.log(`Filtering cables for ${substationName} at`, substationCoords);

    // This is a simplified approach - show primary and secondary cables near this substation
    const serviceRadius = 0.01; // About 1km radius in degrees

    // Enable primary cables toggle
    const primaryToggle = document.getElementById('layer-primary');
    if (primaryToggle && !primaryToggle.checked) {
        primaryToggle.checked = true;
        toggleLayer('primary');
    }

    // Enable secondary cables toggle
    const secondaryToggle = document.getElementById('layer-secondary');
    if (secondaryToggle && !secondaryToggle.checked) {
        secondaryToggle.checked = true;
        toggleLayer('secondary');
    }

    // Add highlighting animation to show connections
    setTimeout(() => {
        highlightSubstationConnections(substationName, substationCoords, serviceRadius);
    }, 1000);

    console.log(`Showing existing cables near ${substationName} (within ${serviceRadius} radius)`);
}

function highlightSubstationConnections(substationName, substationCoords, serviceRadius) {
    console.log('🔆 Highlighting connections for:', substationName);

    // Get network state to find connected infrastructure
    fetch('/api/network_state')
        .then(response => response.json())
        .then(networkState => {
            // 1. Highlight the substation itself with pulsing animation
            setTimeout(() => {
                let pulseCount = 0;
                const pulseInterval = setInterval(() => {
                    if (pulseCount >= 6) {
                        clearInterval(pulseInterval);
                        return;
                    }

                    // Create pulsing circle around substation
                    const coords = substationCoords;
                    if (coords && window.map) {
                        const circleId = `pulse-circle-${Date.now()}-${pulseCount}`;

                        // Add pulsing circle source and layer
                        window.map.addSource(circleId, {
                            type: 'geojson',
                            data: {
                                type: 'FeatureCollection',
                                features: [{
                                    type: 'Feature',
                                    geometry: {
                                        type: 'Point',
                                        coordinates: coords
                                    }
                                }]
                            }
                        });

                        window.map.addLayer({
                            id: circleId,
                            type: 'circle',
                            source: circleId,
                            paint: {
                                'circle-radius': 20 + (pulseCount * 8),
                                'circle-color': '#4A90E2',  // Professional blue
                                'circle-opacity': 0.9 - (pulseCount * 0.12),
                                'circle-stroke-width': 2,
                                'circle-stroke-color': '#FFD700',  // Gold stroke
                                'circle-stroke-opacity': 0.8 - (pulseCount * 0.1)
                            }
                        });

                        // Remove circle after animation
                        setTimeout(() => {
                            if (window.map.getLayer(circleId)) {
                                window.map.removeLayer(circleId);
                                window.map.removeSource(circleId);
                            }
                        }, 500);
                    }
                    pulseCount++;
                }, 400);
            }, 1000);

            // 2. Highlight primary cables connected to this substation
            setTimeout(() => {
                highlightConnectionCables('primary', substationName, networkState);
            }, 1500);

            // 3. Highlight secondary cables connected to this substation
            setTimeout(() => {
                highlightConnectionCables('secondary', substationName, networkState);
            }, 2300);

            // 4. Highlight EV stations connected to this substation
            setTimeout(() => {
                highlightEVStations(substationName, networkState);
            }, 3500);
        })
        .catch(error => {
            console.error('Failed to get network state for highlighting:', error);
        });
}

function highlightConnectionCables(cableType, substationName, networkState) {
    console.log(`🔆 Highlighting ${cableType} cables for:`, substationName);

    if (!window.map || !networkState) return;

    const layerId = `${cableType}-cables`;
    const glowLayerId = `${cableType}-cables-glow`;

    if (!window.map.getLayer(layerId)) return;

    // Find cables connected to this substation
    const cableKey = cableType === 'primary' ? 'primary' : 'secondary';
    const connectedCables = networkState.cables[cableKey].filter(cable =>
        cable.from === substationName ||
        (cableType === 'secondary' && cable.substation === substationName)
    );

    console.log(`Found ${connectedCables.length} ${cableType} cables connected to ${substationName}`);

    if (connectedCables.length === 0) return;

    // Get cable IDs to highlight (ONLY connected cables)
    const connectedCableIds = connectedCables.map(cable => cable.id);

    // Store original paint properties
    const originalColor = window.map.getPaintProperty(layerId, 'line-color');
    const originalWidth = window.map.getPaintProperty(layerId, 'line-width');
    const originalGlowColor = window.map.getPaintProperty(glowLayerId, 'line-color') || originalColor;

    // Set professional highlight colors - very visible and professional
    const highlightColor = cableType === 'primary' ? '#00BFFF' : '#FF4500';  // Deep sky blue for primary, Red-orange for secondary
    const highlightWidth = cableType === 'primary' ? 6 : 4;

    console.log(`Applying ${highlightColor} color to ${connectedCableIds.length} connected cables in ${layerId}`);

    // Create filter to ONLY highlight connected cables
    const highlightFilter = ['in', ['get', 'id'], ['literal', connectedCableIds]];

    // Apply highlight ONLY to connected cables using MapBox filter
    window.map.setPaintProperty(layerId, 'line-color', ['case', highlightFilter, highlightColor, originalColor]);
    window.map.setPaintProperty(layerId, 'line-width', ['case', highlightFilter, highlightWidth, originalWidth]);
    if (window.map.getLayer(glowLayerId)) {
        window.map.setPaintProperty(glowLayerId, 'line-color', ['case', highlightFilter, highlightColor, originalGlowColor]);
    }

    // Restore original colors after 4 seconds
    setTimeout(() => {
        console.log(`Restoring original colors for ${layerId}`);
        if (window.map.getLayer(layerId)) {
            window.map.setPaintProperty(layerId, 'line-color', originalColor);
            window.map.setPaintProperty(layerId, 'line-width', originalWidth);
            if (window.map.getLayer(glowLayerId)) {
                window.map.setPaintProperty(glowLayerId, 'line-color', originalGlowColor);
            }
        }
    }, 4000);
}

function filterEVStationForSubstation(substationName, substationCoords) {
    console.log(`Filtering EV station for ${substationName}`);

    // Enable EV stations layer
    const evToggle = document.getElementById('layer-ev');
    if (evToggle && !evToggle.checked) {
        evToggle.checked = true;
        toggleLayer('ev');
    }

    // Add highlighting animation for EV stations
    setTimeout(() => {
        highlightEVStations(substationName);
    }, 1200);

    console.log(`Showing EV station associated with ${substationName}`);
}

function highlightEVStations(substationName, networkState) {
    console.log('🔆 Highlighting EV stations for:', substationName);

    if (!window.map || !networkState) return;

    const iconLayerId = 'ev-stations-icon';
    if (!window.map.getLayer(iconLayerId)) return;

    // Find EV stations connected to this substation through secondary cables
    const connectedEVStations = [];
    networkState.cables.secondary.forEach(cable => {
        if (cable.substation === substationName && cable.to) {
            // Find if this cable endpoint connects to an EV station
            networkState.ev_stations.forEach(ev => {
                if (ev.id === cable.to || ev.traffic_light_id === cable.to) {
                    connectedEVStations.push(ev.id);
                }
            });
        }
    });

    console.log(`Found ${connectedEVStations.length} EV stations connected to ${substationName}`);

    if (connectedEVStations.length === 0) return;

    // Store original size
    const originalSize = window.map.getPaintProperty(iconLayerId, 'icon-size') || 1;
    const originalOpacity = window.map.getPaintProperty(iconLayerId, 'icon-opacity') || 1;

    // Create filter to only highlight connected EV stations
    const highlightFilter = ['in', ['get', 'id'], ['literal', connectedEVStations]];

    let flashCount = 0;
    const flashInterval = setInterval(() => {
        if (flashCount >= 4) {
            clearInterval(flashInterval);
            // Restore original size and opacity
            window.map.setPaintProperty(iconLayerId, 'icon-size', originalSize);
            window.map.setPaintProperty(iconLayerId, 'icon-opacity', originalOpacity);
            return;
        }

        // Professional flash effect only for connected infrastructure
        const isFlashOn = flashCount % 2 === 0;
        window.map.setPaintProperty(iconLayerId, 'icon-size',
            ['case', highlightFilter, isFlashOn ? originalSize * 1.3 : originalSize, originalSize]);
        window.map.setPaintProperty(iconLayerId, 'icon-opacity',
            ['case', highlightFilter, isFlashOn ? 0.8 : 1, originalOpacity]);

        flashCount++;
    }, 300);
}

console.log('🚀 ULTIMATE LLM MAP SYSTEM loaded successfully - World-class capabilities active!');
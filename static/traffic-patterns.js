/**
 * WORLD-CLASS TRAFFIC PATTERN SYSTEM
 * Realistic vehicle spawning based on time of day
 */

class TrafficPatternManager {
    constructor() {
        // Define realistic traffic patterns for Manhattan
        this.patterns = {
            'late_night': {
                timeRange: [0, 5],
                vehicleRange: [10, 20],
                evPercentage: 0.5, // Lower EV percentage at night
                description: 'Late Night - Minimal Traffic',
                icon: '🌙'
            },
            'early_morning': {
                timeRange: [5, 7],
                vehicleRange: [40, 60],
                evPercentage: 0.6,
                description: 'Early Morning - Light Traffic',
                icon: '🌅'
            },
            'morning_rush': {
                timeRange: [7, 9],
                vehicleRange: [85, 100],
                evPercentage: 0.7,
                description: 'Morning Rush Hour - Heavy Traffic',
                icon: '🚗'
            },
            'mid_morning': {
                timeRange: [9, 11],
                vehicleRange: [60, 80],
                evPercentage: 0.7,
                description: 'Mid Morning - Moderate Traffic',
                icon: '☀️'
            },
            'midday': {
                timeRange: [11, 14],
                vehicleRange: [70, 90],
                evPercentage: 0.7,
                description: 'Midday - Normal Traffic',
                icon: '🌞'
            },
            'afternoon': {
                timeRange: [14, 17],
                vehicleRange: [75, 95],
                evPercentage: 0.7,
                description: 'Afternoon - Building Traffic',
                icon: '🌤️'
            },
            'evening_rush': {
                timeRange: [17, 19],
                vehicleRange: [90, 100],
                evPercentage: 0.75, // Peak EV usage
                description: 'Evening Rush Hour - Heavy Traffic',
                icon: '🌆'
            },
            'evening': {
                timeRange: [19, 21],
                vehicleRange: [70, 85],
                evPercentage: 0.7,
                description: 'Evening - Moderate Traffic',
                icon: '🌃'
            },
            'night': {
                timeRange: [21, 23],
                vehicleRange: [40, 60],
                evPercentage: 0.6,
                description: 'Night - Light Traffic',
                icon: '🌉'
            },
            'late_evening': {
                timeRange: [23, 24],
                vehicleRange: [20, 30],
                evPercentage: 0.5,
                description: 'Late Evening - Minimal Traffic',
                icon: '🌙'
            }
        };

        console.log('✅ Traffic Pattern Manager initialized');
    }

    /**
     * Get traffic pattern for a specific hour
     */
    getPatternForTime(hour) {
        hour = parseInt(hour);

        for (const [key, pattern] of Object.entries(this.patterns)) {
            const [start, end] = pattern.timeRange;
            if (hour >= start && hour < end) {
                return {
                    key: key,
                    ...pattern
                };
            }
        }

        // Fallback to midday
        return {
            key: 'midday',
            ...this.patterns.midday
        };
    }

    /**
     * Get vehicle count for a specific hour
     * Returns a value within the realistic range for that time
     */
    getVehicleCountForTime(hour) {
        const pattern = this.getPatternForTime(hour);
        const [min, max] = pattern.vehicleRange;

        // Add some randomization for realism
        const variance = Math.floor((max - min) * 0.2); // 20% variance
        const base = Math.floor((min + max) / 2);
        const count = base + Math.floor(Math.random() * variance * 2) - variance;

        // SAFETY CAP: Simulation handles max 100 vehicles
        return Math.max(min, Math.min(100, Math.min(max, count)));
    }

    /**
     * Get EV percentage for a specific hour
     */
    getEVPercentageForTime(hour) {
        const pattern = this.getPatternForTime(hour);
        return pattern.evPercentage;
    }

    /**
     * Get traffic description for UI display
     */
    getTrafficDescription(hour) {
        const pattern = this.getPatternForTime(hour);
        const vehicleCount = this.getVehicleCountForTime(hour);

        return {
            icon: pattern.icon,
            description: pattern.description,
            vehicleCount: vehicleCount,
            evPercentage: pattern.evPercentage,
            pattern: pattern.key
        };
    }

    /**
     * Spawn vehicles based on time of day
     */
    async spawnVehiclesForTime(hour) {
        try {
            const vehicleCount = this.getVehicleCountForTime(hour);
            const evPercentage = this.getEVPercentageForTime(hour);
            const pattern = this.getPatternForTime(hour);

            console.log(`🚗 Requesting ${vehicleCount} vehicles for ${pattern.description} (${Math.round(evPercentage * 100)}% EV)`);

            // Stop existing simulation
            await fetch('/api/sumo/stop', {method: 'POST'});
            await new Promise(resolve => setTimeout(resolve, 500));

            // Start with calculated vehicle count
            const response = await fetch('/api/sumo/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    vehicle_count: vehicleCount,
                    ev_percentage: evPercentage,
                    battery_min_soc: 0.2,
                    battery_max_soc: 0.9
                })
            });

            const data = await response.json();

            if (data.success) {
                // Get ACTUAL spawned count from API (may be less than requested)
                const actualSpawned = data.vehicles_spawned || vehicleCount;

                console.log(`✅ Requested: ${vehicleCount}, Actually spawned: ${actualSpawned}`);

                // Update EV charging load based on ACTUAL spawned count
                await fetch('/api/scenario/add_vehicles', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({count: actualSpawned})
                });

                // **FORCE NETWORK STATE RELOAD TO UPDATE VEHICLE COUNT IN FOOTER**
                await new Promise(resolve => setTimeout(resolve, 300)); // Brief delay for SUMO to register vehicles
                if (window.loadNetworkState) {
                    await window.loadNetworkState();
                    console.log('🔄 Network state reloaded - vehicle count should update');
                }

                return {
                    success: true,
                    vehicleCount: actualSpawned,  // Return ACTUAL spawned count
                    requestedCount: vehicleCount,  // Keep requested for reference
                    evPercentage: evPercentage,
                    pattern: pattern
                };
            } else {
                return {
                    success: false,
                    error: data.error || 'Failed to spawn vehicles'
                };
            }

        } catch (error) {
            console.error('Error spawning vehicles:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get all patterns for display/documentation
     */
    getAllPatterns() {
        return this.patterns;
    }

    /**
     * Get summary of traffic throughout the day
     */
    getDailySummary() {
        let summary = '📊 **Daily Traffic Pattern Summary**\n\n';

        for (const [key, pattern] of Object.entries(this.patterns)) {
            const [start, end] = pattern.timeRange;
            const [minV, maxV] = pattern.vehicleRange;
            const timeStr = `${String(start).padStart(2, '0')}:00 - ${String(end).padStart(2, '0')}:00`;

            summary += `${pattern.icon} **${timeStr}**: ${minV}-${maxV} vehicles\n`;
            summary += `   ${pattern.description}\n\n`;
        }

        return summary;
    }
}

// Create global instance
window.trafficPatternManager = new TrafficPatternManager();

console.log('✅ Traffic Pattern System loaded');

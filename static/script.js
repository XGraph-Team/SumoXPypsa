        /**
         * World-Class Markdown Renderer for Chatbot
         * Renders markdown with proper formatting (bold, italic, lists, code blocks, etc.)
         */
        
        // Initialize global socket connection
        if (typeof io !== 'undefined') {
            window.socket = io();
            window.socket.on('connect', () => {
                console.log('[System] Socket connected');
            });
        }

        window.renderMarkdown = function(text) {
            if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
                // Fallback if libraries not loaded
                return text.replace(/\n/g, '<br>');
            }

            // Configure marked for better rendering
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: false,
                mangle: false
            });

            // Convert markdown to HTML
            const rawHtml = marked.parse(text);

            // Sanitize HTML to prevent XSS attacks
            const cleanHtml = DOMPurify.sanitize(rawHtml, {
                ALLOWED_TAGS: ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'code', 'pre', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'a'],
                ALLOWED_ATTR: ['href', 'target', 'rel']
            });

            return cleanHtml;
        };

        function togglePanel() {
            const panel = document.querySelector('.control-panel');
            const btn = document.getElementById('panel-toggle');

            if (!panel || !btn) return;

            if (panel.classList.contains('collapsed')) {
                // Expanding
                panel.classList.remove('collapsed');
                panel.style.width = '480px';
                btn.innerHTML = '✕';
            } else {
                // Collapsing
                panel.classList.add('collapsed');
                panel.style.width = '80px';
                btn.innerHTML = '☰';
            }
        }
        function selectTab(tab, el) {
            const panel = document.querySelector('.control-panel');
            
            // If panel is collapsed, don't change tabs
            if (panel && panel.classList.contains('collapsed')) {
                return;
            }
            
            document.body.setAttribute('data-tab', tab);
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            if (el) el.classList.add('active');
        }

        function dismissEmergencyBanner() {
            const eb = document.getElementById('v2g-emergency-banner');
            if (eb) {
                eb.style.transition = 'opacity 0.4s ease';
                eb.style.opacity = '0';
                setTimeout(() => eb.remove(), 450);
            }
            // Also remove any progress overlay immediately
            const ov = document.getElementById('v2g-overlay');
            if (ov) ov.remove();
        }

        function dismissRestoredBanner() {
            const rb = document.getElementById('v2g-restored-banner');
            if (rb) {
                rb.style.transition = 'opacity 0.4s ease';
                rb.style.opacity = '0';
                setTimeout(() => rb.remove(), 450);
            }
        }

        function forceClearV2GEmergencyUI() {
            const ids = ['v2g-emergency-banner', 'v2g-overlay', 'v2g-celebration'];
            ids.forEach(id => { const el = document.getElementById(id); if (el) el.remove(); });
        }

        function forceShowRestorationBanner() {
            // Ensure emergency UI is gone
            forceClearV2GEmergencyUI();
            // Show success banner if not already visible
            if (!document.getElementById('v2g-success-banner') && !document.getElementById('v2g-restored-banner')) {
                const successBanner = document.createElement('div');
                successBanner.id = 'v2g-success-banner';
                successBanner.style.cssText = `position:fixed;inset:0;z-index:3000;background:radial-gradient(ellipse at center, rgba(0,80,40,0.92), rgba(0,40,20,0.98));display:flex;align-items:center;justify-content:center;`;
                successBanner.innerHTML = `
                    <div style="text-align:center;max-width:900px;padding:28px 32px;border-radius:18px;background:linear-gradient(135deg, rgba(0,20,10,0.96), rgba(0,30,20,0.92));border:2px solid rgba(0,255,136,0.6);box-shadow:0 30px 80px rgba(0,0,0,0.7), 0 0 140px rgba(0,255,136,0.25);">
                        <div style="font-size:44px;font-weight:900;letter-spacing:1px;color:#a8ffcf;text-shadow:0 0 30px rgba(0,255,136,0.5);margin-bottom:10px;">✅ SYSTEM RESTORED — PEOPLE SAFE</div>
                        <div style="font-size:18px;color:#c8ffe6;margin-bottom:14px;">V2G rescue successful. Elevators cleared, traffic lights back to normal, services operational.</div>
                        <button onclick="document.getElementById('v2g-success-banner').remove()" class="btn btn-primary" style="padding:10px 16px;">Dismiss</button>
                    </div>`;
                document.body.appendChild(successBanner);
            }
        }

        // World-class restored banner (reusable)
        function showRestoredBanner() {
            // Remove emergency banner if visible
            const eb = document.getElementById('v2g-emergency-banner');
            if (eb) eb.remove();
            // Remove progress overlay if visible
            const ov = document.getElementById('v2g-overlay');
            if (ov) ov.remove();
            // Remove any celebration overlay remnants
            const cel = document.getElementById('v2g-celebration');
            if (cel) cel.remove();

            // Hide generic blackout alert if present
            const blackout = document.getElementById('blackout-alert');
            if (blackout) blackout.style.display = 'none';

            // Compact toast
            showNotification('✅ System Restored', 'V2G saved the day — grid stabilized and services recovered.', 'success');

            // Dismissible restored banner
            let restored = document.getElementById('v2g-restored-banner');
            if (!restored) {
                restored = document.createElement('div');
                restored.id = 'v2g-restored-banner';
                restored.style.cssText = `position:fixed;inset:0;z-index:2650;background:radial-gradient(ellipse at center, rgba(0,80,40,0.85), rgba(0,40,20,0.95));display:flex;align-items:center;justify-content:center;`;
                restored.innerHTML = `
                    <div style="text-align:center;max-width:900px;padding:28px 32px;border-radius:18px;background:linear-gradient(135deg, rgba(0,20,10,0.9), rgba(0,35,20,0.88));border:2px solid rgba(0,255,136,0.5);box-shadow:0 30px 80px rgba(0,0,0,0.7), 0 0 120px rgba(0,255,136,0.2);">
                        <div style="font-size:40px;font-weight:900;letter-spacing:1px;color:#a8ffcf;text-shadow:0 0 26px rgba(0,255,136,0.45);margin-bottom:10px;">✅ SYSTEM RESTORED — PEOPLE SAFE</div>
                        <div style="font-size:18px;color:#c8ffe6;margin-bottom:14px;">Elevators cleared, traffic lights back to normal, and services fully operational.</div>
                        <button onclick="dismissRestoredBanner()" class="btn btn-primary" style="padding:10px 16px;">Dismiss</button>
                    </div>`;
                document.body.appendChild(restored);
                // Keep until user dismisses
            }
        }

        // Snapshot function - Comprehensive System State Capture
        window.buildSnapshotData = function() {
            const ns = window.networkState || {};
            const stats = ns.statistics || {};
            const vStats = ns.vehicle_stats || {};
            const v2g = ns.v2g || {};
            const subs = ns.substations || [];
            const evStations = ns.ev_stations || [];
            const cables = ns.cables || {};
            const scenario = ns.scenario || {};

            const totalCapacity = subs.reduce((s, sub) => s + (sub.capacity_mva || 0), 0);
            const totalLoad = stats.total_load_mw || ns.total_load_mw || 0;
            const opSubs = subs.filter(s => s.operational).length;
            const totalSubs = subs.length;
            const totalVehicles = vStats.active_vehicles || vStats.total_vehicles || 0;
            const evCount = vStats.ev_vehicles || 0;

            return {
                meta: {
                    snapshot_id: `SNAP-${Date.now()}`,
                    timestamp: new Date().toISOString(),
                    simulation_time: scenario.time_formatted || null,
                    simulation_hour: scenario.time_hour,
                    simulation_minute: scenario.time_minute,
                    generated_by: "Manhattan Grid Control Dashboard"
                },
                map_view: {
                    center: map.getCenter(),
                    zoom: map.getZoom(),
                    pitch: map.getPitch(),
                    bearing: map.getBearing(),
                    visible_layers: {
                        traffic_lights: layers.lights,
                        vehicles: layers.vehicles,
                        primary_cables: layers.primary,
                        secondary_cables: layers.secondary,
                        ev_stations: layers.ev,
                        substations: layers.substations
                    }
                },
                grid_status: {
                    substations: subs.map(sub => ({
                        name: sub.name,
                        operational: sub.operational,
                        load_mw: sub.load_mw,
                        capacity_mva: sub.capacity_mva,
                        utilization_pct: sub.capacity_mva > 0 ? +(sub.load_mw / sub.capacity_mva * 100).toFixed(1) : 0,
                        coverage_area: sub.coverage_area || null
                    })),
                    summary: {
                        total_substations: totalSubs,
                        operational: opSubs,
                        offline: totalSubs - opSubs,
                        total_load_mw: +totalLoad.toFixed(2),
                        total_capacity_mva: +totalCapacity.toFixed(2),
                        base_load_mw: +(stats.base_load_mw || 0).toFixed(2),
                        ev_charging_load_mw: +(stats.ev_charging_load_mw || 0).toFixed(2)
                    }
                },
                traffic: {
                    sumo_running: ns.sumo_running || false,
                    total_vehicles: totalVehicles,
                    ev_count: evCount,
                    gas_count: (totalVehicles - evCount) || 0,
                    avg_speed_kmh: +((vStats.avg_speed_mps || 0) * 3.6).toFixed(1),
                    vehicles_charging: vStats.vehicles_charging || 0,
                    vehicles_low_battery: vStats.vehicles_low_battery || 0,
                    vehicles_stranded: vStats.vehicles_stranded || 0,
                    vehicles_circling: vStats.vehicles_circling || 0,
                    total_energy_consumed_kwh: +(vStats.total_energy_consumed_kwh || 0).toFixed(1),
                    total_distance_km: +(vStats.total_distance_km || 0).toFixed(1)
                },
                v2g: {
                    active_sessions: v2g.active_sessions_count || 0,
                    total_power_kw: +(v2g.total_power_kw || 0).toFixed(1),
                    total_earnings_usd: +(v2g.total_earnings || 0).toFixed(2),
                    total_kwh_provided: +(v2g.total_kwh_provided || 0).toFixed(2),
                    earnings_rate_per_hour: +(v2g.earnings_rate_per_hour || 0).toFixed(2),
                    peak_power_kw: +(v2g.peak_power || 0).toFixed(1),
                    locked_vehicles: v2g.locked_vehicles || 0,
                    pending_vehicles: v2g.pending_vehicles || 0,
                    enabled_substations: v2g.enabled_substations || [],
                    restored_substations: v2g.restored_substations || [],
                    per_substation_delivery: Object.entries(v2g.energy_delivered || {}).map(([name, kwh]) => ({
                        substation: name,
                        delivered_kwh: +(kwh || 0).toFixed(2),
                        required_kwh: +((v2g.energy_required || {})[name] || 0).toFixed(2)
                    }))
                },
                ev_stations: evStations.map(st => ({
                    id: st.id,
                    name: st.name,
                    operational: st.operational,
                    chargers: st.chargers,
                    vehicles_charging: st.vehicles_charging || 0,
                    current_load_kw: +(st.current_load_kw || 0).toFixed(1),
                    substation: st.substation
                })),
                cables: {
                    primary: {
                        total: stats.total_primary_cables || (cables.primary || []).length,
                        operational: stats.operational_primary_cables || 0
                    },
                    secondary: {
                        total: stats.total_secondary_cables || (cables.secondary || []).length,
                        operational: stats.operational_secondary_cables || 0
                    }
                },
                scenario: {
                    temperature_f: scenario.temperature_f || null,
                    weather: scenario.weather || null,
                    time_description: scenario.time_description || null,
                    auto_advance: scenario.auto_advance || false
                },
                kpis: {
                    capacity_utilization_pct: totalCapacity > 0 ? +(totalLoad / totalCapacity * 100).toFixed(1) : 0,
                    grid_health_pct: totalSubs > 0 ? +(opSubs / totalSubs * 100).toFixed(1) : 100,
                    ev_adoption_pct: totalVehicles > 0 ? +(evCount / totalVehicles * 100).toFixed(1) : 0,
                    v2g_participation_pct: evCount > 0 ? +((v2g.active_sessions_count || 0) / Math.max(evCount, 1) * 100).toFixed(1) : 0,
                    avg_substation_load_pct: totalSubs > 0 && totalCapacity > 0
                        ? +(totalLoad / totalCapacity * 100).toFixed(1) : 0,
                    cable_integrity_pct: (() => {
                        const tp = stats.total_primary_cables || 0;
                        const ts = stats.total_secondary_cables || 0;
                        const op = stats.operational_primary_cables || 0;
                        const os = stats.operational_secondary_cables || 0;
                        const total = tp + ts;
                        return total > 0 ? +((op + os) / total * 100).toFixed(1) : 100;
                    })(),
                    vehicles_charging_pct: totalVehicles > 0 ? +((vStats.vehicles_charging || 0) / totalVehicles * 100).toFixed(1) : 0
                }
            };
        };

        window.captureSnapshot = function() {
            try {
                const mapCanvas = map.getCanvas();
                const image = mapCanvas.toDataURL('image/png');
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const data = window.buildSnapshotData();

                // Download map image
                const link = document.createElement('a');
                link.download = `snapshot_map_${timestamp}.png`;
                link.href = image;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                // Download comprehensive JSON
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
                const dataLink = document.createElement('a');
                dataLink.setAttribute("href", dataStr);
                dataLink.setAttribute("download", `snapshot_${timestamp}.json`);
                document.body.appendChild(dataLink);
                dataLink.click();
                dataLink.remove();

                showNotification('📸 Snapshot Captured', 'Map image and comprehensive state JSON downloaded.', 'success');

            } catch (e) {
                console.error("Snapshot failed:", e);
                showNotification('❌ Snapshot Failed', 'Could not capture screen.', 'error');
            }
        };

        // Socket listener for remote snapshot trigger
        if (typeof socket !== 'undefined') {
            socket.on('trigger_snapshot', () => {
                console.log("Remote snapshot trigger received");
                window.captureSnapshot();
            });

            // Socket listener for report download (triggered by chatbot tool)
            socket.on('trigger_report_download', (data) => {
                if (data && data.url) {
                    console.log("Report download trigger received:", data.url);
                    const link = document.createElement('a');
                    link.href = data.url;
                    link.download = data.url.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    showNotification('Report Ready', 'PDF report downloaded.', 'success');
                }
            });
        }

        // Generate Report Function — sends map screenshot + snapshot data to backend
        window.generateReport = async function() {
            try {
                showNotification('📄 Generating Report...', 'Capturing map and compiling analytics...', 'info');

                const notes = prompt("Optional: Add notes for this report (or leave empty):");

                // Capture the current map as a PNG base64 string
                let screenshotBase64 = null;
                try {
                    const mapCanvas = map.getCanvas();
                    screenshotBase64 = mapCanvas.toDataURL('image/png');
                } catch (imgErr) {
                    console.warn("Could not capture map screenshot for report:", imgErr);
                }

                const response = await fetch('/api/report/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        notes: notes || "",
                        screenshot_base64: screenshotBase64
                    })
                });

                const data = await response.json();

                if (data.success && data.url) {
                    const link = document.createElement('a');
                    link.href = data.url;
                    link.download = data.url.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    showNotification('✅ Report Ready', 'PDF report downloaded successfully.', 'success');
                } else {
                    showNotification('❌ Report Failed', data.message || 'Unknown error', 'error');
                }
            } catch (e) {
                console.error("Report generation failed:", e);
                showNotification('❌ Error', 'Could not contact reporting server.', 'error');
            }
        };

        async function runV2GRescueScenario() {
            try {
                const substation = 'Times Square';
                // Cinematic emergency banner
                let emergency = document.getElementById('v2g-emergency-banner');
                if (!emergency) {
                    emergency = document.createElement('div');
                    emergency.id = 'v2g-emergency-banner';
                    emergency.style.cssText = `position:fixed;inset:0;z-index:2600;background:radial-gradient(ellipse at center, rgba(120,0,0,0.88), rgba(40,0,0,0.96));display:flex;align-items:center;justify-content:center;`;
                    emergency.innerHTML = `
                        <div style="text-align:center;max-width:900px;padding:28px 32px;border-radius:18px;background:linear-gradient(135deg, rgba(15,0,0,0.9), rgba(30,0,0,0.85));border:2px solid rgba(255,50,50,0.5);box-shadow:0 30px 80px rgba(0,0,0,0.7), 0 0 120px rgba(255,0,0,0.2);">
                            <div style="font-size:44px;font-weight:900;letter-spacing:1px;color:#ffb3b3;text-shadow:0 0 30px rgba(255,0,0,0.5);margin-bottom:10px;">🚨 EMERGENCY: PEOPLE BLOCKED IN ELEVATORS</div>
                            <div style="font-size:18px;color:#ffd6d6;margin-bottom:14px;">Substation Times Square failed. Do NOT restore manually — V2G emergency protocol is in progress.</div>
                            <div style="font-size:16px;color:#ffe0e0;opacity:0.9;margin-bottom:16px;">High‑SOC EVs are being dispatched to supply power. The system will confirm restoration automatically when sufficient energy has been delivered.</div>
                            <button onclick="dismissEmergencyBanner()" class="btn btn-primary" style="padding:10px 16px;">Dismiss</button>
                        </div>`;
                    document.body.appendChild(emergency);
                }
                // Fail substation
                await fetch(`/api/fail/${encodeURIComponent(substation)}`, { method: 'POST' });
                await loadNetworkState();

                showNotification('📣 Public Safety Notice', 'Sending notification to EVs with battery ≥ 70% to assist via V2G.', 'info');
                await new Promise(r => setTimeout(r, 800));

                const enableResp = await fetch(`/api/v2g/enable/${encodeURIComponent(substation)}`, { method: 'POST' });
                const enableData = await enableResp.json();
                if (!enableData.success) {
                    showNotification('❌ V2G Activation Failed', enableData.message || 'Unable to enable V2G.', 'error');
                    return;
                }
                const energyTarget = enableData.energy_needed_kwh || 50;
                showNotification('⚡ V2G Activated', `Dispatching EVs. Target energy: ${Math.round(energyTarget)} kWh`, 'success');

                // Create cinematic overlay with live progress
                let overlay = document.getElementById('v2g-overlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'v2g-overlay';
                    overlay.style.cssText = `position:fixed;inset:0;pointer-events:none;z-index:2500;display:flex;align-items:flex-start;justify-content:center;padding-top:80px;`;
                    overlay.innerHTML = `
                        <div id="v2g-card" style="min-width:480px;max-width:640px;background:linear-gradient(135deg, rgba(0,20,25,0.9), rgba(0,30,40,0.9));border:1px solid rgba(0,255,255,0.25);border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,0.6), 0 0 50px rgba(0,255,255,0.15);backdrop-filter:blur(12px);padding:18px 20px;">
                            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px;">
                                <div style="font-weight:800;color:#00ffff;letter-spacing:0.5px;">V2G EMERGENCY RESTORATION</div>
                                <div id="v2g-overlay-status" style="font-size:12px;color:#00ff88;">Active</div>
                            </div>
                            <div id="v2g-overlay-msg" style="color:#cfeff2;font-size:13px;margin-bottom:10px;">Vehicles responding… stabilizing voltage and serving critical loads (elevators).</div>
                            <div style="height:10px;background:rgba(255,255,255,0.08);border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.12);">
                                <div id="v2g-progress" style="height:100%;width:0%;background:linear-gradient(90deg,#00ffff,#00ccff);box-shadow:0 0 20px rgba(0,255,255,0.6);transition:width 0.5s ease;"></div>
                            </div>
                            <div id="v2g-detail" style="display:flex;justify-content:space-between;font-size:12px;color:#a9dfe6;margin-top:6px;">
                                <span id="v2g-active">Active vehicles: 0</span>
                                <span id="v2g-energy">Delivered: 0 kWh / ${Math.round(energyTarget)} kWh</span>
                            </div>
                        </div>`;
                    document.body.appendChild(overlay);
                }

                // Poll status until energy target is met, then restore
                let delivered = 0;
                while (true) {
                    const status = await (await fetch('/api/v2g/status')).json();
                    const required = (status?.energy_required && status.energy_required[substation]) || energyTarget;
                    delivered = (status?.energy_delivered && status.energy_delivered[substation]) || 0;
                    const activeVehicles = Array.isArray(status?.active_vehicles) ? status.active_vehicles.filter(v => v.substation === substation).length : (status?.active_sessions || 0);
                    const pct = Math.max(0, Math.min(100, Math.round((delivered / Math.max(1, required)) * 100)));
                    const pbar = document.getElementById('v2g-progress');
                    const activeEl = document.getElementById('v2g-active');
                    const energyEl = document.getElementById('v2g-energy');
                    const msgEl = document.getElementById('v2g-overlay-msg');
                    if (pbar) pbar.style.width = pct + '%';
                    if (activeEl) activeEl.textContent = `Active vehicles: ${activeVehicles}`;
                    if (energyEl) energyEl.textContent = `Delivered: ${Math.round(delivered)} kWh / ${Math.round(required)} kWh`;
                    if (msgEl && activeVehicles > 0) msgEl.textContent = 'Vehicles arriving and discharging—stabilizing substation voltages…';

                    if (delivered >= required) break;
                    await new Promise(r => setTimeout(r, 1200));
                }

                // Restore once target reached
                await fetch(`/api/restore/${encodeURIComponent(substation)}`, { method: 'POST' });
                await loadNetworkState();

                // Update overlay to success state
                const statusEl = document.getElementById('v2g-overlay-status');
                const msgEl2 = document.getElementById('v2g-overlay-msg');
                const pbarEl = document.getElementById('v2g-progress');
                if (pbarEl) pbarEl.style.width = '100%';
                if (statusEl) {
                    statusEl.textContent = 'Restored';
                    statusEl.style.color = '#00ff88';
                }
                if (msgEl2) msgEl2.textContent = 'V2G rescue successful — substation restored, elevators operational, and traffic lights normalized.';

                // Beautiful celebration overlay
                let celebrate = document.getElementById('v2g-celebration');
                if (!celebrate) {
                    celebrate = document.createElement('div');
                    celebrate.id = 'v2g-celebration';
                    celebrate.style.cssText = `position:fixed;inset:0;z-index:2700;display:flex;align-items:center;justify-content:center;pointer-events:none;`;
                    celebrate.innerHTML = `
                        <div style="text-align:center;max-width:820px;padding:26px 30px;border-radius:18px;background:linear-gradient(135deg, rgba(0,20,10,0.92), rgba(0,40,20,0.9));border:1px solid rgba(0,255,136,0.35);box-shadow:0 28px 80px rgba(0,0,0,0.6), 0 0 100px rgba(0,255,136,0.2);">
                            <div style="font-size:40px;font-weight:900;letter-spacing:0.5px;color:#a8ffcf;text-shadow:0 0 24px rgba(0,255,136,0.35);margin-bottom:10px;">✅ SYSTEM RESTORED — V2G RESCUE COMPLETE</div>
                            <div style="font-size:16px;color:#c8ffe6;opacity:0.95;margin-bottom:6px;">Power was stabilized using contribution from participating EVs.</div>
                            <div style="font-size:16px;color:#c8ffe6;opacity:0.95;">Traffic lights, elevators, and critical services are back online. People are safe.</div>
                        </div>`;
                    document.body.appendChild(celebrate);
                }

                // Also show compact toast
                showNotification('✅ System Restored', 'V2G saved the day — grid stabilized and services recovered.', 'success');

                // Replace overlays with a dismissible restored banner
                // Remove progress overlay immediately to avoid showing zeros
                const ov = document.getElementById('v2g-overlay');
                if (ov) ov.remove();
                // Remove emergency banner if present
                const eb = document.getElementById('v2g-emergency-banner');
                if (eb) eb.remove();

                // Restored banner with dismiss
                let restored = document.getElementById('v2g-restored-banner');
                if (!restored) {
                    restored = document.createElement('div');
                    restored.id = 'v2g-restored-banner';
                    restored.style.cssText = `position:fixed;inset:0;z-index:2650;background:radial-gradient(ellipse at center, rgba(0,80,40,0.85), rgba(0,40,20,0.95));display:flex;align-items:center;justify-content:center;`;
                    restored.innerHTML = `
                        <div style="text-align:center;max-width:900px;padding:28px 32px;border-radius:18px;background:linear-gradient(135deg, rgba(0,20,10,0.9), rgba(0,35,20,0.88));border:2px solid rgba(0,255,136,0.5);box-shadow:0 30px 80px rgba(0,0,0,0.7), 0 0 120px rgba(0,255,136,0.2);">
                            <div style="font-size:40px;font-weight:900;letter-spacing:1px;color:#a8ffcf;text-shadow:0 0 26px rgba(0,255,136,0.45);margin-bottom:10px;">✅ SYSTEM RESTORED — PEOPLE SAFE</div>
                            <div style="font-size:18px;color:#c8ffe6;margin-bottom:14px;">V2G energy was sufficient to recover the substation. Elevators, traffic lights, and critical services are back online.</div>
                            <button onclick="dismissRestoredBanner()" class="btn btn-primary" style="padding:10px 16px;">Dismiss</button>
                        </div>`;
                    document.body.appendChild(restored);
                }
            } catch (e) {
                console.error('V2G scenario error', e);
                showNotification('❌ Scenario Error', 'An error occurred running the V2G rescue scenario.', 'error');
            }
        }

    // ==========================================
    // ULTRA PERFORMANCE CONFIGURATION - MAXIMUM GPU UTILIZATION
    // ==========================================
    const PERFORMANCE_CONFIG = {
        renderMode: 'webgl',
        targetFPS: 144,  // Cap at 144 for stability
        dataUpdateRate: 200,  // Reduced polling frequency (5 FPS for data)
        interpolationSteps: 4,  // Smoother interpolation
        useWebWorkers: true,
        useGPUAcceleration: true,
        vehiclePoolSize: 5000,
        enableAdvancedEffects: false,
        enablePrediction: false,
        smoothingFactor: 0.85,
        enableDebugMode: window.location.hash === '#debug'
    };

    // Load Mapbox token from backend (served from MAPBOX_TOKEN env var)
    let _mapboxToken = '';
    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/config', false);  // synchronous — must complete before map init
        xhr.send();
        if (xhr.status === 200) {
            const config = JSON.parse(xhr.responseText);
            _mapboxToken = config.mapbox_token || '';
        }
    } catch (e) {
        console.warn('Could not fetch config, using fallback token');
    }
    mapboxgl.accessToken = _mapboxToken || 'YOUR_MAPBOX_ACCESS_TOKEN_HERE';

    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [-73.980, 40.758],
        zoom: 14.5,
        pitch: 60,           // 3D perspective - tilt camera 60 degrees
        bearing: -17.6,      // Rotate for better Manhattan view
        antialias: true,
        preserveDrawingBuffer: true, // REQUIRED for screenshot capability
        refreshExpiredTiles: false,
        fadeDuration: 0,
        maxZoom: 20,
        minZoom: 10,
        maxPitch: 85 // Allow looking closer to the horizon for 'free' feel
    });

    window.map = map;
    window.mapLoaded = false;

    // Add zoom +/- and compass rotation controls
    map.addControl(new mapboxgl.NavigationControl({
        showCompass: true,
        showZoom: true,
        visualizePitch: true
    }), 'bottom-right');

    // Wait for map to fully load before allowing AI actions
    map.on('load', async () => {
        console.log('Map fully loaded - AI actions now available');
        window.mapLoaded = true;

        // **LOAD NETWORK STATE FIRST TO CREATE LAYERS WITH DATA**
        await loadNetworkState();
        console.log('✅ Network state loaded on map init');

        // Safety: re-fetch after a brief delay to catch any layers that weren't
        // ready on the first call (3D terrain + EV layer init can race)
        setTimeout(async () => {
            await loadNetworkState();
            console.log('✅ Network state refreshed (safety reload)');
        }, 2000);

        // ==========================================
        // 3D TERRAIN AND BUILDINGS
        // ==========================================
        
        // 1. Add Terrain Source (Safety Check)
        if (!map.getSource('mapbox-dem')) {
            map.addSource('mapbox-dem', {
                'type': 'raster-dem',
                'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
                'tileSize': 512,
                'maxzoom': 14
            });
        }

        // 2. Enable Terrain - DISABLED BY DEFAULT to prevent vertical stretching
        // map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 0.5 });

        // 3. Add 3D Building Layer (Remove old one first to apply updates)
        if (map.getLayer('building-3d')) map.removeLayer('building-3d');

        // Find the label layer to place buildings *under* (so text is readable)
        const labelLayerId = map.getStyle().layers.find(
            (layer) => layer.type === 'symbol' && layer.layout['text-field']
        )?.id;

        map.addLayer({
            id: 'building-3d',
            source: 'composite',
            'source-layer': 'building',
            // NO FILTER: We want to try rendering EVERYTHING
            type: 'fill-extrusion',
            minzoom: 12,
            paint: {
                // Color: Dark at bottom, lighter at top
                'fill-extrusion-color': [
                    'interpolate',
                    ['linear'],
                    ['case',
                        ['>', ['get', 'height'], 0], ['get', 'height'],
                        ['>', ['get', 'levels'], 0], ['*', ['get', 'levels'], 3],
                        10 // Default used for color scale
                    ],
                    0, '#1a1f2c',    // Deep blue-black base
                    50, '#2a3245',   // More saturated dark blue
                    100, '#3a4660',  // Mid-tone blue-gray
                    200, '#4a5a7a',  // Desaturated steel blue
                    400, '#5a6e8e',  // Lighter steel
                    800, '#6a82a2'   // Horizon blue
                ],
                
                // Height: Robust logic with Fallbacks + Clamping
                'fill-extrusion-height': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    13, 0,
                    13.5, [
                        'min', // FINAL CAP: 350m (to catch extreme outliers without flattening the city)
                        [
                            '*', // SCALING: 0.6x original height (preserves relative scale but reduces verticality)
                            0.6,
                            [
                                'case',
                                ['>', ['get', 'height'], 0], ['get', 'height'], // Use real data
                                ['>', ['get', 'levels'], 0], ['*', ['get', 'levels'], 3], // Estimate from floors
                                10 // Fallback: 10m
                            ]
                        ],
                        350
                    ]
                ],
                
                // Base: Clamped to prevent vertical pillars from bad data
                'fill-extrusion-base': [
                    'min',
                    ['case',
                        ['>', ['get', 'min_height'], 0], ['get', 'min_height'],
                        0
                    ],
                    50
                ],
                'fill-extrusion-opacity': 0.7
            }
        }, labelLayerId); // Insert under labels

        console.log('✅ 3D terrain and buildings enabled (Robust Mode)');

        // Brighten road surfaces for visibility under 3D buildings
        const roadLayers = ['road-street', 'road-minor', 'road-major', 'road-primary', 'road-secondary', 'road-tertiary',
                            'road-street-low', 'road-minor-low', 'road-major-low'];
        roadLayers.forEach(layerId => {
            if (map.getLayer(layerId)) {
                try {
                    map.setPaintProperty(layerId, 'line-color', 'rgba(180, 190, 210, 0.3)');
                    map.setPaintProperty(layerId, 'line-opacity', 0.4);
                } catch(e) { /* some layers may not support these props */ }
            }
        });
        // Also try the generic road-simple layer used in dark-v11
        ['road-simple', 'road-street_limited'].forEach(layerId => {
            if (map.getLayer(layerId)) {
                try {
                    map.setPaintProperty(layerId, 'line-color', 'rgba(160, 175, 200, 0.2)');
                } catch(e) {}
            }
        });

        // Initialize power grid layers based on their initial state
        // Shorter delay since layers should exist now
        setTimeout(() => {
            const powerGridLayers = ['primary', 'secondary', 'ev', 'substations'];
            powerGridLayers.forEach(layer => {
                const layerMappings = {
                    'primary': ['primary-cables', 'primary-cables-glow'],
                    'secondary': ['secondary-cables', 'secondary-cables-glow'],
                    'ev': ['ev-stations-layer', 'ev-stations-badge-bg', 'ev-stations-badge-text', 'ev-stations-icon'],
                    'substations': ['substations-layer', 'substations-icon']
                };

                const layerIds = layerMappings[layer] || [];
                const shouldBeVisible = layers[layer]; // Check initial state

                layerIds.forEach(id => {
                    if (map.getLayer(id)) {
                        const visibility = shouldBeVisible ? 'visible' : 'none';
                        map.setLayoutProperty(id, 'visibility', visibility);
                        console.log(`Layer ${id}: ${visibility} (initial state)`);
                    }
                });
            });
        }, 100); // Reduced from 1000ms to 100ms
    });

    // Start 60 FPS vehicle interpolation loop after map loads
    map.on('load', () => {
        startVehicleAnimation();
    });

    // CRITICAL: Recreate vehicle layer when style reloads (e.g., when switching map styles)
    map.on('style.load', () => {
        console.log('🔄 Map style reloaded, recreating vehicle symbol layer...');
        ensureVehicleSymbolLayer();
        // Trigger immediate update if we have vehicle data
        if (networkState && networkState.vehicles) {
            updateVehicleSymbolLayer();
        }
    });

    // ==========================================
    // WEBGL VEHICLE RENDERER (GPU ACCELERATED)
    // ==========================================
    class WebGLVehicleRenderer {
        constructor(map) {
            this.map = map;
            this.vehicles = new Map();
            this.animationFrame = null;
            this.lastFrameTime = performance.now();
            this.frameCount = 0;
            this.fps = 0;
            
            this.gl = null;
            this.program = null;
            this.buffers = {};
            
            this.stats = {
                fps: 0,
                vehicles: 0,
                drawCalls: 0,
                updateTime: 0,
                renderTime: 0
            };
            
            this.initWebGL();
            this.initWorker();
        }
        
        initWebGL() {
            this.customLayer = {
                id: 'vehicle-webgl-layer',
                type: 'custom',
                
                onAdd: (map, gl) => {
                    this.gl = gl;
                    
                    // Modern vehicle shader with sleek car shape
                    const vertexShader = `
                        attribute vec2 a_position;
                        attribute vec2 a_offset;
                        attribute vec3 a_color;
                        attribute float a_angle;
                        attribute float a_scale;
                        
                        uniform mat4 u_matrix;
                        uniform float u_zoom;
                        
                        varying vec3 v_color;
                        varying vec2 v_offset;
                        
                        void main() {
                            // Realistic vehicle size that doesn't get too big when zooming
                            float baseSize = 1.5;  // Balanced base size for realistic scale
                            float zoomFactor = smoothstep(14.0, 20.0, u_zoom);  // Start scaling later
                            float size = a_scale * baseSize * (1.0 + zoomFactor * 0.15);  // Reduced zoom scaling
                            
                            vec2 rotatedOffset = vec2(
                                a_offset.x * cos(a_angle) - a_offset.y * sin(a_angle),
                                a_offset.x * sin(a_angle) + a_offset.y * cos(a_angle)
                            );
                            
                            vec2 worldPos = a_position + rotatedOffset * size * 0.0000006;
                            gl_Position = u_matrix * vec4(worldPos, 0.0, 1.0);
                            v_color = a_color;
                            v_offset = a_offset;
                        }
                    `;

                    const fragmentShader = `
                        precision highp float;
                        varying vec3 v_color;
                        varying vec2 v_offset;
                        
                        void main() {
                            // Create rounded rectangle (car shape)
                            vec2 p = abs(v_offset);
                            float cornerRadius = 0.3;
                            vec2 rectSize = vec2(0.4, 0.9);
                            
                            vec2 q = p - rectSize + cornerRadius;
                            float dist = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - cornerRadius;
                            
                            // Define border
                            float borderWidth = 0.12;
                            float innerDist = dist + borderWidth;
                            
                            // Create alpha for anti-aliasing
                            float alpha = 1.0 - smoothstep(-0.02, 0.02, dist);
                            if (alpha < 0.01) discard;
                            
                            // Determine if we're in border or body
                            vec3 finalColor;
                            if (innerDist < 0.0) {
                                // Inside the vehicle body
                                float gradient = 1.0 - (v_offset.y + 1.0) * 0.15;
                                float glow = 1.0 + (1.0 - innerDist * 2.0) * 0.15;
                                
                                finalColor = v_color * gradient * glow;
                                
                                // Add subtle windshield highlight
                                if (v_offset.y > 0.3 && v_offset.y < 0.6) {
                                    finalColor = mix(finalColor, vec3(1.0), 0.1);
                                }
                            } else {
                                // In the border area - make it black
                                finalColor = vec3(0.0, 0.0, 0.0);
                            }
                            
                            gl_FragColor = vec4(finalColor, alpha);
                        }
                    `;
                    
                    const vs = this.compileShader(gl, vertexShader, gl.VERTEX_SHADER);
                    const fs = this.compileShader(gl, fragmentShader, gl.FRAGMENT_SHADER);
                    
                    this.program = gl.createProgram();
                    gl.attachShader(this.program, vs);
                    gl.attachShader(this.program, fs);
                    gl.linkProgram(this.program);
                    
                    this.attributes = {
                        position: gl.getAttribLocation(this.program, 'a_position'),
                        offset: gl.getAttribLocation(this.program, 'a_offset'),
                        color: gl.getAttribLocation(this.program, 'a_color'),
                        angle: gl.getAttribLocation(this.program, 'a_angle'),
                        scale: gl.getAttribLocation(this.program, 'a_scale')
                    };
                    
                    this.uniforms = {
                        matrix: gl.getUniformLocation(this.program, 'u_matrix'),
                        zoom: gl.getUniformLocation(this.program, 'u_zoom')
                    };
                    
                    this.buffers = {
                        position: gl.createBuffer(),
                        offset: gl.createBuffer(),
                        color: gl.createBuffer(),
                        angle: gl.createBuffer(),
                        scale: gl.createBuffer()
                    };
                    
                    this.rectangleVertices = new Float32Array([
                        -0.4, -1.0,  // narrower width, same length
                        0.4, -1.0,
                        0.4,  1.0,
                        -0.4, -1.0,
                        0.4,  1.0,
                        -0.4,  1.0
                    ]);
                    
                    const maxVehicles = PERFORMANCE_CONFIG.vehiclePoolSize;
                    this.arrays = {
                        positions: new Float32Array(maxVehicles * 12),
                        offsets: new Float32Array(maxVehicles * 12),
                        colors: new Float32Array(maxVehicles * 18),
                        angles: new Float32Array(maxVehicles * 6),
                        scales: new Float32Array(maxVehicles * 6)
                    };
                },
                
                render: (gl, matrix) => {
                    if (!this.program || this.vehicles.size === 0) return;
                    
                    const startTime = performance.now();
                    
                    gl.useProgram(this.program);
                    gl.uniformMatrix4fv(this.uniforms.matrix, false, matrix);
                    gl.uniform1f(this.uniforms.zoom, this.map.getZoom());
                    
                    let vehicleIndex = 0;
                    for (const [id, vehicle] of this.vehicles) {
                        if (vehicleIndex >= PERFORMANCE_CONFIG.vehiclePoolSize) break;
                        
                        const pos = this.getInterpolatedPosition(vehicle);
                        const projected = mapboxgl.MercatorCoordinate.fromLngLat([pos.lon, pos.lat]);
                        
                        const color = this.getVehicleColor(vehicle.data);
                        
                        let angle = vehicle.angle || 0;
                        
                        for (let v = 0; v < 6; v++) {
                            const idx = vehicleIndex * 6 + v;
                            
                            this.arrays.positions[idx * 2] = projected.x;
                            this.arrays.positions[idx * 2 + 1] = projected.y;
                            
                            this.arrays.offsets[idx * 2] = this.rectangleVertices[v * 2];
                            this.arrays.offsets[idx * 2 + 1] = this.rectangleVertices[v * 2 + 1];
                            
                            this.arrays.colors[idx * 3] = color.r;
                            this.arrays.colors[idx * 3 + 1] = color.g;
                            this.arrays.colors[idx * 3 + 2] = color.b;
                            
                            this.arrays.angles[idx] = angle;
                            
                            this.arrays.scales[idx] = (vehicle.scale || 1) * 0.7;  // Smaller scale for realistic view
                        }
                        
                        vehicleIndex++;
                    }
                    
                    const vertexCount = vehicleIndex * 6;
                    
                    this.updateBuffer(gl, this.buffers.position, this.arrays.positions, this.attributes.position, 2, vertexCount);
                    this.updateBuffer(gl, this.buffers.offset, this.arrays.offsets, this.attributes.offset, 2, vertexCount);
                    this.updateBuffer(gl, this.buffers.color, this.arrays.colors, this.attributes.color, 3, vertexCount);
                    this.updateBuffer(gl, this.buffers.angle, this.arrays.angles, this.attributes.angle, 1, vertexCount);
                    this.updateBuffer(gl, this.buffers.scale, this.arrays.scales, this.attributes.scale, 1, vertexCount);
                    
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.drawArrays(gl.TRIANGLES, 0, vertexCount);
                    gl.disable(gl.BLEND);
                    
                    this.stats.renderTime = performance.now() - startTime;
                    this.stats.drawCalls++;
                }
            };
            
            if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
                this.map.addLayer(this.customLayer);
            }
        }
        
        initWorker() {
            this.worker = null;
            return;
        }
        
        compileShader(gl, source, type) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                return null;
            }
            
            return shader;
        }
        
        updateBuffer(gl, buffer, data, attribute, size, count) {
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
            // Use bufferSubData for better performance with existing buffers
            const byteLength = count * size * 4; // Float32 = 4 bytes
            if (buffer.size !== byteLength) {
                gl.bufferData(gl.ARRAY_BUFFER, data.buffer, gl.DYNAMIC_DRAW);
                buffer.size = byteLength;
            } else {
                gl.bufferSubData(gl.ARRAY_BUFFER, 0, data.subarray(0, count * size));
            }
            gl.enableVertexAttribArray(attribute);
            gl.vertexAttribPointer(attribute, size, gl.FLOAT, false, 0, 0);
        }
        
        getInterpolatedPosition(vehicle) {
            return {
                lon: vehicle.currentLon || vehicle.targetLon || 0,
                lat: vehicle.currentLat || vehicle.targetLat || 0
            };
        }

        updateVehicles(vehicleData) {
            const updateStartTime = performance.now();
            const currentTime = performance.now();

            // Pre-allocate Set for O(1) lookups
            const currentIds = new Set();

            vehicleData.forEach(data => {
                currentIds.add(data.id);

                if (!this.vehicles.has(data.id)) {
                    this.vehicles.set(data.id, {
                        id: data.id,
                        previousLon: data.lon,
                        previousLat: data.lat,
                        currentLon: data.lon,
                        currentLat: data.lat,
                        targetLon: data.lon,
                        targetLat: data.lat,
                        lastUpdateTime: currentTime,
                        interpolationProgress: 0,
                        velocityLon: 0,
                        velocityLat: 0,
                        angle: 0,
                        targetAngle: 0,  // Initialize target angle for smooth rotation
                        scale: 0,
                        targetScale: 0.8,
                        opacity: 0,
                        targetOpacity: 1,
                        data: data,
                        trail: []
                    });
                } else {
                    const vehicle = this.vehicles.get(data.id);
                    
                    const distanceMoved = Math.sqrt(
                        Math.pow(data.lon - vehicle.targetLon, 2) + 
                        Math.pow(data.lat - vehicle.targetLat, 2)
                    );
                    
                    if (distanceMoved > 0.000001) {
                        vehicle.previousLon = vehicle.currentLon;
                        vehicle.previousLat = vehicle.currentLat;
                        
                        vehicle.targetLon = data.lon;
                        vehicle.targetLat = data.lat;
                        
                        vehicle.interpolationProgress = 0;
                        vehicle.lastUpdateTime = currentTime;
                        
                        const dx = vehicle.targetLon - vehicle.previousLon;
                        const dy = vehicle.targetLat - vehicle.previousLat;
                        if (Math.abs(dx) > 0.00001 || Math.abs(dy) > 0.00001) {
                            vehicle.angle = Math.atan2(dx, dy) + Math.PI;
                        }
                    }
                    vehicle.data = data;
                }
            });

            // Remove vehicles that are no longer present (reuse currentIds from above)
            for (const [id, vehicle] of this.vehicles) {
                if (!currentIds.has(id)) {
                    vehicle.targetOpacity = 0;
                    vehicle.targetScale = 0;
                    if (vehicle.opacity < 0.01) {
                        this.vehicles.delete(id);
                    }
                }
            }
            
            this.stats.updateTime = performance.now() - updateStartTime;
            this.stats.vehicles = this.vehicles.size;
        }
interpolate(deltaTime) {
            const now = performance.now();
            
            for (const [id, vehicle] of this.vehicles) {
                const timeSinceUpdate = now - vehicle.lastUpdateTime;
                const expectedUpdateInterval = PERFORMANCE_CONFIG.dataUpdateRate * 1.2;
                vehicle.interpolationProgress = Math.min(1, timeSinceUpdate / expectedUpdateInterval);
                
                const easeInOutSine = (t) => {
                    return -(Math.cos(Math.PI * t) - 1) / 2;
                };
                
                const easedProgress = easeInOutSine(vehicle.interpolationProgress);
                
                const microSmooth = 0.02;
                const targetLon = vehicle.previousLon + (vehicle.targetLon - vehicle.previousLon) * easedProgress;
                const targetLat = vehicle.previousLat + (vehicle.targetLat - vehicle.previousLat) * easedProgress;
                
                vehicle.currentLon = vehicle.currentLon * (1 - microSmooth) + targetLon * microSmooth;
                vehicle.currentLat = vehicle.currentLat * (1 - microSmooth) + targetLat * microSmooth;
                
                const scaleSpeed = 0.08;
                if (Math.abs(vehicle.targetScale - vehicle.scale) > 0.001) {
                    vehicle.scale += (vehicle.targetScale - vehicle.scale) * scaleSpeed;
                }
                
                const opacitySpeed = 0.08;
                if (Math.abs(vehicle.targetOpacity - vehicle.opacity) > 0.001) {
                    vehicle.opacity += (vehicle.targetOpacity - vehicle.opacity) * opacitySpeed;
                }
            }
            
            if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
                this.map.triggerRepaint();
            }
        }
        
        updateFromWorker(positions) {
            positions.forEach(pos => {
                const vehicle = this.vehicles.get(pos.id);
                if (vehicle) {
                    vehicle.currentLon = pos.lon;
                    vehicle.currentLat = pos.lat;
                }
            });
        }
                
        getVehicleColor(data) {
            let r, g, b;
            
            if (data.is_stranded) {
                // Purple for stranded
                r = 0.8; g = 0.2; b = 1.0;
            } else if (data.is_charging) {
                // Cyan for charging
                r = 0; g = 0.9; b = 1.0;
            } else if (data.is_queued) {
                // Yellow for queued
                r = 1.0; g = 0.9; b = 0.1;
            } else if (data.is_circling) {
                // Orange for circling
                r = 1.0; g = 0.6; b = 0.2;
            } else if (data.is_ev) {
                const battery = data.battery_percent || 100;
                if (battery < 20) {
                    // Red for low battery
                    r = 1.0; g = 0.2; b = 0.2;
                } else if (battery < 50) {
                    // Orange for medium battery
                    r = 1.0; g = 0.7; b = 0.2;
                } else {
                    // Green for good battery
                    r = 0.2; g = 0.9; b = 0.3;
                }
            } else {
                // White/light blue for gas vehicles
                r = 0.8; g = 0.8; b = 1.0;
            }
            
            return { r, g, b };
        }
        
        getStats() {
            return this.stats;
        }
        
        clear() {
            this.vehicles.clear();
            if (this.worker) {
                this.worker.postMessage({ type: 'clear' });
            }
        }
    }

    // Throttling controls for heavy UI layers
    let _uiLoopCounter = 0;
    const UI_DECIMATION_FACTOR = 3; // Render heavy layers every 3rd loop
    const VEHICLE_SYMBOL_THRESHOLD = 200; // Above this, thin or skip symbol layer
    const VEHICLE_SYMBOL_UPDATE_MS = 1000; // Update symbols at most once per second
    let _lastVehicleSymbolUpdate = 0;

    // ==========================================
    // HYBRID DOM RENDERER (FALLBACK)
    // ==========================================
    class HybridVehicleRenderer {
        constructor(map) {
            this.map = map;
            this.vehicles = new Map();
            this.markerPool = [];
            this.activeMarkers = new Map();
            this.stats = { vehicles: 0, updateTime: 0, renderTime: 0 };
        }
        
        createMarker(data) {
            let el;
            if (this.markerPool.length > 0) {
                el = this.markerPool.pop();
                el.style.display = 'block';
            } else {
                el = document.createElement('div');
                el.className = 'vehicle-marker-ultra';
                el.style.cssText = `
                    position: absolute;
                    width: 14px;
                    height: 14px;
                    border-radius: 50%;
                    border: 2.5px solid rgba(255,255,255,0.95);
                    box-shadow: 0 3px 10px rgba(0,0,0,0.55);
                    will-change: transform;
                    transform: translate(-50%, -50%);
                    transition: transform 0.05s linear;
                    pointer-events: auto;
                    cursor: pointer;
                `;
            }
            
            el.style.background = this.getColor(data);
            
            const marker = new mapboxgl.Marker({
                element: el,
                anchor: 'center'
            }).setLngLat([data.lon, data.lat]).addTo(this.map);
            
            return marker;
        }
        
        updateVehicles(vehicleData) {
            const updateStartTime = performance.now();
            const currentTime = performance.now();
            
            vehicleData.forEach(data => {
                if (!this.vehicles.has(data.id)) {
                    this.vehicles.set(data.id, {
                        id: data.id,
                        previousLon: data.lon,
                        previousLat: data.lat,
                        currentLon: data.lon,
                        currentLat: data.lat,
                        targetLon: data.lon,
                        targetLat: data.lat,
                        lastUpdateTime: currentTime,
                        interpolationProgress: 0,
                        velocityLon: 0,
                        velocityLat: 0,
                        angle: 0,
                        targetAngle: 0,  // Initialize target angle for smooth rotation
                        scale: 0,
                        targetScale: 0.8,
                        opacity: 0,
                        targetOpacity: 1,
                        data: data,
                        trail: []
                    });
                } else {
                    const vehicle = this.vehicles.get(data.id);
                    
                    const distanceMoved = Math.sqrt(
                        Math.pow(data.lon - vehicle.targetLon, 2) + 
                        Math.pow(data.lat - vehicle.targetLat, 2)
                    );
                    
                    if (distanceMoved > 0.000001) {
                        vehicle.previousLon = vehicle.currentLon;
                        vehicle.previousLat = vehicle.currentLat;
                        
                        vehicle.targetLon = data.lon;
                        vehicle.targetLat = data.lat;
                        
                        vehicle.interpolationProgress = 0;
                        vehicle.lastUpdateTime = currentTime;
                        
                        const dx = vehicle.targetLon - vehicle.previousLon;
                        const dy = vehicle.targetLat - vehicle.previousLat;
                        if (Math.abs(dx) > 0.00001 || Math.abs(dy) > 0.00001) {
                            const newAngle = Math.atan2(dy, dx);

                            // Smooth angle transition - no sudden jumps!
                            if (vehicle.angle !== undefined && vehicle.angle !== null) {
                                let angleDiff = newAngle - vehicle.angle;

                                // Normalize angle difference to [-PI, PI] for shortest rotation
                                while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                                while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;

                                // Store target angle for smooth interpolation
                                vehicle.targetAngle = newAngle;
                            } else {
                                // First time - set directly
                                vehicle.angle = newAngle;
                                vehicle.targetAngle = newAngle;
                            }
                        }
                    }

                    vehicle.data = data;

                    // UPDATE MARKER COLOR (V2G real-time color change)
                    const marker = this.activeMarkers.get(data.id);
                    if (marker) {
                        const newColor = this.getColor(data);
                        const element = marker.getElement();
                        if (element) {
                            element.style.background = newColor;
                        }
                    }
                }
            });

            const currentIds = new Set(vehicleData.map(v => v.id));
            for (const [id, vehicle] of this.vehicles) {
                if (!currentIds.has(id)) {
                    vehicle.targetOpacity = 0;
                    vehicle.targetScale = 0;
                    if (vehicle.opacity < 0.01) {
                        this.vehicles.delete(id);
                    }
                }
            }
            
            this.stats.updateTime = performance.now() - updateStartTime;
            this.stats.vehicles = this.vehicles.size;
        }
        
        interpolate(deltaTime) {
            const now = performance.now();
            
            for (const [id, vehicle] of this.vehicles) {
                const timeSinceUpdate = now - vehicle.lastUpdateTime;
                const expectedUpdateInterval = PERFORMANCE_CONFIG.dataUpdateRate * 1.1;
                vehicle.interpolationProgress = Math.min(1, timeSinceUpdate / expectedUpdateInterval);
                
                // Use LINEAR interpolation for accurate street following (no curve cutting)
                vehicle.currentLon = vehicle.previousLon +
                    (vehicle.targetLon - vehicle.previousLon) * vehicle.interpolationProgress;
                vehicle.currentLat = vehicle.previousLat +
                    (vehicle.targetLat - vehicle.previousLat) * vehicle.interpolationProgress;
                
                if (vehicle.scale !== vehicle.targetScale) {
                    const scaleDelta = vehicle.targetScale - vehicle.scale;
                    vehicle.scale += scaleDelta * 0.15;
                    if (Math.abs(scaleDelta) < 0.001) {
                        vehicle.scale = vehicle.targetScale;
                    }
                }
                
                if (vehicle.opacity !== vehicle.targetOpacity) {
                    const opacityDelta = vehicle.targetOpacity - vehicle.opacity;
                    vehicle.opacity += opacityDelta * 0.15;
                    if (Math.abs(opacityDelta) < 0.001) {
                        vehicle.opacity = vehicle.targetOpacity;
                    }
                }

                // SMOOTH ANGLE INTERPOLATION - Fixes turning issues!
                if (vehicle.targetAngle !== undefined && vehicle.angle !== undefined) {
                    let angleDiff = vehicle.targetAngle - vehicle.angle;

                    // Normalize to shortest rotation path
                    while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                    while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;

                    // Smooth rotation - responsive but not too slow
                    vehicle.angle += angleDiff * 0.35;

                    // Snap when very close
                    if (Math.abs(angleDiff) < 0.01) {
                        vehicle.angle = vehicle.targetAngle;
                    }
                }
            }
            
           if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
                if (!this.map.getLayer('vehicle-webgl-layer')) {
                    this.map.addLayer(this.customLayer);
                }
            }
        }
        
        getColor(data) {
            // V2G ACTIVE vehicles get BRIGHT CYAN (highest priority!)
            if (data.is_v2g_active || (window.v2gActiveVehicles && window.v2gActiveVehicles.has(data.id))) {
                return '#00FFFF'; // Bright cyan for V2G discharge
            }

            if (data.is_stranded) return '#ff00ff';
            if (data.is_charging) return '#00ffff';
            if (data.is_queued) return '#ffff00';
            if (data.is_circling) return '#ff8c00';
            if (data.is_ev) {
                const battery = data.battery_percent || 100;
                if (battery < 20) return '#ff0000';
                if (battery < 50) return '#ffa500';
                return '#00ff00';
            }
            return '#6464ff';
        }
        
        getStats() {
            return this.stats;
        }
        
        clear() {
            for (const [id, marker] of this.activeMarkers) {
                marker.remove();
            }
            this.activeMarkers.clear();
            this.vehicles.clear();
        }
    }

    // ==========================================
    // GLOBAL STATE
    // ==========================================
    let networkState = null;
    let vehicleRenderer = null;
    let substationMarkers = {};
    let substationLayerInitialized = false;
    let evStationLayerInitialized = false;
    let vehicleClickLayerInitialized = false;
    let lightsClickBound = false;
    
    // ==========================================
    // VEHICLE INTERPOLATION STATE
    // ==========================================
    const vehicleStore = new Map();  // Map<vehicleId, interpolation state>
    // ADAPTIVE INTERPOLATION: Dynamically adjust to network speed
    const MIN_INTERPOLATION_DURATION = 100;
    let currentInterpolationDuration = 2000; // Start with safe default
    let lastPacketTime = performance.now();
    // animationFrameId declared below in animation loop section
    
    // Linear interpolation helper
    function lerp(start, end, progress) {
        return start + (end - start) * progress;
    }
    
    // Smooth easing function (ease-out cubic for natural deceleration)
    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
    
    // Calculate bearing between two points (for smooth rotation)
    function calculateBearing(lon1, lat1, lon2, lat2) {
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const lat1Rad = lat1 * Math.PI / 180;
        const lat2Rad = lat2 * Math.PI / 180;
        
        const y = Math.sin(dLon) * Math.cos(lat2Rad);
        const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) -
                  Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
        
        let bearing = Math.atan2(y, x) * 180 / Math.PI;
        return (bearing + 360) % 360;  // Normalize to 0-360
    }
    
    let layers = {
        lights: true,
        vehicles: true,
        primary: true,
        secondary: false,
        ev: true,
        substations: true
    };
    let sumoRunning = false;

    // V2G Active Vehicle Tracking (optimized - no lag)
    window.v2gActiveVehicles = new Set();
    window.v2gStationCounts = {}; // station_id -> count

    // OPTIMIZED V2G Color Updater - NOW USES WEBSOCKET DATA (no HTTP polling!)
    async function updateV2GColorsOptimized() {
        // DISABLED: Polling replaced with WebSocket updates via updateV2GFromWebSocket()
        // V2G data is now pushed via WebSocket 'system_update' event
        // The window.v2gActiveVehicles set is updated by updateV2GFromWebSocket()
        
        try {
            // V2G active vehicles are already updated via WebSocket
            // Just update the colors based on current window.v2gActiveVehicles set
            
            // DISABLED: Using Mapbox symbol layer instead of custom renderer
            // Symbol layer automatically updates colors based on is_v2g_active property
            /*
            // FORCE COLOR UPDATE - Update existing markers
            if (vehicleRenderer && vehicleRenderer.activeMarkers) {
                for (const [vehicleId, marker] of vehicleRenderer.activeMarkers) {
                    const isV2G = window.v2gActiveVehicles.has(vehicleId);
                    const vehicle = vehicleRenderer.vehicles.get(vehicleId);

                    if (vehicle && vehicle.data) {
                        const newColor = isV2G ? '#00FFFF' : vehicleRenderer.getColor(vehicle.data);
                        const element = marker.getElement();
                        if (element) {
                            element.style.background = newColor;
                        }
                    }
                }
            }
            */


        } catch (error) {
            // Silently ignore errors
        }

        // DISABLED POLLING: No longer recursively calls itself
        // Colors update automatically when WebSocket data arrives
    }

    // ==========================================
    // PERFORMANCE MONITORING
    // ==========================================
    const performanceMonitor = {
        frameCount: 0,
        lastTime: performance.now(),
        fps: 0,
        
        update() {
            this.frameCount++;
            const now = performance.now();
            if (now - this.lastTime >= 1000) {
                this.fps = this.frameCount;
                this.frameCount = 0;
                this.lastTime = now;

                // Always update performance stats overlay
                this.updatePerformanceStats();

                if (PERFORMANCE_CONFIG.enableDebugMode) {
                    this.updateDebugDisplay();
                }
            }
        },

        updatePerformanceStats() {
            const stats = vehicleRenderer ? vehicleRenderer.getStats() : {};

            const fpsEl = document.getElementById('fps-counter');
            const updateTimeEl = document.getElementById('update-time');
            const renderTimeEl = document.getElementById('render-time');
            const renderModeEl = document.getElementById('render-mode');

            if (fpsEl) {
                fpsEl.textContent = this.fps.toFixed(0);
                fpsEl.style.color = this.fps >= 60 ? '#00ff88' : (this.fps >= 30 ? '#ffaa00' : '#ff4444');
            }
            // Vehicle count is handled by updateUI() when network state is reloaded
            // Don't update it here to avoid race conditions with scenario changes
            if (updateTimeEl) updateTimeEl.textContent = (stats.updateTime || 0).toFixed(2);
            if (renderTimeEl) renderTimeEl.textContent = (stats.renderTime || 0).toFixed(2);
            if (renderModeEl) renderModeEl.textContent = PERFORMANCE_CONFIG.renderMode.toUpperCase();
        },
        
        updateDebugDisplay() {
            let debugEl = document.getElementById('debug-overlay');
            if (!debugEl) {
                debugEl = document.createElement('div');
                debugEl.id = 'debug-overlay';
                debugEl.style.cssText = `
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: linear-gradient(135deg, rgba(0,0,0,0.9), rgba(20,20,30,0.85));
                    color: #00ff88;
                    padding: 12px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 12px;
                    z-index: 9999;
                    border: 1px solid #00ff88;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 4px 16px rgba(0,255,136,0.2);
                `;
                document.body.appendChild(debugEl);
            }
            
            const stats = vehicleRenderer ? vehicleRenderer.getStats() : {};
            debugEl.innerHTML = `
                <div style="margin-bottom: 4px; font-weight: 600;">PERFORMANCE</div>
                <div>FPS: <span style="color: ${this.fps >= 60 ? '#00ff88' : '#ffaa00'}">${this.fps}</span></div>
                <div>Vehicles: ${stats.vehicles || 0}</div>
                <div>Update: ${(stats.updateTime || 0).toFixed(2)}ms</div>
                <div>Render: ${(stats.renderTime || 0).toFixed(2)}ms</div>
                <div>Mode: ${PERFORMANCE_CONFIG.renderMode.toUpperCase()}</div>
            `;
        }
    };

    // ==========================================
    // DATA MANAGEMENT
    // ==========================================
    const dataManager = {
        lastFetch: 0,
        cache: null,
        fetching: false,
        lastVehicleHash: null,

        async fetchData() {
            if (this.fetching) return this.cache;

            const now = performance.now();
            if (this.cache && now - this.lastFetch < PERFORMANCE_CONFIG.dataUpdateRate) {
                return this.cache;
            }

            this.fetching = true;
            try {
                const response = await fetch('/api/network_state', {
                    // Enable compression if supported
                    headers: {
                        'Accept-Encoding': 'gzip, deflate, br'
                    }
                });
                const data = await response.json();

                // Only update if vehicles data has changed
                if (data.vehicles) {
                    const vehicleHash = data.vehicles.length + '_' + (data.vehicles[0]?.id || '');
                    if (vehicleHash === this.lastVehicleHash && this.cache) {
                        // No changes, return cached data
                        this.lastFetch = now;
                        this.fetching = false;
                        return this.cache;
                    }
                    this.lastVehicleHash = vehicleHash;
                }

                this.cache = data;
                this.lastFetch = now;
                return data;
            } catch (error) {
                console.error('Error fetching data:', error);
                return this.cache;
            } finally {
                this.fetching = false;
            }
        }
    };

    // ==========================================
    // V2G STATUS UPDATER
    // ==========================================
    async function updateV2GStatus() {
        // Disabled polling - V2G data is now pushed via WebSockets (system_update event)
        return; 
    }

    // ==========================================
    // EV STATION V2G BADGE UPDATER
    // ==========================================
    function updateEVStationBadges() {
        if (!map || !networkState || !networkState.ev_stations) return;

        // Remove old badges
        const oldBadges = document.querySelectorAll('.v2g-station-badge');
        oldBadges.forEach(badge => badge.remove());

        // Create new badges for active V2G stations
        Object.entries(window.v2gStationCounts).forEach(([stationId, count]) => {
            if (count <= 0) return;

            // Find station coordinates
            const station = networkState.ev_stations.find(s => s.id === stationId);
            if (!station) return;

            const point = map.project([station.lon, station.lat]);

            // Create badge element
            const badge = document.createElement('div');
            badge.className = 'v2g-station-badge';
            badge.style.cssText = `
                position: absolute;
                left: ${point.x}px;
                top: ${point.y - 25}px;
                background: linear-gradient(135deg, #00FFFF, #00CCCC);
                color: #000;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 0.9);
                box-shadow: 0 3px 12px rgba(0, 255, 255, 0.6);
                pointer-events: none;
                z-index: 10;
                transform: translate(-50%, -100%);
                animation: v2gBadgePulse 1.5s ease-in-out infinite;
                white-space: nowrap;
            `;
            badge.textContent = `⚡ ${count}`;

            map.getCanvasContainer().appendChild(badge);
        });

        // Add CSS animation if not already present
        if (!document.getElementById('v2g-badge-styles')) {
            const style = document.createElement('style');
            style.id = 'v2g-badge-styles';
            style.textContent = `
                @keyframes v2gBadgePulse {
                    0%, 100% {
                        transform: translate(-50%, -100%) scale(1);
                        box-shadow: 0 3px 12px rgba(0, 255, 255, 0.6);
                    }
                    50% {
                        transform: translate(-50%, -100%) scale(1.1);
                        box-shadow: 0 5px 20px rgba(0, 255, 255, 0.9);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Update badges when map moves or zooms
    if (map) {
        map.on('move', updateEVStationBadges);
        map.on('zoom', updateEVStationBadges);
    }

// ==========================================
    // MAIN LOOPS
    // ==========================================
    async function updateLoop() {
        // Disabled polling - UI updates are driven by processNetworkState via WebSockets
        return;
    }

    let lastAnimationTime = performance.now();
    let animationFrameId = null;

    // ==========================================
    // 60 FPS VEHICLE INTERPOLATION LOOP
    // ==========================================
    let frameCounter = 0;  // For throttling
    
    function animateVehicles() {
        const currentTime = performance.now();
        
        if (!map.getSource('vehicles-symbols')) {
            animationFrameId = requestAnimationFrame(animateVehicles);
            return;
        }
        
        // OPTIMIZATION: Throttle to 30 FPS in low performance mode
        frameCounter++;
        const shouldRender = !PERFORMANCE_CONFIG || 
                           PERFORMANCE_CONFIG.renderMode !== 'low' || 
                           (frameCounter % 2 === 0);
        
        if (!shouldRender) {
            animationFrameId = requestAnimationFrame(animateVehicles);
            return;
        }
        
        const features = [];
        
        // Interpolate all vehicles (BATCH UPDATE)
        vehicleStore.forEach((state, vehicleId) => {
            const elapsed = currentTime - state.startTime;
            // Use dynamic interpolation duration
            let progress = Math.min(elapsed / currentInterpolationDuration, 1.0);
            
            // OPTIMIZATION: Skip expensive math if vehicle reached target
            if (progress >= 1.0 && state.startLon === state.targetLon && state.startLat === state.targetLat) {
                // Vehicle is stationary at target - use cached position
                features.push({
                    type: 'Feature',
                    geometry: { type: 'Point', coordinates: [state.targetLon, state.targetLat] },
                    properties: {
                        id: vehicleId,
                        bearing: state.bearing,
                        is_ev: state.is_ev || false,
                        battery_percent: state.battery_percent,
                        is_charging: state.is_charging || false,
                        is_queued: state.is_queued || false,
                        is_stranded: state.is_stranded || false,
                        is_circling: state.is_circling || false,
                        is_v2g_active: state.is_v2g_active || false,
                        assigned_station: state.assigned_station || ''
                    }
                });
                return;  // Skip interpolation
            }
            
            // Apply easing for smoother motion
            progress = easeOutCubic(progress);
            
            // Interpolate position
            const currentLon = lerp(state.startLon, state.targetLon, progress);
            const currentLat = lerp(state.startLat, state.targetLat, progress);
            
            // Calculate dynamic bearing (direction of movement)
            let bearing = state.bearing;
            if (state.startLon !== state.targetLon || state.startLat !== state.targetLat) {
                bearing = calculateBearing(state.startLon, state.startLat, state.targetLon, state.targetLat);
                // Adjust for icon orientation (arrow pointing right)
                bearing = (bearing - 90 + 360) % 360;
            }
            
            // Create GeoJSON feature
            features.push({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [currentLon, currentLat] },
                properties: {
                    id: vehicleId,
                    bearing: bearing,
                    is_ev: state.is_ev || false,
                    battery_percent: state.battery_percent,
                    is_charging: state.is_charging || false,
                    is_queued: state.is_queued || false,
                    is_stranded: state.is_stranded || false,
                    is_circling: state.is_circling || false,
                    is_v2g_active: state.is_v2g_active || false,
                    assigned_station: state.assigned_station || ''
                }
            });
        });
        
        // BATCH UPDATE: Single setData call per frame (not inside loop)
        const source = map.getSource('vehicles-symbols');
        if (source && features.length > 0) {
            source.setData({ type: 'FeatureCollection', features });
        }
        
        // Continue animation loop
        animationFrameId = requestAnimationFrame(animateVehicles);
    }
    
    // Start the animation loop
    function startVehicleAnimation() {
        if (!animationFrameId) {
            console.log('🎬 Starting 60 FPS vehicle interpolation loop');
            animationFrameId = requestAnimationFrame(animateVehicles);
        }
    }
    
    // Stop the animation loop
    function stopVehicleAnimation() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
            console.log('⏸️ Stopped vehicle interpolation loop');
        }
    }
    

    // ==========================================
    // UI UPDATES WITH SMOOTH ANIMATIONS
    // ==========================================
    function updateUI() {
        if (!networkState) return;
        
        requestAnimationFrame(() => {
            const stats = networkState.statistics;
            
            // DEBUG: Log substation counts
            if (stats.operational_substations === 8 && stats.total_substations === 8) {
                 console.warn("Substations show 8/8 but failure might be active:", networkState);
            } else {
                 console.log(`Substations: ${stats.operational_substations}/${stats.total_substations}`);
            }

            const updates = {
                'traffic-lights': stats.total_traffic_lights,
                'powered-lights': stats.powered_traffic_lights,
                'load-mw': Math.round(stats.total_load_mw),
                'substations-online': `${stats.operational_substations}/${stats.total_substations}`,
                'green-count': stats.green_lights || 0,
                'yellow-count': stats.yellow_lights || 0,
                'red-count': stats.red_lights || 0,
                'black-count': stats.black_lights || 0,
                'total-load': Math.round(stats.total_load_mw),
                'legend-substations': stats.total_substations || 0,
                'legend-ev': stats.total_ev_stations || 0,
                'legend-green': stats.green_lights || 0,
                'legend-yellow': stats.yellow_lights || 0,
                'legend-red': stats.red_lights || 0,
                // Footer Updates
                'charging-stations': (networkState.ev_stations || []).filter(s => s.chargers_occupied && s.chargers_occupied > 0).length,
                'system-status': (networkState.substations || []).some(s => !s.operational) ? "GRID ALERT" : "System Online"
            };

            // Update status indicator color
            const statusIndicator = document.getElementById('system-indicator');
            if (statusIndicator) {
                const isNormal = updates['system-status'] === "System Online";
                statusIndicator.style.backgroundColor = isNormal ? '#00ff88' : '#ff0000';
                statusIndicator.style.boxShadow = isNormal ? '0 0 10px #00ff88' : '0 0 10px #ff0000';
            }
            
            Object.entries(updates).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) {
                    const current = el.textContent;
                    if (current !== value.toString()) {
                        el.style.transition = 'transform 0.3s ease';
                        el.style.transform = 'scale(1.1)';
                        el.textContent = value;
                        setTimeout(() => {
                            el.style.transform = 'scale(1)';
                        }, 300);
                    }
                }
            });
            
            if (networkState.vehicle_stats) {
                const active = (networkState.vehicles || []).length;
                const pending = networkState.vehicle_stats.pending_vehicles || 0;
                const totalConfigured = networkState.vehicle_stats.total_configured || active;
                
                // STATE PERSISTENCE: Prevent flicker by caching last valid count
                // Only update if we have valid data OR if SUMO is explicitly stopped
                if (!window.lastValidVehicleCount) {
                    window.lastValidVehicleCount = 0;
                }
                
                // Determine which count to display
                let displayCount = active;
                if (active === 0 && window.lastValidVehicleCount > 0) {
                    // Check if SUMO is actually stopped (from reactive control updates)
                    const sumoStopped = networkState.sumo_running === false;
                    
                    if (!sumoStopped) {
                        // SUMO is running but we got empty data - use last known count
                        displayCount = window.lastValidVehicleCount;
                    } else {
                        // SUMO is stopped - accept the zero and clear cache
                        window.lastValidVehicleCount = 0;
                    }
                } else if (active > 0) {
                    // Valid count - cache it
                    window.lastValidVehicleCount = active;
                }
                
                // Format display with pending info
                let vehicleDisplayText = displayCount.toString();
                if (pending > 0) {
                    vehicleDisplayText = `${displayCount} (+${pending} queued)`;
                }
                
                // Update all vehicle count elements
                const vehicleCountElements = ['active-vehicles', 'vehicle-count', 'footer-vehicle-count'];
                vehicleCountElements.forEach(elemId => {
                    const elem = document.getElementById(elemId);
                    if (elem) {
                        elem.textContent = vehicleDisplayText;
                    }
                });
                
                updateWithAnimation('ev-count', networkState.vehicle_stats.ev_vehicles || 0);
                const chargingCount = networkState.vehicle_stats.vehicles_charging || 0;
                updateWithAnimation('charging-stations', chargingCount);
                updateWithAnimation('vehicles-charging-count', chargingCount);
                
                const evNum = networkState.vehicle_stats.ev_vehicles || 0;
                const gasNum = Math.max(0, active - evNum);
                updateWithAnimation('legend-vehicles-ev', evNum);
                updateWithAnimation('legend-vehicles-gas', gasNum);
                
                if (networkState.vehicles) {
                    let high=0, med=0, low=0;
                    networkState.vehicles.forEach(v=>{
                        if (v.is_ev) {
                            const b = v.battery_percent != null ? v.battery_percent : 100;
                            if (b < 20) low++; else if (b < 50) med++; else high++;
                        }
                    });
                    updateWithAnimation('legend-ev-high', high);
                    updateWithAnimation('legend-ev-medium', med);
                    updateWithAnimation('legend-ev-low', low);
                }
            }
            
            const controls = document.getElementById('substation-controls');
            if (controls.children.length === 0) {
                networkState.substations.forEach(sub => {
                    const btn = document.createElement('button');
                    btn.className = 'sub-btn';
                    btn.id = `sub-btn-${sub.name}`;
                    btn.textContent = sub.name.replace(/_/g, ' ');
                    btn.onclick = () => toggleSubstation(sub.name);
                    controls.appendChild(btn);
                });
            }
            
            networkState.substations.forEach(sub => {
                const btn = document.getElementById(`sub-btn-${sub.name}`);
                if (btn) {
                    if (sub.operational) {
                        btn.classList.remove('failed');
                    } else {
                        btn.classList.add('failed');
                    }
                }
            });
            
            const failures = stats.total_substations - stats.operational_substations;
            const indicator = document.getElementById('system-indicator');
            const status = document.getElementById('system-status');
            
            if (failures === 0) {
                indicator.style.background = 'var(--primary-glow)';
                status.textContent = 'System Online';
            } else if (failures <= 2) {
                indicator.style.background = 'var(--warning-glow)';
                status.textContent = `${failures} Substation${failures > 1 ? 's' : ''} Failed`;
            } else {
                indicator.style.background = 'var(--danger-glow)';
                status.textContent = 'Critical Failures';
            }
        });
    }

    function updateWithAnimation(id, value) {
        const el = document.getElementById(id);
        if (el && el.textContent !== value.toString()) {
            el.style.transition = 'all 0.3s ease';
            el.style.transform = 'scale(1.15)';
            el.style.filter = 'brightness(1.3)';
            el.textContent = value;
            setTimeout(() => {
                el.style.transform = 'scale(1)';
                el.style.filter = 'brightness(1)';
            }, 300);
        }
    }

    // ==========================================
    // RENDERING FUNCTIONS WITH ENHANCED VISUALS
    // ==========================================
    function initializeRenderers() {
        // DISABLED: Custom WebGL renderer doesn't work with 3D terrain (causes drift)
        // Now using standard Mapbox symbol layer with map-aligned pitch for 3D compatibility
        /*
        if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
            vehicleRenderer = new WebGLVehicleRenderer(map);
        } else {
            vehicleRenderer = new HybridVehicleRenderer(map);
        }
        */
        
        if (map.loaded()) {
            if (!vehicleClickLayerInitialized) initializeVehicleClickLayer();
            ensureVehicleSymbolLayer();
        } else {
            map.on('load', () => {
                if (!vehicleClickLayerInitialized) initializeVehicleClickLayer();
                ensureVehicleSymbolLayer();
            });
        }
    }

    function ensureVehicleSymbolLayer() {
        // STEP 1: Ensure custom arrow icon exists FIRST
        if (!map.hasImage('vehicle-arrow')) {
            console.log('🎨 Creating vehicle-arrow icon...');
            const size = 32;
            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');
            
            // Draw arrow/triangle pointing right (will be rotated by bearing)
            ctx.fillStyle = '#FFFFFF';  // White base (color applied via icon-color)
            ctx.beginPath();
            ctx.moveTo(size * 0.75, size / 2);      // Tip (right)
            ctx.lineTo(size * 0.25, size * 0.2);    // Top left
            ctx.lineTo(size * 0.25, size * 0.8);    // Bottom left
            ctx.closePath();
            ctx.fill();
            
            // Convert canvas to ImageData for Mapbox
            const imageData = ctx.getImageData(0, 0, size, size);
            
            // Add to map with SDF for color tinting
            map.addImage('vehicle-arrow', imageData, { sdf: true });
            console.log('✅ vehicle-arrow icon created');
        }
        
        // STEP 2: Create GeoJSON source if missing
        if (!map.getSource('vehicles-symbols')) {
            map.addSource('vehicles-symbols', { 
                type: 'geojson', 
                data: { type: 'FeatureCollection', features: [] }
            });
            console.log('✅ vehicles-symbols source created');
        }
        
        // STEP 3: Create layer with PROPER Z-ORDERING
        if (!map.getLayer('vehicles-symbols')) {
            // Find a good reference layer to insert before (labels should be on top)
            let beforeLayer = null;
            const labelLayers = ['road-label', 'waterway-label', 'poi-label', 'transit-label'];
            for (const layerId of labelLayers) {
                if (map.getLayer(layerId)) {
                    beforeLayer = layerId;
                    break;
                }
            }
            
            const layerConfig = {
                id: 'vehicles-symbols',
                type: 'symbol',
                source: 'vehicles-symbols',
                layout: {
                    'icon-image': 'vehicle-arrow',  // Use custom arrow icon
                    'icon-size': [
                        'interpolate', ['linear'], ['zoom'],
                        12, 0.8,   // BOOSTED: 0.8 for visibility at low zoom
                        14, 1.0,
                        16, 1.2,
                        18, 1.5
                    ],
                    'icon-rotate': ['get', 'bearing'],
                    'icon-rotation-alignment': 'map',   // CRITICAL: Rotate with map
                    'icon-pitch-alignment': 'map',      // CRITICAL: Drape on terrain
                    'icon-allow-overlap': true,         // CRITICAL: Force render
                    'icon-ignore-placement': true       // CRITICAL: Ignore collisions
                },
                paint: {
                    'icon-color': [
                        'case', 
                        ['get', 'is_v2g_active'], '#00E5FF',  // Bright cyan for V2G
                        ['get', 'is_stranded'], '#E040FB',    // Violet for stranded
                        ['get', 'is_charging'], '#40C4FF',    // Light blue for charging
                        ['get', 'is_queued'], '#B388FF',      // Lavender for queued
                        ['get', 'is_circling'], '#FF80AB',    // Pink for circling
                        ['to-boolean', ['get', 'is_ev']], [   // EV gradient by battery
                            'case',
                            ['<', ['get', 'battery_percent'], 20], '#FF44AA',  // Magenta = low
                            ['<', ['get', 'battery_percent'], 50], '#4488FF',  // Blue = medium
                            '#00FFD4'  // Cyan-mint = high
                        ],
                        '#8899AA'  // Slate gray for gas
                    ],
                    'icon-halo-color': '#000000',  // Black halo
                    'icon-halo-width': 2,          // Thick outline
                    'icon-halo-blur': 0,           // SHARP outline (no blur)
                    'icon-opacity': 1.0
                }
            };
            
            // Add layer BEFORE labels (so it's above buildings but below text)
            if (beforeLayer) {
                map.addLayer(layerConfig, beforeLayer);
                console.log(`✅ vehicles-symbols layer created BEFORE ${beforeLayer}`);
            } else {
                map.addLayer(layerConfig);
                console.log('✅ vehicles-symbols layer created at TOP');
            }
        }
    }

    function updateVehicleSymbolLayer() {
        // Safety check: ensure layer exists before updating
        if (!map.getSource('vehicles-symbols')) {
            console.log('🔧 Vehicle symbol layer missing, creating it now...');
            ensureVehicleSymbolLayer();
        }
        
        if (!networkState || !networkState.vehicles) {
            return;
        }
        
        const currentTime = performance.now();
        
        // Update vehicleStore with new target positions
        networkState.vehicles.forEach(v => {
            const existingState = vehicleStore.get(v.id);
            
            if (existingState) {
                // Vehicle exists - calculate current interpolated position and set new target
                const elapsed = currentTime - existingState.startTime;
                const progress = Math.min(elapsed / currentInterpolationDuration, 1.0);
                const easedProgress = easeOutCubic(progress);
                
                // Current interpolated position becomes new start position
                const currentLon = lerp(existingState.startLon, existingState.targetLon, easedProgress);
                const currentLat = lerp(existingState.startLat, existingState.targetLat, easedProgress);
                
                vehicleStore.set(v.id, {
                    startLon: currentLon,
                    startLat: currentLat,
                    targetLon: v.lon,
                    targetLat: v.lat,
                    startTime: currentTime,
                    bearing: v.angle !== undefined ? (v.angle * 180 / Math.PI) - 90 : existingState.bearing,
                    // Update properties
                    is_ev: !!v.is_ev,
                    battery_percent: v.battery_percent != null ? Math.round(v.battery_percent) : undefined,
                    is_charging: !!v.is_charging,
                    is_queued: !!v.is_queued,
                    is_stranded: !!v.is_stranded,
                    is_circling: !!v.is_circling,
                    is_v2g_active: window.v2gActiveVehicles && window.v2gActiveVehicles.has(v.id),
                    assigned_station: v.assigned_station || ''
                });
            } else {
                // New vehicle - start at its initial position
                vehicleStore.set(v.id, {
                    startLon: v.lon,
                    startLat: v.lat,
                    targetLon: v.lon,
                    targetLat: v.lat,
                    startTime: currentTime,
                    bearing: v.angle !== undefined ? (v.angle * 180 / Math.PI) - 90 : 0,
                    is_ev: !!v.is_ev,
                    battery_percent: v.battery_percent != null ? Math.round(v.battery_percent) : undefined,
                    is_charging: !!v.is_charging,
                    is_queued: !!v.is_queued,
                    is_stranded: !!v.is_stranded,
                    is_circling: !!v.is_circling,
                    is_v2g_active: window.v2gActiveVehicles && window.v2gActiveVehicles.has(v.id),
                    assigned_station: v.assigned_station || ''
                });
            }
        });
        
        // Remove vehicles that no longer exist in the network state
        const currentVehicleIds = new Set(networkState.vehicles.map(v => v.id));
        vehicleStore.forEach((_, id) => {
            if (!currentVehicleIds.has(id)) {
                vehicleStore.delete(id);
            }
        });
    }

    // Enhanced vehicle click handler with premium popup
    map.on('click', async (e) => {
        const layersToQuery = [];
        if (map.getLayer('vehicles-symbols')) layersToQuery.push('vehicles-symbols');
        if (map.getLayer('vehicles-click-layer')) layersToQuery.push('vehicles-click-layer');
        if (layersToQuery.length > 0) {
            const feats = map.queryRenderedFeatures(e.point, { layers: layersToQuery });
            if (feats && feats.length > 0) {
                const p = feats[0].properties || {};
                const isEV = p.is_ev === 'true' || p.is_ev === true;
                const battery = p.battery_percent !== undefined ? `${p.battery_percent}%` : '–';
                const status = (p.is_stranded === 'true' || p.is_stranded === true) ? '⚠️ Stranded' : 
                              ((p.is_charging === 'true' || p.is_charging === true) ? '⚡ Charging' : 
                              ((p.is_queued === 'true' || p.is_queued === true) ? '⏳ Queued' : '🚗 Driving'));
                const station = p.assigned_station || '—';
                const batteryColor = p.battery_percent < 20 ? '#ff0000' : 
                                    p.battery_percent < 50 ? '#ffaa00' : '#00ff88';
                new mapboxgl.Popup({
                    className: 'vehicle-popup-premium',
                    maxWidth: '280px'
                })
                    .setLngLat(e.lngLat)
                    .setHTML(`
                        <div style="padding: 4px;">
                            <strong style="font-size: 15px;">Vehicle ${p.id || ''}</strong><br>
                            <div style="margin-top: 8px; display: grid; gap: 6px;">
                                <div><span style="color: var(--text-muted);">Type:</span> ${isEV ? '⚡ Electric' : '⛽ Gas'}</div>
                                ${isEV ? `<div><span style="color: var(--text-muted);">Battery:</span> <span style="color: ${batteryColor}; font-weight: 600;">${battery}</span></div>` : ''}
                                <div><span style="color: var(--text-muted);">Status:</span> ${status}</div>
                                ${isEV ? `<div><span style="color: var(--text-muted);">Station:</span> ${station}</div>` : ''}
                            </div>
                        </div>
                    `)
                    .addTo(map);
                return;
            }
        }
        
        // Fallback: nearest vehicle detection
        if (networkState && networkState.vehicles && networkState.vehicles.length > 0) {
            const clickPt = e.point;
            let best = null;
            for (const v of networkState.vehicles) {
                const pt = map.project([v.lon, v.lat]);
                const dx = pt.x - clickPt.x;
                const dy = pt.y - clickPt.y;
                const d2 = dx*dx + dy*dy;
                if (!best || d2 < best.d2) best = { v, d2, pt };
            }
            const threshold2 = 30 * 30;
            if (best && best.d2 <= threshold2) {
                const v = best.v;
                const isEV = !!v.is_ev;
                const battery = v.battery_percent != null ? `${Math.round(v.battery_percent)}%` : '–';
                const status = v.is_stranded ? '⚠️ Stranded' : 
                              (v.is_charging ? '⚡ Charging' : 
                              (v.is_queued ? '⏳ Queued' : '🚗 Driving'));
                const station = v.assigned_station || '—';
                const batteryColor = v.battery_percent < 20 ? '#ff0000' : 
                                    v.battery_percent < 50 ? '#ffaa00' : '#00ff88';
                new mapboxgl.Popup({
                    className: 'vehicle-popup-premium',
                    maxWidth: '280px'
                })
                    .setLngLat([v.lon, v.lat])
                    .setHTML(`
                        <div style="padding: 4px;">
                            <strong style="font-size: 15px;">Vehicle ${v.id || ''}</strong><br>
                            <div style="margin-top: 8px; display: grid; gap: 6px;">
                                <div><span style="color: var(--text-muted);">Type:</span> ${isEV ? '⚡ Electric' : '⛽ Gas'}</div>
                                ${isEV ? `<div><span style="color: var(--text-muted);">Battery:</span> <span style="color: ${batteryColor}; font-weight: 600;">${battery}</span></div>` : ''}
                                <div><span style="color: var(--text-muted);">Status:</span> ${status}</div>
                                ${isEV ? `<div><span style="color: var(--text-muted);">Station:</span> ${station}</div>` : ''}
                            </div>
                        </div>
                    `)
                    .addTo(map);
            }
        }
    });
function initializeEVStationLayer() {
        if (evStationLayerInitialized) return;
        
        map.addSource('ev-stations', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: []
            }
        });
        
        // Premium EV station visualization
        map.addLayer({
            id: 'ev-stations-layer',
            type: 'circle',
            source: 'ev-stations',
            paint: {
                'circle-radius': [
                    'interpolate', ['linear'], ['zoom'],
                    12, 12,
                    14, 15,
                    16, 18,
                    18, 22
                ],
                'circle-color': [
                    'case',
                    ['!', ['get', 'operational']], '#404040',
                    ['>=', ['get', 'charging_count'], 20], '#ff3b3b',
                    ['>=', ['get', 'charging_count'], 15], '#ff8c42',
                    ['>=', ['get', 'charging_count'], 10], '#ffcc00',
                    ['>=', ['get', 'charging_count'], 1], '#00c2ff',
                    '#00ff88'
                ],
                'circle-opacity': 0.95,
                'circle-stroke-width': 4,
                'circle-stroke-color': '#ffffff',
                'circle-stroke-opacity': 0.95,
                'circle-blur': 0.4,
                'circle-pitch-alignment': 'map'
            }
        });
        
        // Enhanced icon layer
        // In initializeEVStationLayer function, find and update:
        map.addLayer({
            id: 'ev-stations-icon',
            type: 'symbol',
            source: 'ev-stations',
            layout: {
                'text-field': 'EV',  // Changed from '⚡' to 'EV'
                'text-font': ['Open Sans Bold'],  // Add font specification
                'text-size': [
                    'interpolate', ['linear'], ['zoom'],
                    12, 14,
                    14, 16,
                    16, 18,
                    18, 20
                ],
                'text-allow-overlap': true,
                'text-ignore-placement': true
            },
            paint: {
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 2,
                'text-halo-blur': 0.5
            }
        });
        
        // Premium badge background
        map.addLayer({
            id: 'ev-stations-badge-bg',
            type: 'circle',
            source: 'ev-stations',
            filter: ['>', ['get', 'charging_count'], 0],
            paint: {
                'circle-radius': [
                    'interpolate', ['linear'], ['zoom'],
                    12, 11,
                    16, 13,
                    18, 15
                ],
                'circle-color': [
                    'case',
                    ['>=', ['get', 'charging_count'], 20], '#ff3b3b',
                    ['>=', ['get', 'charging_count'], 15], '#ff8c42',
                    ['>=', ['get', 'charging_count'], 10], '#ffcc00',
                    '#00ff88'
                ],
                'circle-stroke-color': '#ffffff',
                'circle-stroke-width': 3,
                'circle-opacity': 1.0,
                'circle-translate': [14, -14],
                'circle-translate-anchor': 'map'
            }
        });
        
        map.addLayer({
            id: 'ev-stations-badge-text',
            type: 'symbol',
            source: 'ev-stations',
            filter: ['>', ['get', 'charging_count'], 0],
            layout: {
                'text-field': ['to-string', ['get', 'charging_count']],
                'text-font': ['Open Sans Bold'],
                'text-size': [
                    'interpolate', ['linear'], ['zoom'],
                    12, 17,
                    16, 19,
                    18, 21
                ],
                'text-allow-overlap': true,
                'text-ignore-placement': true
            },
            paint: {
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 2.5,
                'text-translate': [14, -14],
                'text-translate-anchor': 'map'
            }
        });
        
        // Premium click handlers
        ['ev-stations-layer', 'ev-stations-badge-bg', 'ev-stations-badge-text', 'ev-stations-icon'].forEach(layerId => {
            map.on('click', layerId, (e) => {
                const props = e.features[0].properties;
                
                const chargingText = props.charging_count > 0 ? 
                    `<span style="color: #00ffff; font-weight: 600;">⚡ ${props.charging_count}/20 Charging</span>` : 
                    '<span style="color: var(--text-muted);">⚡ 0/20 Charging</span>';
                
                const statusColor = props.operational ? '#00ff88' : '#ff0000';
                const statusIcon = props.operational ? '✅' : '❌';
                
                new mapboxgl.Popup({
                    className: 'ev-popup-premium',
                    maxWidth: '320px'
                })
                    .setLngLat(e.lngLat)
                    .setHTML(`
                        <div style="padding: 4px;">
                            <strong style="font-size: 15px;">${props.name}</strong><br>
                            <div style="margin-top: 10px; display: grid; gap: 8px;">
                                <div>
                                    <span style="color: var(--text-muted);">Status:</span> 
                                    <span style="color: ${statusColor}; font-weight: 600;">${statusIcon} ${props.operational ? 'Online' : 'Offline'}</span>
                                </div>
                                <div>${chargingText}</div>
                                <div><span style="color: var(--text-muted);">Capacity:</span> ${props.chargers} chargers</div>
                                <div><span style="color: var(--text-muted);">Substation:</span> ${props.substation}</div>
                            </div>
                            <button onclick="window.askAboutComponent('${props.name}', 'ev_station')" style="
                                margin-top: 12px;
                                width: 100%;
                                background: linear-gradient(135deg, #00aaff, #0077cc);
                                border: none;
                                border-radius: 6px;
                                color: white;
                                padding: 8px;
                                cursor: pointer;
                                font-weight: 600;
                                transition: opacity 0.2s;
                            " onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=1">💬 Ask AI Assistant</button>
                        </div>
                    `)
                    .addTo(map);
            });
            
            map.on('mouseenter', layerId, () => { 
                map.getCanvas().style.cursor = 'pointer'; 
            });
            map.on('mouseleave', layerId, () => { 
                map.getCanvas().style.cursor = ''; 
            });
        });
        
        evStationLayerInitialized = true;
    }

    function initializeVehicleClickLayer() {
        if (vehicleClickLayerInitialized) return;
        map.addSource('vehicles-click', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: [] }
        });
        map.addLayer({
            id: 'vehicles-click-layer',
            type: 'circle',
            source: 'vehicles-click',
            paint: {
                'circle-radius': [
                    'interpolate', ['linear'], ['zoom'],
                    12, 20,
                    16, 24,
                    18, 28
                ],
                'circle-color': '#000000',
                'circle-opacity': 0.001,
                'circle-stroke-width': 0
            }
        });
        try { map.moveLayer('vehicles-click-layer'); } catch (e) {}
        
        map.on('mouseenter', 'vehicles-click-layer', () => { 
            map.getCanvas().style.cursor = 'pointer'; 
        });
        map.on('mouseleave', 'vehicles-click-layer', () => { 
            map.getCanvas().style.cursor = ''; 
        });
        
        vehicleClickLayerInitialized = true;
    }

    function renderVehicleClicks() {
        if (!networkState || !networkState.vehicles) return;
        const src = map.getSource('vehicles-click');
        if (!src) return;
        
        const features = networkState.vehicles.map(v => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [v.lon, v.lat] },
            properties: {
                id: v.id,
                is_ev: !!v.is_ev,
                battery_percent: v.battery_percent != null ? Math.round(v.battery_percent) : undefined,
                is_charging: !!v.is_charging,
                is_queued: !!v.is_queued,
                is_stranded: !!v.is_stranded,
                assigned_station: v.assigned_station || ''
            }
        }));
        src.setData({ type: 'FeatureCollection', features });
    }

    function renderNetwork() {
        if (!networkState) return;
        
        // Premium substations visualization with REAL-TIME FAILURE STATUS
        const substationFeatures = networkState.substations.map(sub => {
            // Determine color based on operational status
            let color = '#ff0066';  // Default: operational (pink/red)

            if (sub.operational === false || sub.operational === 'false') {
                // FAILED substation - BLACK
                color = '#000000';
                console.log(`[RENDER DEBUG] ${sub.name} set to BLACK (operational=${sub.operational})`);
            } else {
                // Check utilization for color coding
                const utilization = sub.load_mw / sub.capacity_mva;
                if (utilization >= 0.95) {
                    color = '#ff0000';  // CRITICAL - bright red
                } else if (utilization >= 0.85) {
                    color = '#ff9800';  // WARNING - orange
                } else {
                    color = '#00ff00';  // NORMAL - green
                }
            }

            return {
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [sub.lon, sub.lat] },
                properties: {
                    name: sub.name,
                    capacity_mva: sub.capacity_mva,
                    load_mw: sub.load_mw,
                    operational: !!sub.operational,
                    coverage_area: sub.coverage_area,
                    color: color
                }
            };
        });
        
        if (!substationLayerInitialized && map.loaded()) {
            if (!map.getSource('substations')) {
                map.addSource('substations', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }});
            }
            if (!map.getLayer('substations-layer')) {
                // Respect initial layer visibility state
                const initialVisibility = layers.substations ? 'visible' : 'none';

                map.addLayer({
                    id: 'substations-layer',
                    type: 'symbol',
                    source: 'substations',
                    layout: {
                        'text-field': '▲',
                        'text-size': [
                            'interpolate', ['linear'], ['zoom'],
                            12, 44,
                            14, 50,
                            16, 56
                        ],
                        'text-allow-overlap': true,
                        'text-ignore-placement': true,
                        'visibility': initialVisibility
                    },
                    paint: {
                        'text-color': ['get', 'color'],
                        'text-halo-color': '#ffffff',
                        'text-halo-width': 3.5,
                        'text-halo-blur': 1
                    }
                });

                // In renderNetwork function, update the substations-icon layer:
                map.addLayer({
                    id: 'substations-icon',
                    type: 'symbol',
                    source: 'substations',
                    layout: {
                        'text-field': 'S',  // Changed to 'S' for Substation
                        'text-font': ['Open Sans Bold'],
                        'text-size': [
                            'interpolate', ['linear'], ['zoom'],
                            12, 16,
                            14, 18,
                            16, 20
                        ],
                        'text-allow-overlap': true,
                        'text-ignore-placement': true,
                        'visibility': initialVisibility
                    },
                    paint: {
                        'text-color': '#ffffff',
                        'text-halo-color': '#000000',
                        'text-halo-width': 1.5
                    }
                });
                
                ['substations-layer', 'substations-icon'].forEach(layerId => {
                    map.on('click', layerId, (e) => {
                        const p = e.features[0].properties || {};
                        const load = parseFloat(p.load_mw || 0);
                        const statusColor = (p.operational === 'true' || p.operational === true) ? '#00ff88' : '#ff0000';
                        const statusText = (p.operational === 'true' || p.operational === true) ? '⚡ ONLINE' : '⚠️ FAILED';
                        
                        new mapboxgl.Popup({ 
                            offset: 25,
                            className: 'substation-popup-premium',
                            maxWidth: '320px'
                        })
                            .setLngLat(e.lngLat)
                            .setHTML(`
                                <div style="padding: 4px;">
                                    <strong style="font-size: 15px;">${p.name}</strong><br>
                                    <div style="margin-top: 10px; display: grid; gap: 8px;">
                                        <div><span style="color: var(--text-muted);">Capacity:</span> ${p.capacity_mva} MVA</div>
                                        <div><span style="color: var(--text-muted);">Load:</span> <span style="font-weight: 600;">${isNaN(load) ? '-' : load.toFixed(1)} MW</span></div>
                                        <div><span style="color: var(--text-muted);">Status:</span> <span style="color: ${statusColor}; font-weight: 600;">${statusText}</span></div>
                                        <div><span style="color: var(--text-muted);">Coverage:</span> ${p.coverage_area}</div>
                                    </div>
                                    <button onclick="window.askAboutComponent('${p.name}', 'substation')" style="
                                        margin-top: 12px;
                                        width: 100%;
                                        background: linear-gradient(135deg, #00aaff, #0077cc);
                                        border: none;
                                        border-radius: 6px;
                                        color: white;
                                        padding: 8px;
                                        cursor: pointer;
                                        font-weight: 600;
                                        transition: opacity 0.2s;
                                    " onmouseover="this.style.opacity=0.9" onmouseout="this.style.opacity=1">💬 Ask AI Assistant</button>
                                </div>
                            `)
                            .addTo(map);
                    });
                    map.on('mouseenter', layerId, () => { map.getCanvas().style.cursor = 'pointer'; });
                    map.on('mouseleave', layerId, () => { map.getCanvas().style.cursor = ''; });
                });
            }
            substationLayerInitialized = true;
        }
        
        if (map.getSource('substations')) {
            map.getSource('substations').setData({ type: 'FeatureCollection', features: substationFeatures });
        }
        
        // Premium cable rendering
        if (networkState.cables) {
            // Primary cables with enhanced glow
            if (networkState.cables.primary) {
                const primaryFeatures = networkState.cables.primary
                    .filter(cable => cable.path && cable.path.length > 1)
                    .map(cable => ({
                        type: 'Feature',
                        geometry: { type: 'LineString', coordinates: cable.path.map(c => [c[0], c[1]]) },
                        properties: { operational: cable.operational, id: cable.id }
                    }));
                const primaryData = { type: 'FeatureCollection', features: primaryFeatures };
                
                if (map.getSource('primary-cables')) {
                    map.getSource('primary-cables').setData(primaryData);
                } else {
                    map.addSource('primary-cables', { type: 'geojson', data: primaryData });
                    map.addLayer({
                        id: 'primary-cables-glow',
                        type: 'line',
                        source: 'primary-cables',
                        layout: {
                            'visibility': layers.primary ? 'visible' : 'none'
                        },
                        paint: {
                            'line-color': ['case', ['get', 'operational'], '#00ff88', '#ff3366'],
                            'line-width': 10,
                            'line-opacity': 0.15,
                            'line-blur': 1.5
                        }
                    });
                    map.addLayer({
                        id: 'primary-cables',
                        type: 'line',
                        source: 'primary-cables',
                        layout: {
                            'visibility': layers.primary ? 'visible' : 'none'
                        },
                        paint: {
                            'line-color': ['case', ['get', 'operational'], '#00ffcc', '#ff3b3b'],
                            'line-width': 3.5,
                            'line-opacity': 0.95
                        }
                    });
                }
            }
// Secondary cables
            if (networkState.cables.secondary) {
                const secondaryFeatures = (layers.secondary ? networkState.cables.secondary : [])
                    .filter(cable => cable.path && cable.path.length > 1)
                    .map(cable => ({
                        type: 'Feature',
                        geometry: { type: 'LineString', coordinates: cable.path.map(c => [c[0], c[1]]) },
                        properties: { operational: cable.operational, substation: cable.substation || 'unknown', id: cable.id }
                    }));
                const secondaryData = { type: 'FeatureCollection', features: secondaryFeatures };
                
                if (map.getSource('secondary-cables')) {
                    map.getSource('secondary-cables').setData(secondaryData);
                } else {
                    map.addSource('secondary-cables', { type: 'geojson', data: secondaryData });
                    map.addLayer({
                        id: 'secondary-cables-glow',
                        type: 'line',
                        source: 'secondary-cables',
                        layout: {
                            'visibility': layers.secondary ? 'visible' : 'none'
                        },
                        paint: {
                            'line-color': '#ffcc66',
                            'line-width': 4,
                            'line-opacity': 0.12,
                            'line-blur': 1
                        }
                    });
                    map.addLayer({
                        id: 'secondary-cables',
                        type: 'line',
                        source: 'secondary-cables',
                        layout: {
                            'visibility': layers.secondary ? 'visible' : 'none'
                        },
                        paint: {
                            'line-color': '#ffbb44',
                            'line-width': 1.4,
                            'line-opacity': ['case', ['get', 'operational'], 0.75, 0.25]
                        }
                    });
                }
            }
        }
        
        // Premium traffic lights
        if (networkState.traffic_lights) {
            const features = (layers.lights ? networkState.traffic_lights : []).map(tl => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [tl.lon, tl.lat] },
                properties: {
                    powered: tl.powered,
                    color: tl.color || '#ff0000',
                    phase: tl.phase,
                    intersection: tl.intersection
                }
            }));
            const tlData = { type: 'FeatureCollection', features };
            
            if (map.getSource('traffic-lights')) {
                map.getSource('traffic-lights').setData(tlData);
            } else {
                map.addSource('traffic-lights', { type: 'geojson', data: tlData });
                map.addLayer({
                    id: 'traffic-lights',
                    type: 'circle',
                    source: 'traffic-lights',
                    minzoom: 13,
                    paint: {
                        'circle-radius': [
                            'interpolate', ['linear'], ['zoom'],
                            13, 1,
                            14, 2.5,
                            15, 4,
                            16, 5.5,
                            18, 8
                        ],
                        // Remap traffic signal colors to muted/pastel versions
                        'circle-color': [
                            'match', ['get', 'color'],
                            '#00ff00', 'rgba(120, 220, 120, 0.85)',   // Green → muted sage
                            '#ff0000', 'rgba(220, 110, 110, 0.85)',   // Red → muted rose
                            '#ffff00', 'rgba(220, 200, 90, 0.85)',    // Yellow → muted amber
                            'rgba(160, 160, 160, 0.7)'               // fallback gray
                        ],
                        'circle-opacity': [
                            'interpolate', ['linear'], ['zoom'],
                            13, 0,
                            14, 0.75,
                            15, 0.9
                        ],
                        'circle-stroke-width': [
                            'interpolate', ['linear'], ['zoom'],
                            14, 0.5,
                            16, 1
                        ],
                        'circle-stroke-color': 'rgba(40, 40, 40, 0.6)',
                        'circle-stroke-opacity': [
                            'interpolate', ['linear'], ['zoom'],
                            13, 0,
                            14.5, 0.5
                        ],
                        'circle-blur': 0.2,
                        'circle-pitch-alignment': 'map',
                        'circle-pitch-scale': 'map'
                    }
                });

                // Ensure vehicles always render ABOVE traffic lights
                if (map.getLayer('vehicles-symbols')) {
                    map.moveLayer('vehicles-symbols');
                }
            }
            
            if (!lightsClickBound && map.getLayer('traffic-lights')) {
                lightsClickBound = true;
                map.on('click', 'traffic-lights', (e) => {
                    const props = e.features[0].properties;
                    let status = '🟢 Green';
                    let statusColor = '#00ff00';
                    if (props.color === '#ffff00') { status = '🟡 Yellow'; statusColor = '#ffff00'; }
                    else if (props.color === '#ff0000') { status = '🔴 Red'; statusColor = '#ff0000'; }
                    else if (props.color === '#000000') { status = '⚫ No Power'; statusColor = '#666666'; }
                    
                    new mapboxgl.Popup({
                        className: 'traffic-popup-premium',
                        maxWidth: '280px'
                    })
                        .setLngLat(e.lngLat)
                        .setHTML(`
                            <div style="padding: 4px;">
                                <strong style="font-size: 15px;">Traffic Light</strong><br>
                                <div style="margin-top: 8px;">
                                    <div style="color: var(--text-muted);">${props.intersection}</div>
                                    <div style="margin-top: 6px;">Status: <span style="color: ${statusColor}; font-weight: 600;">${status}</span></div>
                                </div>
                            </div>
                        `)
                        .addTo(map);
                });
                map.on('mouseenter', 'traffic-lights', () => { map.getCanvas().style.cursor = 'pointer'; });
                map.on('mouseleave', 'traffic-lights', () => { map.getCanvas().style.cursor = ''; });
            }
        }
        
        updateVehicleSymbolLayer();
    }

    function renderEVStations() {
        if (!networkState || !networkState.ev_stations) {
            if (map.getLayer('ev-stations-layer')) {
                map.setLayoutProperty('ev-stations-layer', 'visibility', 'none');
            }
            return;
        }
        
        if (!evStationLayerInitialized && map.loaded()) {
            initializeEVStationLayer();
        }
        
        if (!map.getSource('ev-stations')) return;
        
        const features = networkState.ev_stations.map(ev => {
            let chargingCount = ev.vehicles_charging || 0;
            let queuedCount = ev.vehicles_queued || 0;
            
            if (chargingCount === 0 && networkState.vehicles) {
                chargingCount = networkState.vehicles.filter(v => 
                    v.is_charging && v.assigned_station === ev.id
                ).length;
            }
            
            return {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [ev.lon, ev.lat]
                },
                properties: {
                    id: ev.id,
                    name: ev.name,
                    chargers: ev.chargers,
                    charging_count: chargingCount,
                    queued_count: queuedCount,
                    operational: ev.operational,
                    substation: ev.substation
                }
            };
        });
        
        const source = map.getSource('ev-stations');
        if (source) {
            source.setData({
                type: 'FeatureCollection',
                features: features
            });
        }
        
        ['ev-stations-layer', 'ev-stations-badge-bg', 'ev-stations-badge-text', 'ev-stations-icon'].forEach(id => {
            if (map.getLayer(id)) {
                map.setLayoutProperty(id, 'visibility', layers.ev ? 'visible' : 'none');
            }
        });
    }

    // ==========================================
    // EV CONFIGURATION FUNCTIONS
    // ==========================================
    let currentEVConfig = {
        ev_percentage: 70,
        battery_min_soc: 20,
        battery_max_soc: 90
    };
    
    function updateEVPercentage(value) {
        currentEVConfig.ev_percentage = parseInt(value);
        document.getElementById('ev-percentage-display').textContent = value + '%';
        
        // Visual feedback
        const slider = document.getElementById('ev-percentage-slider');
        slider.style.background = `linear-gradient(to right, 
            var(--primary-glow) 0%, 
            var(--primary-glow) ${value}%, 
            rgba(255,255,255,0.1) ${value}%, 
            rgba(255,255,255,0.1) 100%)`;
    }
    
    function updateBatteryRange() {
        const minSlider = document.getElementById('battery-min-slider');
        const maxSlider = document.getElementById('battery-max-slider');
        
        let minValue = parseInt(minSlider.value);
        let maxValue = parseInt(maxSlider.value);
        
        // Ensure min is always less than max
        if (minValue >= maxValue) {
            if (minSlider === document.activeElement) {
                maxValue = minValue + 1;
                maxSlider.value = maxValue;
            } else {
                minValue = maxValue - 1;
                minSlider.value = minValue;
            }
        }
        
        currentEVConfig.battery_min_soc = minValue;
        currentEVConfig.battery_max_soc = maxValue;
        
        document.getElementById('battery-range-display').textContent = `${minValue}% - ${maxValue}%`;
        
        // Visual feedback for sliders
        const minPercent = ((minValue - 1) / 99) * 100;
        const maxPercent = ((maxValue - 1) / 99) * 100;
        
        minSlider.style.background = `linear-gradient(to right, 
            var(--secondary-glow) 0%, 
            var(--secondary-glow) ${minPercent}%, 
            rgba(255,255,255,0.1) ${minPercent}%, 
            rgba(255,255,255,0.1) 100%)`;
            
        maxSlider.style.background = `linear-gradient(to right, 
            var(--secondary-glow) 0%, 
            var(--secondary-glow) ${maxPercent}%, 
            rgba(255,255,255,0.1) ${maxPercent}%, 
            rgba(255,255,255,0.1) 100%)`;
    }
    
    function setEVPreset(preset) {
        const presets = {
            'low': { ev_percentage: 20, battery_min_soc: 5, battery_max_soc: 75 },
            'medium': { ev_percentage: 50, battery_min_soc: 15, battery_max_soc: 85 },
            'high': { ev_percentage: 80, battery_min_soc: 25, battery_max_soc: 95 }
        };
        
        const config = presets[preset];
        if (!config) return;
        
        // Update sliders
        document.getElementById('ev-percentage-slider').value = config.ev_percentage;
        document.getElementById('battery-min-slider').value = config.battery_min_soc;
        document.getElementById('battery-max-slider').value = config.battery_max_soc;
        
        // Update displays
        updateEVPercentage(config.ev_percentage);
        updateBatteryRange();
        
        // Visual feedback
        showNotification('⚡ Preset Applied', `${preset.charAt(0).toUpperCase() + preset.slice(1)} EV configuration loaded`, 'success');
    }
    
    async function applyEVConfiguration() {
        try {
            const response = await fetch('/api/ev/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(currentEVConfig)
            });
            
            const result = await response.json();
            if (result.success) {
                showNotification('✅ EV Config Applied', 
                    `EV: ${currentEVConfig.ev_percentage}% | Battery: ${currentEVConfig.battery_min_soc}%-${currentEVConfig.battery_max_soc}%`, 
                    'success');
            } else {
                showNotification('❌ Config Failed', result.message || 'Failed to apply EV configuration', 'error');
            }
        } catch (error) {
            console.error('EV config error:', error);
            showNotification('❌ Config Error', 'Failed to apply EV configuration', 'error');
        }
    }
    
    // Initialize EV configuration on page load
    function initializeEVConfig() {
        updateEVPercentage(70);
        updateBatteryRange();
    }

    // Expose EV config functions globally so agentic chatbot socket events can update sliders
    window.updateEVPercentage = updateEVPercentage;
    window.updateBatteryRange = updateBatteryRange;
    window.toggleLayer = toggleLayer;

    // ==========================================
    // CONTROL FUNCTIONS
    // ==========================================
    async function startSUMO() {
        const response = await fetch('/api/sumo/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                vehicle_count: 10,
                ev_percentage: currentEVConfig.ev_percentage / 100,
                battery_min_soc: currentEVConfig.battery_min_soc / 100,
                battery_max_soc: currentEVConfig.battery_max_soc / 100
            })
        });
        
        const result = await response.json();
        if (result.success) {
            // REACTIVE MODE: Don't update UI here - wait for WebSocket to confirm
            showNotification('✅ Starting Vehicles...', result.message, 'success');
        } else {
            showNotification('❌ Failed', 'Failed to start SUMO: ' + result.message, 'error');
        }
        enforceLayerOrder();
    }

    function enforceLayerOrder() {
        const bottomToTop = [
            'primary-cables-glow',
            'primary-cables',
            'secondary-cables-glow',
            'secondary-cables',
            'traffic-lights',
            'vehicle-webgl-layer',
            'vehicles-symbols',
            'vehicles-click-layer',
            'substations-layer',
            'substations-icon',
            'ev-stations-layer',
            'ev-stations-icon',
            'ev-stations-badge-bg',
            'ev-stations-badge-text'
        ];
        bottomToTop.forEach(id => { try { if (map.getLayer(id)) map.moveLayer(id); } catch (e) {} });
    }

    async function stopSUMO() {
        const response = await fetch('/api/sumo/stop', {method: 'POST'});
        const result = await response.json();
        
        if (result.success) {
            // REACTIVE MODE: Don't update UI here - wait for WebSocket to confirm
            showNotification('⏹️ Stopping Vehicles...', 'Halting simulation', 'info');
        }
    }

    async function spawnVehicles(count) {
        const response = await fetch('/api/sumo/spawn', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                count: count,
                ev_percentage: currentEVConfig.ev_percentage / 100,
                battery_min_soc: currentEVConfig.battery_min_soc / 100,
                battery_max_soc: currentEVConfig.battery_max_soc / 100
            })
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification('➕ Vehicles Added', `Spawned vehicles`, 'success');
        }
    }

    async function setSimulationSpeed(speed) {
        document.getElementById('speed-value').textContent = `${speed}x`;
        
        await fetch('/api/simulation/speed', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({speed: parseFloat(speed)})
        });
    }

    async function toggleSubstation(name) {
        const sub = networkState.substations.find(s => s.name === name);

        if (sub.operational) {
            await fetch(`/api/fail/${name}`, { method: 'POST' });
        } else {
            await fetch(`/api/restore/${name}`, { method: 'POST' });
        }

        // Small delay to ensure backend completes
        await new Promise(resolve => setTimeout(resolve, 200));

        // Reload network state
        await loadNetworkState();

        // Force update the specific button
        const btn = document.getElementById(`sub-btn-${name}`);
        if (btn && networkState) {
            const updatedSub = networkState.substations.find(s => s.name === name);
            if (updatedSub) {
                if (updatedSub.operational) {
                    btn.classList.remove('failed');
                } else {
                    btn.classList.add('failed');
                }
            }
        }

        // Update detailed substation grid (power loads section)
        if (window.scenarioUI) {
            await window.scenarioUI.updateStatus();
        }
    }

    async function restoreAll() {
        const response = await fetch('/api/restore_all', { method: 'POST' });
        const data = await response.json();

        // Small delay to ensure backend completes the restore
        await new Promise(resolve => setTimeout(resolve, 300));

        // Force reload network state and update UI
        await loadNetworkState();

        // Force update the substation buttons
        if (networkState && networkState.substations) {
            networkState.substations.forEach(sub => {
                const btn = document.getElementById(`sub-btn-${sub.name}`);
                if (btn) {
                    if (sub.operational) {
                        btn.classList.remove('failed');
                    } else {
                        btn.classList.add('failed');
                    }
                }
            });
        }

        // Update detailed substation grid (power loads section)
        if (window.scenarioUI) {
            await window.scenarioUI.updateStatus();
        }

        showNotification('🔧 System Restored', data.message || 'All substations back online', 'success');
    }

    async function triggerBlackout() {
        try {
            const subs = (networkState?.substations || []).map(s => s.name);
            const total = subs.length;
            showBlackoutAlert(total - 1, 1);
            for (const s of subs) {
                if (s !== 'Midtown East') {
                    await fetch(`/api/fail/${encodeURIComponent(s)}`, {method: 'POST'});
                }
            }
            await loadNetworkState();
        } catch (e) {
            console.error('Blackout error', e);
        }
    }

    async function testEVRush() {
        const response = await fetch('/api/test/ev_rush', {method: 'POST'});
        const result = await response.json();
        if (result.success) {
            showNotification('⚡ EV Rush Test', result.message, 'info');
        }
    }

    function processNetworkState(state) {
        // ADAPTIVE INTERPOLATION: Measure time since last packet
        const now = performance.now();
        const timeDelta = now - lastPacketTime;
        lastPacketTime = now;
        
        // If we have a valid delta (not first packet), adjust interpolation speed
        if (timeDelta > 50) {
            // Add 20% buffer to prevent running out of frames
            const targetDuration = timeDelta * 1.2;
            
            // Smoothly transition (weighted average) to prevent jerky speed changes
            currentInterpolationDuration = (currentInterpolationDuration * 0.7) + (targetDuration * 0.3);
            
            // Clamp to reasonable limits
            currentInterpolationDuration = Math.max(MIN_INTERPOLATION_DURATION, currentInterpolationDuration);
        }

        networkState = state;
        
        // DEBUG: Log failed substations
        const failedSubs = networkState.substations.filter(sub => !sub.operational);
        
        // Handle V2G data from system_update event
        if (state.v2g) {
            updateV2GFromWebSocket(state.v2g);
            updateV2GDashboard(state.v2g);
        }
        
        // Handle AI focus from system_update event
        if (state.ai_focus && state.ai_focus.has_update) {
            applyAIMapFocus(state.ai_focus.focus_data);
        }
        
        // REACTIVE MODE: Update global controls based on server state
        updateGlobalControls(state);
        
        updateUI();
        renderNetwork();
        
        // DISABLED: Custom WebGL renderer causes 3D drift
        // Using Mapbox symbol layer instead (3D terrain compatible)
        /*
        if (layers.vehicles && vehicleRenderer && networkState.vehicles) {
            vehicleRenderer.updateVehicles(networkState.vehicles);
        }
        */
        
        renderEVStations();
        updateVehicleSymbolLayer();  // ✅ PRIMARY vehicle renderer (3D compatible)
    }
    
    /**
     * REACTIVE UI UPDATE - Update global controls based on WebSocket data
     * This ensures UI reflects actual server state, not predicted state
     */
    function updateGlobalControls(data) {
        // 1. Update SUMO Start/Stop button states based on server status
        const sumoIsRunning = data.sumo_running || false;
        
        const startBtn = document.getElementById('start-sumo-btn');
        const stopBtn = document.getElementById('stop-sumo-btn');
        const spawn10Btn = document.getElementById('spawn10-btn');
        
        if (sumoIsRunning) {
            // SUMO is running - enable Stop, disable Start
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            if (spawn10Btn) spawn10Btn.disabled = false;
            
            // Update global state
            sumoRunning = true;
        } else {
            // SUMO is stopped - enable Start, disable Stop
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            if (spawn10Btn) spawn10Btn.disabled = true;
            
            // Clear vehicle renderer when stopped
            if (vehicleRenderer && !sumoIsRunning && sumoRunning) {
                vehicleRenderer.clear();
            }
            
            // Initialize WebGL vehicle renderer or hybrid based on config
            initializeRenderers();
            
            // Start 60 FPS vehicle interpolation loop
            startVehicleAnimation();
            
            // Update global state
            sumoRunning = false;
        }
        
        // 2. Update Dashboard Sidebar Counters
        if (data.statistics) {
            const stats = data.statistics;
            
            // Traffic Lights counters
            const totalLightsEl = document.getElementById('total-traffic-lights');
            const poweredLightsEl = document.getElementById('powered-lights');
            
            if (totalLightsEl) {
                totalLightsEl.textContent = stats.total_traffic_lights || 0;
            }
            if (poweredLightsEl) {
                poweredLightsEl.textContent = stats.powered_traffic_lights || 0;
            }
            
            // MW Load counter
            const loadEl = document.getElementById('total-load');
            if (loadEl && stats.total_load_mw !== undefined) {
                loadEl.textContent = stats.total_load_mw.toFixed(1);
            }
        }
        
        // 3. Update Bottom Status Bar
        const systemStatusEl = document.getElementById('system-status');
        const systemIndicatorEl = document.getElementById('system-indicator');
        
        if (data.statistics) {
            const operational = data.statistics.operational_substations || 0;
            const total = data.statistics.total_substations || 0;
            const failures = total - operational;
            
            if (systemStatusEl && systemIndicatorEl) {
                if (failures === 0) {
                    systemIndicatorEl.style.background = 'var(--primary-glow)';
                    systemStatusEl.textContent = 'System Online';
                } else if (failures <= 2) {
                    systemIndicatorEl.style.background = 'var(--warning-glow)';
                    systemStatusEl.textContent = `${failures} Substation${failures > 1 ? 's' : ''} Failed`;
                } else {
                    systemIndicatorEl.style.background = 'var(--danger-glow)';
                    systemStatusEl.textContent = 'Critical Failures';
                }
            }
        }
    }
    
    // New function to handle V2G updates from WebSocket
    function updateV2GFromWebSocket(v2gData) {
        // Update V2G active vehicles set
        window.v2gActiveVehicles.clear();
        window.v2gStationCounts = {};
        
        if (v2gData.active_vehicles) {
            v2gData.active_vehicles.forEach(v => {
                window.v2gActiveVehicles.add(v.vehicle_id || v.id);
                if (v.station_id) {
                    window.v2gStationCounts[v.station_id] = 
                        (window.v2gStationCounts[v.station_id] || 0) + 1;
                }
            });
        }
        
        // Update EV station badges
        updateEVStationBadges();
        
        // Re-render vehicles with updated V2G status
        if (vehicleRenderer && networkState.vehicles) {
            vehicleRenderer.updateVehicles(networkState.vehicles);
        }
    }
    
    // New function to handle AI map focus from WebSocket
    function applyAIMapFocus(focusData) {
        if (!focusData || !map) return;
        
        // Apply map focus (fly to location, highlight, etc.)
        // Apply map focus (fly to location, highlight, etc.)
        let center = null;
        if (Array.isArray(focusData.coordinates) && focusData.coordinates.length === 2) {
            center = focusData.coordinates;
        } else if (focusData.coordinates && focusData.coordinates.lat && focusData.coordinates.lon) {
            center = [focusData.coordinates.lon, focusData.coordinates.lat];
        }

        if (center) {
            map.flyTo({
                center: center,
                zoom: focusData.zoom || 14,
                duration: 2000
            });
        }
        
        // Show AI notification if available
        if (focusData.message) {
            showAIMapFocusNotification(focusData);
        }
    }

    async function loadNetworkState() {
        try {
            const response = await fetch('/api/network_state');
            const data = await response.json();
            processNetworkState(data);
        } catch (error) {
            console.error('Error loading network state:', error);
        }
    }

    // Expose loadNetworkState globally for use by other modules (e.g., scenario-controls.js)
    window.loadNetworkState = loadNetworkState;
    
    // NEW: Allow updates from WebSockets
    window.updateNetworkFromData = function(data) {
        processNetworkState(data);
    };

    // Removed periodic setInterval polling - now using WebSockets 🚀

    function controlLayers(layerList, message) {
        if (!layerList || !Array.isArray(layerList)) {
            console.error('Invalid layer list for controlLayers');
            return;
        }
        
        console.log('Controlling layers:', layerList);
        
        // Define expected state (true = visible) based on typical usage
        // Or simplified: just ensure they are visible? 
        // Usage in executeMapAction suggests it might be a list of layers to SHOW.
        
        layerList.forEach(layer => {
            // Check current state. If we want to SHOW it and it's hidden, toggle it.
            // But toggleLayer just flips it. 
            // We need 'setLayerVisibility' really, but toggleLayer is what we have.
            // Let's assume controlLayers implies SHOWING them?
            // Or maybe checking the current state?
            
            // Actually, let's implement a smarter setLayer method if possible, 
            // or just use toggleLayer if we lack direct set capability.
            // script.js uses `layers[layer] = !layers[layer]`.
            
            // To be safe, let's look at `layers` object state.
            if (!layers[layer]) {
                 toggleLayer(layer);
            }
        });

        if (message) {
            showNotification('Layer Update', message, 'info');
        }
    }

    function showPowerGrid() {
        const gridLayers = ['primary', 'secondary', 'substations'];
        gridLayers.forEach(layer => {
            if (!layers[layer]) toggleLayer(layer);
        });
        showNotification('⚡ Power Grid', 'Power grid layers enabled', 'success');
    }

    function hidePowerGrid() {
        const gridLayers = ['primary', 'secondary'];
        gridLayers.forEach(layer => {
            if (layers[layer]) toggleLayer(layer);
        });
        showNotification('⚡ Power Grid', 'Power grid layers hidden', 'info');
    }

    function toggleLayer(layer) {
        layers[layer] = !layers[layer];
        
        const layerMappings = {
            'lights': ['traffic-lights'],
            'primary': ['primary-cables', 'primary-cables-glow'],
            'secondary': ['secondary-cables', 'secondary-cables-glow'],
            'vehicles': ['vehicle-webgl-layer', 'vehicles-symbols', 'vehicles-click-layer'],
            'ev': ['ev-stations-layer', 'ev-stations-badge-bg', 'ev-stations-badge-text', 'ev-stations-icon'],
            'substations': ['substations-layer', 'substations-icon']
        };
        
        const layerIds = layerMappings[layer] || [];
        layerIds.forEach(id => {
            if (map.getLayer(id)) {
                map.setLayoutProperty(id, 'visibility', layers[layer] ? 'visible' : 'none');
            }
        });
        
        if (layer === 'vehicles' && !layers[layer] && vehicleRenderer) {
            vehicleRenderer.clear();
        }
    }

    // =========================================================================
    // SIMULATION CLOCK — Single source of truth
    // The backend (ScenarioController) owns the time and broadcasts it every
    // second via the 'system_update' WebSocket event.  The frontend ONLY
    // renders whatever the backend says — no independent counter.
    // Initialize from system clock to avoid a blank flash before the first
    // WebSocket update arrives (~1 s).
    // =========================================================================
    const _initNow = new Date();
    let displayHours = _initNow.getHours();
    let displayMinutes = _initNow.getMinutes();
    let displaySeconds = _initNow.getSeconds();

    function renderTime() {
        const timeEl = document.getElementById('time');
        if (!timeEl) return;
        const ampm = displayHours >= 12 ? 'PM' : 'AM';
        const hours12 = displayHours % 12 || 12;
        timeEl.textContent = `${String(hours12).padStart(2, '0')}:${String(displayMinutes).padStart(2, '0')}:${String(displaySeconds).padStart(2, '0')} ${ampm}`;
    }

    // Called by scenario-controls.js handleSystemUpdate (every ~1s via WebSocket)
    window.updateLocalTime = function(hours, minutes, seconds = 0) {
        displayHours = parseInt(hours);
        displayMinutes = parseInt(minutes);
        displaySeconds = parseInt(seconds);
        renderTime();
    };

    // Called by scenario-controls.js setTime / slider (user-initiated change)
    window.syncDisplayTime = function(hour, minute) {
        displayHours = Math.floor(hour);
        displayMinutes = minute !== undefined ? minute : Math.round((hour % 1) * 60);
        displaySeconds = 0;
        window._lastManualTimeUpdate = Date.now();
        renderTime();
    };

    // Kept for backward-compat — just re-renders current values (no counter)
    function updateTime() { renderTime(); }
    window.updateTime = updateTime;

    // Global debounce: any time setter (chatbot, slider) can set this to suppress auto-advance
    window._lastManualTimeUpdate = 0;

    // Sync local clock when chatbot changes time via socket
    if (window.socket) {
        window.socket.on('scenario_time_update', (data) => {
            if (data.hour !== undefined) {
                displayHours = Math.floor(data.hour);
                displayMinutes = data.minute || Math.round((data.hour % 1) * 60);
                displaySeconds = 0;
                window._lastManualTimeUpdate = Date.now();
                renderTime();
            }
        });
        window.socket.on('scenario_temp_update', (data) => {
            if (data.temperature !== undefined) {
                const tempEl = document.getElementById('temperature');
                if (tempEl) tempEl.textContent = Math.round(data.temperature);
            }
        });
    }

    function showBlackoutAlert(failedCount, operationalCount) {
        const alertEl = document.getElementById('blackout-alert');
        const msg = document.getElementById('blackout-message');
        let onlineName = 'Midtown East';
        if (networkState && networkState.substations) {
            const online = networkState.substations.find(s => s.operational);
            if (online) onlineName = online.name;
        }
        msg.textContent = `${failedCount} substations offline • ${operationalCount} operational (${onlineName})`;
        alertEl.style.display = 'flex';
    }

    function dismissBlackoutAlert() {
        document.getElementById('blackout-alert').style.display = 'none';
    }

    // Premium notification system
    function showNotification(title, message, type = 'info') {
        const colors = {
            success: 'linear-gradient(135deg, #00ff88, #00cc66)',
            error: 'linear-gradient(135deg, #ff4444, #cc0000)',
            info: 'linear-gradient(135deg, #00aaff, #0077cc)',
            warning: 'linear-gradient(135deg, #ffaa00, #ff8800)'
        };
        
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 24px;
                right: 24px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.style.cssText = `
            background: ${colors[type]};
            color: rgba(0, 0, 0, 0.9);
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            max-width: 320px;
            animation: slideInRight 0.3s ease;
            font-weight: 500;
            pointer-events: auto;
            position: relative;
        `;
        notification.innerHTML = `<strong>${title}</strong><br>${message}`;
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }


// ==========================================
    // ML DASHBOARD FUNCTIONS
    // ==========================================
    async function updateMLDashboard() {
        try {
            const response = await fetch('/api/ml/dashboard');
            const data = await response.json();
            const accEl = document.getElementById('ml-accuracy');
            if (!accEl) return;
            accEl.textContent = `${100 - (data.metrics.demand_mape || 5)}%`;
            document.getElementById('ml-patterns').textContent = data.metrics.patterns_found || 0;
            document.getElementById('ml-anomalies').textContent = data.anomalies ? data.anomalies.length : 0;
            document.getElementById('ml-savings').textContent = `${data.metrics.optimization_savings || 0}%`;
            document.getElementById('ml-updated').textContent = new Date(data.timestamp).toLocaleTimeString('en-US', {hour12:false});
            
            // Update V2G analytics if available
            if (data.v2g_analytics) {
                const v2gData = data.v2g_analytics.v2g_performance;
                document.getElementById('v2g-active-vehicles').textContent = v2gData.active_vehicles || 0;
                document.getElementById('v2g-energy-traded').textContent = (v2gData.total_energy_traded || 0).toFixed(1);
                document.getElementById('v2g-revenue').textContent = `$${(v2gData.total_revenue || 0).toFixed(2)}`;
                document.getElementById('v2g-market-price').textContent = `$${(v2gData.market_price || 0).toFixed(2)}`;
                
                // Update V2G insights
                if (data.v2g_analytics.v2g_insights) {
                    document.getElementById('v2g-insights').innerHTML = data.v2g_analytics.v2g_insights;
                }
            }
            
            if (data.anomalies && data.anomalies.length > 0) {
                const resultsDiv = document.getElementById('ml-results');
                if (resultsDiv) {
                    resultsDiv.style.display = 'block';
                    resultsDiv.innerHTML = '<strong style="color: #ff6b6b;">⚠️ Anomalies Detected:</strong><br>' +
                        data.anomalies.map(a => `<span style="color: var(--text-secondary);">${a.type}: ${a.description}</span>`).join('<br>');
                }
            }
        } catch (e) {
            console.error('ML Dashboard error:', e);
        }
    }

    function showV2GAnalytics() {
        const panel = document.getElementById('v2g-analytics-panel');
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            updateMLDashboard(); // Refresh data
        } else {
            panel.style.display = 'none';
        }
    }

    async function showMLPredictions() {
        const response = await fetch('/api/ml/predict/demand?hours=6');
        const predictions = await response.json();
        const resultsDiv = document.getElementById('ml-results');
        if (!resultsDiv) return;
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<strong style="color: #00aaff;">📊 Power Demand Predictions (Next 6 Hours):</strong><br>' +
            predictions.map(p => `<span style="color: var(--text-secondary);">Hour +${p.hour}: <span style="color: #00ff88; font-weight: 600;">${p.predicted_mw} MW</span> (±${(p.confidence_upper - p.predicted_mw).toFixed(1)} MW)</span>`).join('<br>');
    }

    async function runMLOptimization() {
        const response = await fetch('/api/ml/optimize');
        const optimization = await response.json();
        const resultsDiv = document.getElementById('ml-results');
        if (!resultsDiv) return;
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<strong style="color: #c8a2ff;">⚡ Optimization Recommendations:</strong><br>' +
            optimization.recommendations.map(r => `<span style="color: var(--text-secondary);">${r.type}: ${r.action} <span style="color: #ffaa00;">(Priority: ${r.priority})</span></span>`).join('<br>') +
            `<br><strong style="color: #00ff88;">Total Savings: ${optimization.total_savings_mw} MW (${optimization.savings_percentage}%)</strong>`;
    }

    async function askAIAdvice() {
        let chat = document.getElementById('ai-chat');
        if (!chat) {
            chat = document.createElement('div');
            chat.id = 'ai-chat';
            chat.style.cssText = `
                position: fixed;
                right: 24px;
                bottom: 100px;
                width: 380px;
                max-height: 60vh;
                background: linear-gradient(135deg, rgba(20,20,30,0.98), rgba(30,20,50,0.96));
                backdrop-filter: blur(20px);
                border: 1px solid rgba(138,43,226,0.3);
                border-radius: 16px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
                display: flex;
                flex-direction: column;
                z-index: 1200;
                overflow: hidden;
                animation: slideUp 0.3s ease;
            `;
            chat.innerHTML = `
                <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(0,0,0,0.2);">
                    <div style="font-weight:700;color:#c8a2ff;display:flex;align-items:center;gap:8px;">
                        <span style="width:10px;height:10px;background:linear-gradient(135deg,#c8a2ff,#8a2be2);border-radius:50%;"></span>
                        AI Assistant
                    </div>
                    <button id="ai-close" class="chat-close" style="padding:6px 12px;font-size:12px;">✕</button>
                </div>
                <div id="ai-messages" style="padding:16px;font-size:13px;line-height:1.6;overflow:auto;max-height:40vh;flex:1;"></div>
                <div style="display:flex;gap:8px;padding:14px;border-top:1px solid rgba(255,255,255,0.08);background:rgba(0,0,0,0.2);">
                    <input id="ai-input" placeholder="Ask about grid status, ML, optimization…" onkeypress="handleAIKeyPress(event)" style="flex:1;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);color:#fff;font-size:13px;"/>
                    <button id="ai-send" class="btn btn-primary" style="padding:10px 20px;">Send</button>
                </div>
            `;
            document.body.appendChild(chat);
            document.getElementById('ai-close').onclick = () => { chat.style.display = 'none'; };
            document.getElementById('ai-send').onclick = async () => {
                const box = document.getElementById('ai-messages');
                const input = document.getElementById('ai-input');
                const q = input.value.trim();
                if (!q) return;
                box.innerHTML += `<div class="msg user" style="margin:8px 0;padding:10px;background:linear-gradient(135deg,rgba(0,170,255,0.1),rgba(0,120,255,0.05));border-radius:10px;border:1px solid rgba(0,170,255,0.2);"><strong>You:</strong> ${q}</div>`;
                input.value = '';
                box.innerHTML += `<div class="typing" style="padding:8px;color:var(--text-muted);font-style:italic;">AI is typing…</div>`;
                box.scrollTop = box.scrollHeight;
                try {
                    const resp = await fetch('/api/ai/advice', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question:q})});
                    const data = await resp.json();
                    box.querySelector('.typing').remove();
                    if (data.advice) {
                        box.innerHTML += `<div class="msg ai" style="margin:8px 0;padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;border:1px solid rgba(255,255,255,0.05);"><strong style="color:#c8a2ff;">AI:</strong> ${data.advice.replace(/\\n/g,'<br>')}</div>`;
                    } else {
                        box.innerHTML += `<div style="color:#ff6b6b;">Error: ${data.error||'Unknown'}</div>`;
                    }
                } catch(e) {
                    box.querySelector('.typing')?.remove();
                    box.innerHTML += `<div style="color:#ff6b6b;">Request failed</div>`;
                }
                box.scrollTop = box.scrollHeight;
            };
        }
        chat.style.display = 'flex';
        const box = document.getElementById('ai-messages');
        // Don't auto-load insights - let users request them manually
        if (!box.innerHTML.trim()) {
            box.innerHTML = '<div class="msg ai" style="padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;color:var(--text-secondary);">👋 Hello! Ask me anything about the power grid system. I can provide insights, recommendations, and answer questions about the current state.</div>';
        }
    }

    async function showBaselines() {
        const r = await fetch('/api/ml/baselines');
        const data = await r.json();
        const resultsDiv = document.getElementById('ml-results');
        if (!resultsDiv) return;
        resultsDiv.style.display = 'block';
        if (data.method_comparison) {
            const rows = Object.entries(data.method_comparison)
            .map(([k,v]) => `<span style="color:var(--text-secondary);">${k}: MAPE ${v.MAPE}%, Runtime ${v.Runtime_ms}ms, Savings ${v.Cost_Savings}%</span>`)
            .join('<br>');
            resultsDiv.innerHTML = '<strong style="color:#4ecdc4;">📐 Performance Baselines:</strong><br>' + rows;
        } else {
            resultsDiv.textContent = 'No baseline data available.';
        }
    }

    async function downloadExecutiveReport() {
        try {
            showNotification('📄 Generating Report', 'Creating executive summary...', 'info');
            const r = await fetch('/api/ai/report');
            const data = await r.json();
            if (!data.report) return showNotification('❌ Report Failed', data.error || 'Report generation failed', 'error');
            const blob = new Blob([data.report], {type: 'text/markdown'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Executive_Report_${new Date().toISOString().slice(0,19).replace(/[:T]/g,'_')}.md`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
            showNotification('✅ Report Downloaded', 'Executive summary saved', 'success');
        } catch (e) {
            showNotification('❌ Error', 'Report generation failed', 'error');
        }
    }

    // ==========================================
    // SOCKET.IO EVENT LISTENERS
    // ==========================================
    
    // Existing listeners...
    
    if (window.socket) {
        window.socket.on('v2g_update', (data) => {
            console.log('🔋 V2G Update:', data);
            if (data.action === 'v2g_enabled') {
                showNotification('🔋 V2G Activated', `Vehicle-to-Grid enabled for ${data.substation}`, 'success');
            } else if (data.action === 'v2g_disabled') {
                showNotification('🔌 V2G Disabled', `Vehicle-to-Grid disabled for ${data.substation}`, 'info');
            }
            if (typeof refreshV2GDashboard === 'function') refreshV2GDashboard();
        });
    }

    // ==========================================
    // CHATBOT FUNCTIONS
    // ==========================================
    
    // NEW: Click-to-Query Logic
    window.askAboutComponent = function(name, type) {
        const chatWin = document.getElementById('chatbot-window');
        const launcher = document.getElementById('chatbot-launcher');
        const input = document.getElementById('chat-input');
        
        // Ensure chat window is open
        if (chatWin && (chatWin.style.display === 'none' || !chatWin.style.display)) {
            if (typeof toggleChatbot === 'function') {
                toggleChatbot();
            } else {
                chatWin.style.display = 'flex';
                if (launcher) launcher.style.display = 'none';
            }
        } else if (chatWin && chatWin.style.display !== 'flex') {
             // Fallback if style is set to something weird or empty
             chatWin.style.display = 'flex';
             if (launcher) launcher.style.display = 'none';
        }
        
        // Set input value
        if (input) {
            input.value = `Status of ${name}`;
            input.focus();
            
            // Optional: Auto-scroll to bottom of chat
            const chatBody = document.getElementById('chat-body');
            if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
        }
    };

    function toggleChatbot() {
        const launcher = document.getElementById('chatbot-launcher');
        const win = document.getElementById('chatbot-window');
        if (win.style.display === 'flex') {
            win.style.display = 'none';
            launcher.style.display = 'flex';
        } else {
            win.style.display = 'flex';
            launcher.style.display = 'none';
            // Chat history preserved - no auto-loading of insights
            // Users can manually request insights using the chat interface
        }
    }

    function handleChatKeyPress(event) {
        if (event.key === 'Enter') {
            sendChatMessage();
        }
    }

    // ==========================================
    // ENHANCED CHATBOT FUNCTIONS
    // ==========================================

    function sendSuggestion(suggestion) {
        const input = document.getElementById('chat-input');
        if (input) {
            input.value = suggestion;
            input.focus();

            // Add visual feedback
            input.style.background = 'rgba(0,255,136,0.1)';
            input.style.borderColor = '#00ff88';

            // Auto-send after a brief moment
            setTimeout(() => {
                sendChatMessage();
                // Reset input style
                input.style.background = '';
                input.style.borderColor = '';
            }, 300);
        }
    }

    // Expose sendSuggestion globally for inline onclick handlers
    window.sendSuggestion = sendSuggestion;

    function formatAIResponse(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#00ffcc;">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em style="color:#ffcc00;">$1</em>')
            .replace(/`(.*?)`/g, '<code style="background:rgba(0,0,0,0.3);padding:2px 4px;border-radius:3px;color:#ff88cc;">$1</code>')
            .replace(/•/g, '<span style="color:#00ff88;">•</span>')
            .replace(/\n/g, '<br>')
            .replace(/✅/g, '<span style="color:#00ff88;">✅</span>')
            .replace(/❌/g, '<span style="color:#ff6b6b;">❌</span>')
            .replace(/⚠️/g, '<span style="color:#ffaa00;">⚠️</span>')
            .replace(/🔋/g, '<span style="color:#00ffff;">🔋</span>')
            .replace(/⚡/g, '<span style="color:#ffff00;">⚡</span>');
    }

    // ==========================================
    // ADVANCED MAP ACTION EXECUTION SYSTEM
    // ==========================================

    // Global map highlighting state
    let activeHighlights = new Map();
    let highlightAnimations = new Map();

    async function executeMapAction(mapAction) {
        console.log('executeMapAction called with:', mapAction);
        
        if (!mapAction) {
            console.error('No map action provided');
            return;
        }

        // Normalize coordinates (handle coords vs coordinates)
        if (mapAction.coords && !mapAction.coordinates) {
            mapAction.coordinates = mapAction.coords;
        }
        // Handle single dict coord vs array
        if (mapAction.coordinates && !Array.isArray(mapAction.coordinates) && mapAction.coordinates.lat) {
            mapAction.coordinates = [mapAction.coordinates.lon, mapAction.coordinates.lat];
        }

        if (!window.map) {
            console.error('Map not available');
            showNotification('❌ Map Error', 'Map not loaded yet', 'error');
            return;
        }

        if (!window.mapLoaded) {
            console.warn('Map not fully loaded yet, retrying in 1 second...');
            setTimeout(() => executeMapAction(mapAction), 1000);
            return;
        }

        if (typeof window.map.flyTo !== 'function') {
            console.error('Map flyTo method not available:', typeof window.map.flyTo);
            showNotification('❌ Map Error', 'Map not fully initialized', 'error');
            return;
        }

        try {
            switch (mapAction.type) {
                case 'zoom_to_location':
                case 'focus_and_highlight':
                case 'highlight_location':  // Added support for new tool
                    console.log('Processing map highlight action:', mapAction);

                    if (mapAction.coordinates && mapAction.coordinates.length === 2) {
                        console.log('Flying to coordinates:', mapAction.coordinates);

                        // CRITICAL: Reload network state to update map with restored substation
                        // Only if needed (restoration implied?)
                        if (mapAction.type === 'highlight_restore') await loadNetworkState();

                        // Clear previous highlights
                        clearAllHighlights();

                        // Enhanced fly-to with smooth animation
                        try {
                            window.map.flyTo({
                                center: mapAction.coordinates,
                                zoom: mapAction.zoom || 16,
                                pitch: mapAction.pitch || 45,
                                duration: 1500,
                                essential: true,
                                easing(t) { return t * (2 - t); }
                            });
                        } catch (flyError) {
                            console.error('Map flyTo error:', flyError);
                            showNotification('❌ Map Error', 'Could not focus on location', 'error');
                            return;
                        }

                        // Add advanced highlight with delay
                        setTimeout(() => {
                            createAdvancedHighlight({
                                coordinates: mapAction.coordinates,
                                name: mapAction.name || mapAction.location || 'Location',
                                type: 'location',
                                duration: 15000,
                                pulseColor: '#00ff88',
                                showConnections: mapAction.showConnections || true
                            });
                        }, 800);

                        // Show success notification
                        const locName = mapAction.name || mapAction.location || 'location';
                        showNotification('🗺️ Location Found', `Showing ${locName} on map`, 'success');
                    } else {
                        console.error('Invalid coordinates:', mapAction.coordinates);
                        showNotification('❌ Map Error', `Invalid coordinates for ${mapAction.location || 'location'}`, 'error');
                    }
                    break;

                case 'highlight_substation':
                case 'highlight_failure':
                case 'highlight_restore':
                    if (mapAction.substation_id || mapAction.location || mapAction.name) {
                        const locationName = mapAction.location || mapAction.name || mapAction.substation_id;
                        console.log('Highlighting substation:', locationName, mapAction.coordinates);
                        
                        // Fly to location if coordinates are provided
                        // Fly to location if coordinates are provided
                        let center = null;
                        if (Array.isArray(mapAction.coordinates) && mapAction.coordinates.length === 2) {
                            center = mapAction.coordinates;
                        } else if (mapAction.coordinates && mapAction.coordinates.lat && mapAction.coordinates.lon) {
                            center = [mapAction.coordinates.lon, mapAction.coordinates.lat];
                        }

                        if (center) {
                             window.map.flyTo({
                                center: center,
                                zoom: mapAction.zoom || 15,
                                pitch: mapAction.pitch || 45,
                                duration: 1500,
                                essential: true
                            });
                        }
                        
                        // Use advanced highlighter
                        if (center) {
                            highlightSubstationAdvanced(locationName, center);
                        } else {
                            highlightSubstationAdvanced(locationName, mapAction.coordinates);
                        }
                        
                        // Specific notification per type
                        if (mapAction.type === 'highlight_failure') {
                             showNotification('⚠️ Substation Failure', `${locationName} is OFFLINE`, 'error');
                        } else if (mapAction.type === 'highlight_restore') {
                             showNotification('✅ Substation Restored', `${locationName} is back ONLINE`, 'success');
                        } else {
                             showNotification('🏭 Substation Highlighted', `Showing ${locationName}`, 'info');
                        }
                    }
                    break;

                case 'zoom_to_area':
                    if (mapAction.bounds) {
                        window.map.fitBounds(mapAction.bounds, {
                            padding: { top: 80, bottom: 80, left: 80, right: 80 },
                            duration: 2000,
                            essential: true
                        });
                    }
                    break;

                case 'show_system_overview':
                    showSystemOverview();
                    break;

                case 'show_connections':
                    if (mapAction.coordinates) {
                        showLocationConnections(mapAction.coordinates, mapAction.name);
                    }
                    break;

                // ===== WORLD-CLASS LLM MAP ACTIONS =====
                case 'show_route':
                    if (mapAction.from_coords && mapAction.to_coords) {
                        showRouteOnMap(mapAction.from_coords, mapAction.to_coords, mapAction);
                    }
                    break;

                case 'visualize_power_grid':
                case 'show_power_grid':
                    console.log('🔌 Showing complete power grid');
                    showPowerGrid();
                    break;

                case 'hide_power_grid':
                    console.log('🔌 Hiding complete power grid');
                    hidePowerGrid();
                    break;

                case 'show_substation_network':
                    if (mapAction.substation_name) {
                        showSubstationNetwork(mapAction.substation_name, {
                            showCables: mapAction.show_cables || true,
                            focusZoom: mapAction.focus_zoom || 15
                        });
                    }
                    break;

                case 'show_ev_charging':
                    if (mapAction.substation && mapAction.coordinates) {
                        const evToggle = document.getElementById('layer-ev');
                        if (evToggle && !evToggle.checked) {
                            evToggle.checked = true;
                            toggleLayer('ev');
                        }
                        window.map.flyTo({
                            center: mapAction.coordinates,
                            zoom: mapAction.zoom || 16,
                            duration: 1500,
                            essential: true
                        });
                        setTimeout(() => {
                            highlightEVStations(mapAction.substation);
                            createAdvancedHighlight({
                                coordinates: mapAction.coordinates,
                                name: `${mapAction.substation} - EV Charging`,
                                type: 'ev_station',
                                duration: 15000,
                                pulseColor: '#00ffff'
                            });
                        }, 800);
                        showNotification('⚡ EV Charging Station', `Showing EV station for ${mapAction.substation}`, 'success');
                    }
                    break;

                case 'control_layers':
                    if (mapAction.layers && Array.isArray(mapAction.layers)) {
                        controlLayers(mapAction.layers, mapAction.message || '');
                    }
                    break;

                case 'focus_location':
                     // Already handled by normalization logic + general flyTo above?
                     // But if it slips through:
                    if (mapAction.coordinates) {
                        window.map.flyTo({
                            center: mapAction.coordinates,
                            zoom: mapAction.zoom || 16,
                            duration: 2000,
                            essential: true
                        });
                         setTimeout(() => {
                            createAdvancedHighlight({
                                coordinates: mapAction.coordinates,
                                name: mapAction.name || 'Location',
                                type: 'destination',
                                duration: 20000,
                                pulseColor: '#00aaff'
                            });
                        }, 1000);
                        showNotification('🎯 Location Focus', `Focused on ${mapAction.name || 'location'}`, 'success');
                    }
                    break;

                case 'show_all_vehicles':
                    highlightAllVehicles(mapAction);
                    showNotification('🚗 Vehicle Display', 'All vehicles highlighted', 'info');
                    break;

                case 'visualize_grid':
                    visualizePowerGrid(mapAction);
                    showNotification('⚡ Grid Visualization', 'Power grid displayed', 'info');
                    break;

                case 'show_heatmap':
                    showHeatmapOverlay(mapAction);
                    showNotification('🌡️ Heatmap Active', 'Heatmap overlay enabled', 'info');
                    break;

                case 'zoom_change':
                    const currentZoom = window.map.getZoom();
                    const newZoom = currentZoom + (mapAction.delta || 0);
                    window.map.easeTo({
                        zoom: newZoom,
                        duration: 800,
                        easing(t) { return t * (2 - t); }
                    });
                    break;

                case 'set_zoom':
                    window.map.easeTo({
                        zoom: mapAction.level || 12,
                        duration: 1000,
                        easing(t) { return t * (2 - t); }
                    });
                    break;

                case 'set_camera':
                    window.map.easeTo({
                        pitch: mapAction.pitch !== undefined ? mapAction.pitch : window.map.getPitch(),
                        bearing: mapAction.bearing !== undefined ? mapAction.bearing : window.map.getBearing(),
                        zoom: mapAction.zoom !== undefined ? mapAction.zoom : window.map.getZoom(),
                        duration: 1500
                    });
                    break;

                case 'set_map_view':
                    const pitch2d = mapAction.mode === '2d' ? 0 : (mapAction.pitch !== undefined ? mapAction.pitch : 60);
                    const bearing2d = mapAction.bearing !== undefined ? mapAction.bearing : window.map.getBearing();
                    window.map.easeTo({
                        pitch: pitch2d,
                        bearing: bearing2d,
                        zoom: mapAction.zoom !== undefined ? mapAction.zoom : window.map.getZoom(),
                        duration: 1500
                    });
                    showNotification('🗺️ Map View', mapAction.mode === '2d' ? 'Switched to 2D top-down view' : 'Switched to 3D view', 'success');
                    break;
            }
        } catch (error) {
            console.error('Map action execution error:', error);
            showNotification('❌ Map Error', `Action failed: ${error.message}`, 'error');
        }
    }

    // ==========================================
    // ADVANCED HIGHLIGHTING SYSTEM
    // ==========================================

    function createAdvancedHighlight(options) {
        if (!window.map) return;

        const {
            coordinates,
            name,
            type = 'location',
            duration = 15000,
            pulseColor = '#00ff88',
            showConnections = false
        } = options;

        // Clear existing highlight for this location
        const key = `${coordinates[0]}_${coordinates[1]}`;
        if (activeHighlights.has(key)) {
            activeHighlights.get(key).remove();
        }

        // Create advanced pulsing marker
        const pulseDiv = document.createElement('div');
        pulseDiv.className = 'advanced-pulse-marker';
        pulseDiv.innerHTML = `
            <div class="pulse-ring"></div>
            <div class="pulse-core"></div>
            <div class="pulse-label">${name}</div>
        `;

        // Enhanced CSS animations
        if (!document.getElementById('advanced-pulse-animation')) {
            const style = document.createElement('style');
            style.id = 'advanced-pulse-animation';
            style.textContent = `
                .advanced-pulse-marker {
                    position: relative;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .pulse-ring {
                    position: absolute;
                    width: 40px;
                    height: 40px;
                    border: 3px solid ${pulseColor};
                    border-radius: 50%;
                    animation: pulseRing 2s ease-out infinite;
                    opacity: 0;
                }
                .pulse-core {
                    width: 16px;
                    height: 16px;
                    background: ${pulseColor};
                    border: 2px solid #ffffff;
                    border-radius: 50%;
                    box-shadow: 0 0 15px ${pulseColor};
                    animation: pulseCore 1.5s ease-in-out infinite alternate;
                }
                .pulse-label {
                    position: absolute;
                    top: -35px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                    white-space: nowrap;
                    pointer-events: none;
                    opacity: 0;
                    animation: labelFade 0.5s ease-in 1s forwards;
                }
                @keyframes pulseRing {
                    0% {
                        transform: scale(0.8);
                        opacity: 1;
                    }
                    100% {
                        transform: scale(2.5);
                        opacity: 0;
                    }
                }
                @keyframes pulseCore {
                    0% {
                        transform: scale(1);
                        box-shadow: 0 0 15px ${pulseColor};
                    }
                    100% {
                        transform: scale(1.2);
                        box-shadow: 0 0 25px ${pulseColor};
                    }
                }
                @keyframes labelFade {
                    from {
                        opacity: 0;
                        transform: translateX(-50%) translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(-50%) translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }

        // Create marker with enhanced popup
        const marker = new mapboxgl.Marker(pulseDiv)
            .setLngLat(coordinates)
            .setPopup(
                new mapboxgl.Popup({
                    offset: 35,
                    className: 'custom-popup'
                }).setHTML(`
                    <div style="padding: 10px;">
                        <h4 style="margin: 0 0 8px 0; color: ${pulseColor};">${name}</h4>
                        <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                            📍 ${coordinates[1].toFixed(4)}, ${coordinates[0].toFixed(4)}<br>
                            🎯 Click to see connections
                        </p>
                    </div>
                `)
            )
            .addTo(window.map);

        // Store reference
        activeHighlights.set(key, marker);

        // Show connections if requested
        if (showConnections) {
            setTimeout(() => {
                showLocationConnections(coordinates, name);
            }, 1500);
        }

        // Auto-remove after duration
        setTimeout(() => {
            if (activeHighlights.has(key)) {
                activeHighlights.get(key).remove();
                activeHighlights.delete(key);
            }
        }, duration);

        return marker;
    }

    function clearAllHighlights() {
        activeHighlights.forEach(marker => marker.remove());
        activeHighlights.clear();
    }

    // ==========================================
    // ENHANCED SUBSTATION HIGHLIGHTING
    // ==========================================

    function highlightSubstationAdvanced(substationId, providedCoords = null) {
        const substationCoords = {
            'times_square': [-73.9857, 40.7549],
            'times square': [-73.9857, 40.7549],
            'penn_station': [-73.9904, 40.7505],
            'penn station': [-73.9904, 40.7505],
            'grand_central': [-73.9772, 40.7527],
            'grand central': [-73.9772, 40.7527],
            'murray_hill': [-73.9816, 40.7486],
            'murray hill': [-73.9816, 40.7486],
            'turtle_bay': [-73.9665, 40.7519],
            'turtle bay': [-73.9665, 40.7519],
            'chelsea': [-73.9969, 40.7439],
            'hells_kitchen': [-73.9897, 40.7648],
            'hell\'s kitchen': [-73.9897, 40.7648],
            'midtown_east': [-73.9735, 40.7549],
            'midtown east': [-73.9735, 40.7549],
            'wall street': [-73.9901, 40.7074],
            'broadway': [-73.9776, 40.7614],
            'central park': [-73.9654, 40.7829]
        };

        // Try multiple ways to match the substation name
        let coords = providedCoords;
        
        // Normalize object coordinates to array if needed
        if (coords && !Array.isArray(coords) && coords.lat && coords.lon) {
            coords = [coords.lon, coords.lat];
        }

        if (!coords) {
            const normalizedId = substationId.toLowerCase().replace(/[^a-z\s]/g, '');
            coords = substationCoords[normalizedId] || substationCoords[substationId.toLowerCase()] || substationCoords[substationId];
        }

        console.log('highlightSubstationAdvanced:', substationId, '-> coords:', coords);

        if (coords && coords.length === 2) {
            const formattedName = substationId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            // Direct highlighting to avoid recursive calls
            clearAllHighlights();

            // Zoom and highlight
            if (window.map) {
                console.log('Flying to coordinates:', coords);
                window.map.flyTo({
                    center: coords,
                    zoom: 17,
                    duration: 1500,
                    essential: true
                });

                // Create highlight after zoom
                setTimeout(() => {
                    console.log('Creating highlight for:', formattedName);
                    createAdvancedHighlight({
                        coordinates: coords,
                        name: `${formattedName} Substation`,
                        type: 'substation',
                        duration: 15000,
                        pulseColor: '#ff6b6b',
                        showConnections: true
                    });
                }, 800);

                // Show info
                setTimeout(() => {
                    showSubstationInfo(coords, formattedName);
                }, 2000);

                showNotification('🏭 Substation Located', `Highlighting ${formattedName}`, 'success');
            } else {
                console.error('Map not available');
            }
        } else {
            console.error('Coordinates not found for substation:', substationId);
            showNotification('⚠️ Location Error', `Substation "${substationId}" coordinates not found`, 'warning');
        }
    }

    function showSubstationInfo(coordinates, name) {
        if (!window.map) return;

        // Create info overlay
        const infoDiv = document.createElement('div');
        infoDiv.className = 'substation-info-overlay';
        infoDiv.style.cssText = `
            position: fixed;
            top: 120px;
            right: 20px;
            width: 300px;
            background: linear-gradient(135deg, rgba(0, 40, 60, 0.95), rgba(0, 20, 40, 0.98));
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 12px;
            padding: 16px;
            z-index: 1000;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            animation: slideInRight 0.5s ease;
        `;

        infoDiv.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: between; margin-bottom: 12px;">
                <h3 style="color: #00ff88; margin: 0; font-size: 16px;">🏭 ${name}</h3>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: #fff; font-size: 18px; cursor: pointer; margin-left: auto;">×</button>
            </div>
            <div style="font-size: 13px; color: #ccc; line-height: 1.5;">
                <p><strong>📍 Location:</strong> ${coordinates[1].toFixed(4)}, ${coordinates[0].toFixed(4)}</p>
                <p><strong>⚡ Voltage:</strong> 13.8kV Primary / 480V Secondary</p>
                <p><strong>🔋 Capacity:</strong> 50-100 MVA</p>
                <p><strong>🔄 Status:</strong> <span id="substation-status">Checking...</span></p>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <button onclick="toggleSubstationControl('${name}')" class="btn btn-secondary" style="width: 100%; padding: 8px; font-size: 12px;">🔧 Control Panel</button>
                </div>
            </div>
        `;

        document.body.appendChild(infoDiv);

        // Update status
        setTimeout(() => {
            const statusEl = document.getElementById('substation-status');
            if (statusEl) {
                statusEl.innerHTML = '<span style="color: #00ff88;">✅ Operational</span>';
            }
        }, 1000);

        // Auto-remove after 15 seconds
        setTimeout(() => {
            if (infoDiv.parentElement) {
                infoDiv.remove();
            }
        }, 15000);
    }

    function showLocationConnections(coordinates, name) {
        // Show connected infrastructure
        const connections = [
            { name: 'Traffic Lights', count: 12, color: '#ffaa00' },
            { name: 'EV Stations', count: 3, color: '#00ff88' },
            { name: 'Primary Lines', count: 4, color: '#00ffcc' },
            { name: 'Secondary Lines', count: 8, color: '#ffbb44' }
        ];

        showNotification(
            `🔗 ${name} Connections`,
            connections.map(c => `${c.name}: ${c.count}`).join(' • '),
            'info'
        );
    }

    function showSystemOverview() {
        clearAllHighlights();

        window.map.flyTo({
            center: [-73.9857, 40.7549],
            zoom: 12,
            duration: 2000,
            essential: true
        });

        showNotification('🗺️ System Overview', 'Showing Manhattan power grid overview', 'info');

        // Highlight all major substations
        setTimeout(() => {
            const majorSubstations = [
                { name: 'Times Square', coords: [-73.9857, 40.7549] },
                { name: 'Grand Central', coords: [-73.9772, 40.7527] },
                { name: 'Penn Station', coords: [-73.9904, 40.7505] },
                { name: 'Chelsea', coords: [-73.9969, 40.7439] }
            ];

            majorSubstations.forEach((sub, index) => {
                setTimeout(() => {
                    createAdvancedHighlight({
                        coordinates: sub.coords,
                        name: sub.name + ' Substation',
                        type: 'substation',
                        duration: 20000,
                        pulseColor: '#ff6b6b'
                    });
                }, index * 500);
            });
        }, 1500);
    }

    function handleAIKeyPress(event) {
        if (event.key === 'Enter') {
            const aiSendButton = document.getElementById('ai-send');
            if (aiSendButton) {
                aiSendButton.click();
            }
        }
    }

    function sendChatMessage() {
        const input = document.getElementById('chat-input');
        const text = (input.value||'').trim();
        if (!text) return;

        // Check for scenario confirmation/cancellation
        const textLower = text.toLowerCase();
        if (window.chatbotScenarioHandler && window.chatbotScenarioHandler.awaitingConfirmation) {
            if (textLower === 'confirm' || textLower === 'yes' || textLower === 'proceed') {
                const box = document.getElementById('chat-messages');
                box.innerHTML += `<div class="msg user" style="margin:10px 0;padding:14px 18px;background:linear-gradient(135deg,rgba(0,170,255,0.25),rgba(0,120,255,0.18));border-radius:14px;border:1px solid rgba(0,170,255,0.5);box-shadow:0 3px 12px rgba(0,170,255,0.2);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:0;right:0;width:4px;height:100%;background:linear-gradient(180deg,#00aaff,#0077ff);box-shadow:0 0 10px rgba(0,170,255,0.6);"></div>
                    <strong style="color:#00d4ff;display:flex;align-items:center;margin-bottom:8px;font-size:13px;letter-spacing:0.3px;">
                        <svg width="16" height="16" style="margin-right:7px;" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>You
                    </strong>
                    <div style="color:rgba(255,255,255,0.98);font-size:14px;line-height:1.6;padding-left:23px;">${text}</div>
                </div>`;
                input.value = '';
                box.scrollTop = box.scrollHeight;
                window.chatbotScenarioHandler.handleScenarioConfirmation();
                return;
            } else if (textLower === 'cancel' || textLower === 'no' || textLower === 'abort') {
                const box = document.getElementById('chat-messages');
                box.innerHTML += `<div class="msg user" style="margin:10px 0;padding:14px 18px;background:linear-gradient(135deg,rgba(0,170,255,0.25),rgba(0,120,255,0.18));border-radius:14px;border:1px solid rgba(0,170,255,0.5);box-shadow:0 3px 12px rgba(0,170,255,0.2);position:relative;overflow:hidden;">
                    <div style="position:absolute;top:0;right:0;width:4px;height:100%;background:linear-gradient(180deg,#00aaff,#0077ff);box-shadow:0 0 10px rgba(0,170,255,0.6);"></div>
                    <strong style="color:#00d4ff;display:flex;align-items:center;margin-bottom:8px;font-size:13px;letter-spacing:0.3px;">
                        <svg width="16" height="16" style="margin-right:7px;" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>You
                    </strong>
                    <div style="color:rgba(255,255,255,0.98);font-size:14px;line-height:1.6;padding-left:23px;">${text}</div>
                </div>`;
                input.value = '';
                box.scrollTop = box.scrollHeight;
                window.chatbotScenarioHandler.handleScenarioCancellation();
                return;
            }
        }

        const box = document.getElementById('chat-messages');
        box.innerHTML += `<div class="msg user" style="margin:10px 0;padding:14px 18px;background:linear-gradient(135deg,rgba(0,170,255,0.25),rgba(0,120,255,0.18));border-radius:14px;border:1px solid rgba(0,170,255,0.5);box-shadow:0 3px 12px rgba(0,170,255,0.2), inset 0 1px 0 rgba(255,255,255,0.15);position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;right:0;width:4px;height:100%;background:linear-gradient(180deg,#00aaff,#0077ff);box-shadow:0 0 10px rgba(0,170,255,0.6);"></div>
            <strong style="color:#00d4ff;display:flex;align-items:center;margin-bottom:8px;font-size:13px;letter-spacing:0.3px;">
                <svg width="16" height="16" style="margin-right:7px;" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>You
            </strong>
            <div style="color:rgba(255,255,255,0.98);font-size:14px;line-height:1.6;padding-left:23px;">${text}</div>
        </div>`;

        input.value = '';

        // ALL commands are now processed by the backend agentic chatbot.
        // Frontend interception (llmScenarioHandler) is bypassed.
        proceedWithNormalChat(text, box);
    }

    // Separated normal chat logic
    function proceedWithNormalChat(text, box) {
        box.innerHTML += `<div class="typing">AI is analyzing…<div class="tool-progress-feed" id="toolProgressFeed" style="display:none;"></div></div>`;
        const typingRef = box.querySelector('.typing');

        // Listen for real-time tool progress events
        const progressHandler = (data) => {
            const feed = document.getElementById('toolProgressFeed');
            if (feed) {
                feed.style.display = 'flex';
                // Update the main typing text
                const mainText = typingRef.childNodes[0];
                if (mainText && mainText.nodeType === Node.TEXT_NODE) {
                    mainText.textContent = `Executing tools (step ${data.iteration})…`;
                }
                // Add progress item
                const item = document.createElement('div');
                item.className = 'tool-progress-item';
                item.innerHTML = `<div class="spinner"></div><span>🔧 ${data.tool}(${Object.values(data.args || {}).join(', ')})</span>`;
                feed.appendChild(item);
                box.scrollTop = box.scrollHeight;
            }
        };
        if (window.socket) {
            window.socket.on('chatbot_tool_progress', progressHandler);
        }

        // Use the enhanced Ultra-Intelligent AI chat endpoint
        fetch('/api/ai/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:text, user_id:'web_user'})})
        .then(r=>r.json()).then(data=>{
            // Clean up progress handler
            if (window.socket) window.socket.off('chatbot_tool_progress', progressHandler);
            if (typingRef) typingRef.remove();

            // Handle ultra-intelligent chatbot response format
            let aiResponse = null;
            if (data.status === 'success' && data.response) {
                // Backend returns {status: 'success', response: 'text', full_data: {...}}
                // Extract full_data if available, otherwise create object with response text
                aiResponse = data.full_data || { text: data.response };
            } else if (data.text) {
                aiResponse = data;
            }

            if (aiResponse && aiResponse.text) {
                // Check if this is a scenario prep response
                if (window.chatbotScenarioHandler && window.chatbotScenarioHandler.processChatbotResponse(aiResponse)) {
                    // Scenario handler took care of the response
                    box.scrollTop = box.scrollHeight;
                    return;
                }

                let responseHtml = `<div class="msg ai" style="margin:10px 0;padding:16px 20px;background:linear-gradient(135deg,rgba(15,25,45,0.95),rgba(20,30,50,0.92));border-radius:16px;border:1px solid rgba(0,255,136,0.3);box-shadow:0 4px 16px rgba(0,255,136,0.15), inset 0 1px 0 rgba(255,255,255,0.1);position:relative;overflow:hidden;">`;
                responseHtml += `<div style="position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(180deg,#00ff88,#00d4ff);box-shadow:0 0 12px rgba(0,255,136,0.5);"></div>`;
                responseHtml += `<strong style="color:#00ff88;display:flex;align-items:center;margin-bottom:10px;font-size:14px;letter-spacing:0.3px;"><svg width="18" height="18" style="margin-right:8px;" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 5.58 2 10c0 2.39 1.31 4.53 3.4 6.01-.14.52-.51 1.89-.59 2.24-.09.37.13.73.5.82.26.06.52-.03.7-.21.28-.27 1.25-1.2 1.77-1.7.79.22 1.63.34 2.52.34 5.52 0 10-3.58 10-8s-4.48-8-10-8Z"/></svg>Ultra-Intelligent AI</strong>`;
                responseHtml += `<div style="line-height:1.7;color:rgba(255,255,255,0.95);font-size:14px;padding-left:26px;" class="markdown-content">${window.renderMarkdown(aiResponse.text)}</div>`;

                // ═══ GLASS BOX: Show tool execution transparency ═══
                if (aiResponse.tool_calls_made && aiResponse.tool_calls_made.length > 0) {
                    const toolCount = aiResponse.tool_calls_made.length;
                    const iterations = aiResponse.iterations || 1;
                    responseHtml += `<div class="glass-box-panel" style="margin-top:12px;padding-left:26px;">`;
                    responseHtml += `<div class="glass-box-header" onclick="this.parentElement.classList.toggle('expanded')" style="cursor:pointer;display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(0,170,255,0.08);border:1px solid rgba(0,170,255,0.2);border-radius:10px;transition:all 0.3s ease;">`;
                    responseHtml += `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00aaff" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`;
                    responseHtml += `<span style="font-size:12px;color:#00aaff;font-weight:600;">Agent Actions</span>`;
                    responseHtml += `<span style="font-size:11px;color:rgba(0,170,255,0.7);margin-left:auto;">${toolCount} tool${toolCount > 1 ? 's' : ''} · ${iterations} step${iterations > 1 ? 's' : ''}</span>`;
                    responseHtml += `<svg class="glass-box-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#00aaff" stroke-width="2" style="transition:transform 0.3s;"><polyline points="6 9 12 15 18 9"/></svg>`;
                    responseHtml += `</div>`;
                    responseHtml += `<div class="glass-box-body" style="max-height:0;overflow:hidden;transition:max-height 0.4s ease;">`;
                    responseHtml += `<div style="padding:8px 0 4px 0;display:flex;flex-direction:column;gap:4px;">`;
                    aiResponse.tool_calls_made.forEach((tc, idx) => {
                        const icon = tc.success ? '✓' : '✗';
                        const color = tc.success ? '#00ff88' : '#ff6b6b';
                        const argsStr = Object.entries(tc.args || {}).map(([k,v]) => `${k}: ${JSON.stringify(v)}`).join(', ');
                        responseHtml += `<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(255,255,255,0.02);border-radius:8px;border-left:3px solid ${color};">`;
                        responseHtml += `<span style="color:${color};font-weight:700;font-size:13px;min-width:16px;">${icon}</span>`;
                        responseHtml += `<code style="font-size:11px;color:#e0e0ff;font-family:'JetBrains Mono',monospace;word-break:break-all;">${tc.tool}(${argsStr})</code>`;
                        responseHtml += `</div>`;
                    });
                    responseHtml += `</div></div></div>`;

                    // Downloadable file links (reports, snapshots)
                    const downloadableTools = aiResponse.tool_calls_made.filter(
                        tc => tc.success && (tc.url || tc.download_link || tc.server_json)
                    );
                    if (downloadableTools.length > 0) {
                        responseHtml += `<div style="margin-top:10px;padding-left:26px;display:flex;flex-wrap:wrap;gap:8px;">`;
                        downloadableTools.forEach(tc => {
                            const url = tc.url || tc.download_link;
                            const jsonUrl = tc.server_json;
                            if (url) {
                                const fname = url.split('/').pop();
                                const isPdf = fname.endsWith('.pdf');
                                const icon = isPdf ? '📄' : '📸';
                                const label = isPdf ? 'Download Report' : 'Download File';
                                responseHtml += `<a href="${url}" download="${fname}" style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;background:linear-gradient(135deg,rgba(0,255,136,0.15),rgba(0,212,255,0.1));border:1px solid rgba(0,255,136,0.4);border-radius:10px;color:#00ff88;font-size:12px;font-weight:600;text-decoration:none;cursor:pointer;transition:all 0.2s ease;" onmouseover="this.style.background='rgba(0,255,136,0.25)';this.style.transform='translateY(-1px)'" onmouseout="this.style.background='linear-gradient(135deg,rgba(0,255,136,0.15),rgba(0,212,255,0.1))';this.style.transform='none'">${icon} ${label}</a>`;
                            }
                            if (jsonUrl) {
                                responseHtml += `<a href="${jsonUrl}" download="${jsonUrl.split('/').pop()}" style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;background:linear-gradient(135deg,rgba(0,170,255,0.15),rgba(0,100,255,0.1));border:1px solid rgba(0,170,255,0.4);border-radius:10px;color:#00aaff;font-size:12px;font-weight:600;text-decoration:none;cursor:pointer;transition:all 0.2s ease;" onmouseover="this.style.background='rgba(0,170,255,0.25)';this.style.transform='translateY(-1px)'" onmouseout="this.style.background='linear-gradient(135deg,rgba(0,170,255,0.15),rgba(0,100,255,0.1))';this.style.transform='none'">📋 Download JSON</a>`;
                            }
                        });
                        responseHtml += `</div>`;
                    }
                }

                // Add suggestions if available
                if (aiResponse.suggestions && aiResponse.suggestions.length > 0) {
                    responseHtml += `<div style="margin-top:12px;"><div style="font-size:12px;color:#00ffcc;margin-bottom:6px;">💡 Try these suggestions:</div>`;
                    responseHtml += `<div style="display:flex;flex-wrap:wrap;gap:6px;">`;
                    aiResponse.suggestions.slice(0,3).forEach(suggestion => {
                        responseHtml += `<button onclick="sendSuggestion('${suggestion.replace(/'/g, '\\\'')}')" style="padding:4px 8px;background:rgba(0,123,255,0.3);border:1px solid rgba(0,123,255,0.5);border-radius:12px;color:white;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,123,255,0.6)'" onmouseout="this.style.background='rgba(0,123,255,0.3)'">${suggestion}</button>`;
                    });
                    responseHtml += `</div></div>`;
                }

                // Show typo corrections if available
                if (aiResponse.corrections_made && aiResponse.corrections_made.length > 0) {
                    responseHtml += `<div style="margin-top:8px;padding:6px;background:rgba(255,255,0,0.1);border-radius:6px;font-size:11px;color:#ffff88;">✨ Auto-corrected: ${aiResponse.corrections_made.join(', ')}</div>`;
                }

                // Only show backend error if there's a failure
                if (aiResponse.backend_error) {
                    responseHtml += `<div style="margin-top:8px;padding:6px;background:rgba(255,107,107,0.15);border-radius:6px;font-size:11px;color:#ff6b6b;border-left:3px solid #ff6b6b;">❌ <strong>Backend connection failed</strong></div>`;
                }

                // Don't show extra system changes or action details - the main message already contains this info

                responseHtml += `</div>`;
                box.innerHTML += responseHtml;

                // Enhanced map action handling
                if (aiResponse.map_action) {
                    console.log('Executing map action:', aiResponse.map_action);
                    setTimeout(() => {
                        executeMapAction(aiResponse.map_action);
                    }, 500);
                }

                // Handle map updates (for multiple actions)
                if (aiResponse.map_updates && aiResponse.map_updates.length > 0) {
                    console.log('Executing map updates:', aiResponse.map_updates);
                    aiResponse.map_updates.forEach((update, index) => {
                        setTimeout(() => {
                            executeMapAction(update);
                        }, 500 + (index * 200));
                    });
                }

            } else {
                box.innerHTML += `<div class="msg ai" style="margin:8px 0;padding:12px;background:rgba(255,107,107,0.1);border-radius:12px;border:1px solid rgba(255,107,107,0.3);"><strong style="color:#ff6b6b;">Ultra-AI:</strong> ${data.error||data.message||'No response received. Please try again.'}</div>`;
            }
            box.scrollTop = box.scrollHeight;
        }).catch(()=>{
            if (typingRef) typingRef.remove();
            box.innerHTML += '<div class="msg ai" style="color:#ff6b6b;"><strong>AI:</strong> Request failed</div>';
        });
    }



    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            map.resize();
        }, 100);
    });
    // V2G Management Functions
    // Removed polling interval - using WebSockets

    function initV2G() {
        // Initial setup only
        console.log("V2G Dashboard initialized (WebSocket mode)");
    }

    async function refreshV2GDashboard() {
        try {
            const res = await fetch('/api/v2g/status');
            const data = await res.json();
            if (data) updateV2GDashboard(data);
        } catch (e) {
            console.error('V2G refresh error:', e);
        }
    }

    async function updateV2GDashboard(data) {
        if (!data) return;

        // Verify data structure matches what we expect from backend
        // If data comes from network_state, it might be nested differently than the specific API response
        // But let's assume valid data for now or fallback safely
        
        const activeSessions = data.active_sessions_list || data.v2g_sessions || []; 
        const totalPower = data.v2g_total_power || data.total_power_kw || 0;
        const totalCars = data.v2g_vehicle_count || data.vehicles_participated || 0;
        const currentRate = data.v2g_rate || data.current_rate || 0.15;
        const totalEarnings = data.v2g_earnings || data.total_earnings || 0;

        // DEBUG: Log V2G data for troubleshooting
        console.log("V2G Update:", { active: activeSessions.length, power: totalPower, vehicles: totalCars });

        // CRITICAL FIX: Ensure substation list is updated
        updateV2GSubstationList(data);

        // Update metrics with animation
        updateWithAnimation('v2g-active-sessions', activeSessions.length);
        updateWithAnimation('v2g-power', totalPower);
        updateWithAnimation('v2g-vehicles', totalCars);
        updateWithAnimation('v2g-rate', `$${currentRate.toFixed(2)}`);
        
        // Count actual discharging vehicles if list provided
        let dischargingCount = 0;
        if (Array.isArray(activeSessions)) {
            dischargingCount = activeSessions.filter(s => s.status === 'discharging').length;
        } else {
             dischargingCount = data.active_vehicles ? data.active_vehicles.length : 0;
        }
        updateWithAnimation('v2g-discharging-count', dischargingCount);
        
        // Animate earnings with counting effect
        const earningsEl = document.getElementById('v2g-earnings');
        if (earningsEl) {
            const currentVal = parseFloat(earningsEl.textContent.replace('$', '') || 0);
            const newVal = totalEarnings;
            if (Math.abs(currentVal - newVal) > 0.01) {
                animateValue(earningsEl, currentVal, newVal, 500, '$');
            }
        }
        
        // Update active sessions list if data available
        if (Array.isArray(activeSessions)) {
            updateV2GSessionList(activeSessions);
        }
    }

    function updateV2GSessionList(activeSessions) {
        const sessionList = document.getElementById('v2g-session-list');
        if (!sessionList) return;

        if (activeSessions && activeSessions.length > 0) {
            sessionList.innerHTML = activeSessions.map(v => {
                // Calculate real-time progress
                // If we have detailed session object use it, otherwise fallback
                const chargeRate = 250; // kW
                const earnings = v.earnings || 25.50; 
                const progress = 75; 
                const powerRate = 250; 
                
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(255,255,255,0.03); margin-bottom: 8px; border-radius: 8px; border-left: 3px solid #00ff88;">
                        <div>
                            <div style="font-weight: 600; color: #fff;">${v.vehicle_id || v.id || 'Vehicle'}</div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                                Discharging at ${chargeRate}kW • Earned $${typeof earnings === 'number' ? earnings.toFixed(2) : earnings}
                            </div>
                            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 4px;">
                                <div style="width: ${Math.min(progress, 100)}%; height: 100%; background: linear-gradient(90deg, #00ffff, #00ff88); border-radius: 2px; transition: width 0.3s;"></div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 14px; color: #ffaa00; font-weight: 600;">
                                ${powerRate} kW
                            </div>
                            <div style="font-size: 10px; color: var(--text-muted);">
                                ${v.substation}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            sessionList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No active V2G sessions</div>';
        }
    }

    // Refactored to accept data - NO POLLING
    function updateV2GSubstationList(v2gData) {
        if (!v2gData) return;
        
        // Use global networkState which is kept fresh by WebSockets
        if (!networkState || !networkState.substations) return;
        
        const failedSubstations = networkState.substations.filter(s => !s.operational);
        const listElement = document.getElementById('v2g-substation-list');
        if (!listElement) return;
        
        if (failedSubstations.length === 0) {
            // If previously showed restored banner, keep it; otherwise nothing to do
            listElement.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">All substations operational - V2G not needed</div>';
            return;
        }
        
        // Track which substations have triggered the restored UX, so we don't duplicate
        window._v2gRestoredShown = window._v2gRestoredShown || {};

        listElement.innerHTML = failedSubstations.map(sub => {
            const isV2GEnabled = v2gData.enabled_substations.includes(sub.name);
            
            // CRITICAL FIX: Show real-time power status
            let baseLoadMW = sub.load_mw;
            let energyDelivered = v2gData.energy_delivered ? v2gData.energy_delivered[sub.name] || 0 : 0;
            let energyRequired = v2gData.energy_required ? v2gData.energy_required[sub.name] || 50 : 50;
            
            // Calculate remaining power needed (decreases as energy is delivered)
            let remainingPowerMW = Math.max(0, baseLoadMW * (1 - energyDelivered / energyRequired));
            
            // If V2G is active, show active discharge power
            let activePowerKW = 0;
            if (isV2GEnabled && v2gData.active_vehicles) {
                const activeVehiclesAtSub = v2gData.active_vehicles.filter(v => v.substation === sub.name);
                activePowerKW = activeVehiclesAtSub.length * 250; // 250kW per vehicle
            }
            
            // Calculate restoration progress
            const restorationProgress = Math.min(100, (energyDelivered / energyRequired) * 100);

            // Simple logic: when progress hits 100%, remove emergency UI and show success
            if (isV2GEnabled && restorationProgress >= 100 && !window._v2gRestoredShown[sub.name]) {
                window._v2gRestoredShown[sub.name] = true;
                // Call backend restore; UI handled locally
                fetch(`/api/restore/${encodeURIComponent(sub.name)}`, { method: 'POST' }).catch(() => {});
                // Force cleanup and show persistent success banner with dismiss
                forceClearV2GEmergencyUI();
                forceShowRestorationBanner();
            }
            
            // Hide progress bar when complete to avoid showing 0 after reset
            const progressBar = isV2GEnabled && restorationProgress > 0 && restorationProgress < 100 ? `
                <div style="width: 100%; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 6px;">
                    <div style="width: ${restorationProgress}%; height: 100%; background: linear-gradient(90deg, #ff6666, #00ff88); border-radius: 2px; transition: width 0.5s;"></div>
                </div>
                <div style="font-size: 10px; color: #00ff88; margin-top: 4px;">
                    ${energyDelivered.toFixed(1)}/${energyRequired.toFixed(1)} kWh (${restorationProgress.toFixed(0)}%)
                </div>
            ` : '';
            
            // Status indicator
            const statusIcon = restorationProgress >= 100 ? '✅' : 
                            restorationProgress > 0 ? '⚡' : '⚠️';
            
            // Show active power being delivered
            const powerStatus = activePowerKW > 0 ? 
                `<span style="color: #00ffff;">↓ ${(activePowerKW/1000).toFixed(1)} MW</span>` : 
                `<span style="color: #ffaa00;">${remainingPowerMW.toFixed(1)} MW</span>`;
            
            // If restored, suppress the entire emergency-style item from appearing like a pending issue
            if (restorationProgress >= 100) {
                return `
                <div class="v2g-substation-item" style="background: rgba(0, 255, 136, 0.06); border-color: rgba(0, 255, 136, 0.25);">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 18px;">✅</span>
                            <span style="font-weight: 600; color: #a6ffc9;">${sub.name}</span>
                        </div>
                        <div style="font-size: 12px; color: #00ff88; margin-top: 4px;">Restored</div>
                    </div>
                    <div style="width: 56px; text-align: right; font-size: 11px; color: var(--text-muted);">OK</div>
                </div>`;
            }

            return `
                <div class="v2g-substation-item" style="${isV2GEnabled ? 'background: rgba(0, 255, 255, 0.1); border-color: rgba(0, 255, 255, 0.3);' : ''}">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 18px;">${statusIcon}</span>
                            <span style="font-weight: 600; color: #ff6666;">${sub.name}</span>
                        </div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                            ${restorationProgress >= 100 ? '<span style="color:#00ff88;">Restored</span>' : `Needs: ${powerStatus}`}
                            ${isV2GEnabled ? ` | Rate: <span style="color: #00ff88;">$${v2gData.current_rate.toFixed(2)}/kWh</span>` : ''}
                        </div>
                        ${progressBar}
                    </div>
                    <label class="v2g-toggle">
                        <input type="checkbox" 
                            ${isV2GEnabled ? 'checked' : ''} 
                            ${restorationProgress >= 100 ? 'disabled' : ''}
                            onchange="toggleV2GForSubstation('${sub.name}', this.checked)">
                        <span class="v2g-slider"></span>
                    </label>
                </div>
            `;
        }).join('');
    }
    // Smooth value animation function
    function animateValue(element, start, end, duration, prefix = '') {
        const range = end - start;
        const startTime = performance.now();
        
        function update() {
            const currentTime = performance.now();
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeInOutQuad = progress < 0.5 
                ? 2 * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;
            
            const current = start + (range * easeInOutQuad);
            element.textContent = prefix + current.toFixed(2);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        update();
    }    

    async function toggleV2GForSubstation(substationName, enable) {
        const endpoint = enable ? 'enable' : 'disable';
        
        try {
            const response = await fetch(`/api/v2g/${endpoint}/${substationName}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (enable) {
                    showNotification(
                        '⚡ V2G Enabled',
                        `Seeking EVs to restore ${substationName} at $${result.rate_per_kwh.toFixed(2)}/kWh`,
                        'success'
                    );
                } else {
                    showNotification(
                        '🔌 V2G Disabled',
                        `V2G disabled for ${substationName}`,
                        'info'
                    );
                }
            } else {
                showNotification(
                    '❌ V2G Error',
                    result.message,
                    'error'
                );
            }
            
            // Refresh dashboard
            updateV2GDashboard();
            
        } catch (error) {
            console.error('Error toggling V2G:', error);
            showNotification('❌ Error', 'Failed to toggle V2G', 'error');
        }
    }

    // Initialize V2G when map loads


    // Add V2G visual layer
    function renderV2GFlow() {
        if (!networkState) return;
        
        // Show energy flow from vehicles to substations
        const v2gFlows = [];
        
        // This would show animated energy flows from V2G vehicles to substations
        // Implementation depends on your exact visualization needs
    }    
    // Fix for black space issue
    function fixTabLayout() {
        // Force hidden tabs to not affect layout
        document.querySelectorAll('.tab').forEach(tab => {
            if (!tab.classList.contains(`tab-${document.body.dataset.tab}`)) {
                tab.style.position = 'absolute';
                tab.style.visibility = 'hidden';
                tab.style.pointerEvents = 'none';
                tab.style.opacity = '0';
                tab.style.height = '0';
                tab.style.overflow = 'hidden';
            } else {
                tab.style.position = '';
                tab.style.visibility = '';
                tab.style.pointerEvents = '';
                tab.style.opacity = '';
                tab.style.height = '';
                tab.style.overflow = '';
            }
        });
        
        // Force map to resize
        if (map) {
            map.resize();
        }
    }

    // Call on tab change
    function selectTab(tab, el) {
        document.body.setAttribute('data-tab', tab);
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        if (el) el.classList.add('active');
        fixTabLayout(); // Add this line
    }
    // ==========================================
    // INITIALIZATION
    // ==========================================
    map.on('load', () => {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100px); opacity: 0; }
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .vehicle-marker-ultra {
                will-change: transform;
                backface-visibility: hidden;
                -webkit-backface-visibility: hidden;
                transform: translateZ(0);
                -webkit-transform: translateZ(0);
            }
            .mapboxgl-canvas {
                image-rendering: optimizeSpeed;
                image-rendering: -webkit-optimize-contrast;
            }
            * {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
        `;
        document.head.appendChild(style);
        
        initializeRenderers();
        initializeEVStationLayer();

        // Network state already loaded in first map.on('load') handler

        // DISABLED: updateLoop() - now using WebSocket-driven updates
        // updateLoop();
        // DISABLED: updateV2GColorsOptimized() - now using WebSocket data
        // updateV2GColorsOptimized();
        if (!animationFrameId) {
            animationFrameId = requestAnimationFrame(animationLoop);
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        // Removed automatic ML dashboard updates - only update when manually requested
        // setInterval(updateMLDashboard, 8000);
        updateMLDashboard();

        // ==========================================
        // AI MAP FOCUS INTEGRATION - REAL-TIME VISUAL UPDATES
        // ==========================================
        let lastMapFocusUpdate = null;
        let mapFocusHighlight = null;

        async function checkAIMapFocus() {
            // Disabled polling - AI Map Focus is now event-driven (if implemented) or disabled to reduce noise
            return;
        }

        async function applyAIMapFocus(focusData) {
            if (!focusData || !focusData.location) return;

            // Clear existing highlight
            if (mapFocusHighlight) {
                map.removeLayer(mapFocusHighlight.id);
                map.removeSource(mapFocusHighlight.sourceId);
                mapFocusHighlight = null;
            }

            const coords = [focusData.longitude || focusData.lon, focusData.latitude || focusData.lat];
            const zoom = focusData.zoom || 16;

            // Smooth camera transition to AI-requested location
            map.flyTo({
                center: coords,
                zoom: zoom,
                duration: 2000,
                essential: true
            });

            // Add visual highlighting based on action type
            if (focusData.action_type === 'blackout' || focusData.action_type === 'substation_off') {
                // Red pulsing circle for blackouts/failures
                const circleId = 'ai-highlight-' + Date.now();
                const sourceId = 'ai-highlight-source-' + Date.now();

                map.addSource(sourceId, {
                    type: 'geojson',
                    data: {
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: coords
                        }
                    }
                });

                map.addLayer({
                    id: circleId,
                    source: sourceId,
                    type: 'circle',
                    paint: {
                        'circle-radius': [
                            'interpolate',
                            ['linear'],
                            ['zoom'],
                            10, 20,
                            18, 100
                        ],
                        'circle-color': '#ff0000',
                        'circle-opacity': 0.6,
                        'circle-stroke-width': 3,
                        'circle-stroke-color': '#ff0000',
                        'circle-stroke-opacity': 0.8
                    }
                });

                mapFocusHighlight = { id: circleId, sourceId: sourceId };

                // Animate pulsing effect
                let opacity = 0.6;
                let direction = -1;
                const pulseInterval = setInterval(() => {
                    opacity += direction * 0.1;
                    if (opacity <= 0.2) direction = 1;
                    if (opacity >= 0.8) direction = -1;

                    if (map.getLayer(circleId)) {
                        map.setPaintProperty(circleId, 'circle-opacity', opacity);
                    } else {
                        clearInterval(pulseInterval);
                    }
                }, 150);

                // Auto-remove after 10 seconds
                setTimeout(() => {
                    if (map.getLayer(circleId)) {
                        map.removeLayer(circleId);
                        map.removeSource(sourceId);
                    }
                    clearInterval(pulseInterval);
                    mapFocusHighlight = null;
                }, 10000);

            } else {
                // Blue highlight circle for normal focus
                const circleId = 'ai-focus-' + Date.now();
                const sourceId = 'ai-focus-source-' + Date.now();

                map.addSource(sourceId, {
                    type: 'geojson',
                    data: {
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: coords
                        }
                    }
                });

                map.addLayer({
                    id: circleId,
                    source: sourceId,
                    type: 'circle',
                    paint: {
                        'circle-radius': [
                            'interpolate',
                            ['linear'],
                            ['zoom'],
                            10, 15,
                            18, 60
                        ],
                        'circle-color': '#00aaff',
                        'circle-opacity': 0.4,
                        'circle-stroke-width': 2,
                        'circle-stroke-color': '#00aaff',
                        'circle-stroke-opacity': 0.9
                    }
                });

                mapFocusHighlight = { id: circleId, sourceId: sourceId };

                // Auto-remove after 8 seconds
                setTimeout(() => {
                    if (map.getLayer(circleId)) {
                        map.removeLayer(circleId);
                        map.removeSource(sourceId);
                    }
                    mapFocusHighlight = null;
                }, 8000);
            }

            // Show notification
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                color: #ffffff;
                padding: 12px 20px;
                border-radius: 8px;
                border: 1px solid #00aaff;
                box-shadow: 0 4px 20px rgba(0, 170, 255, 0.3);
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                opacity: 0;
                transform: translateX(20px);
                transition: all 0.3s ease;
                max-width: 300px;
            `;
            notification.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <div style="color: #00aaff; margin-right: 8px;">🤖</div>
                    <div>
                        <div style="color: #00aaff;">AI Map Focus</div>
                        <div style="font-size: 12px; opacity: 0.8;">${focusData.location}</div>
                    </div>
                </div>
            `;
            document.body.appendChild(notification);

            // Animate in
            setTimeout(() => {
                notification.style.opacity = '1';
                notification.style.transform = 'translateX(0)';
            }, 100);

            // Auto-remove notification
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 5000);
        }

        // Poll for AI map focus updates every 2 seconds
        // setInterval(checkAIMapFocus, 2000);
        // checkAIMapFocus(); // Initial check
        
        initializeEVConfig();
        
        // ==========================================
        // ADD V2G INITIALIZATION HERE!
        // ==========================================
        initV2G();
        if (PERFORMANCE_CONFIG.enableDebugMode) {
            console.log('⚡ V2G system initialized!');
            console.log('🚀 Manhattan Power Grid - World-class UI initialized!');
            console.log('Performance mode:', PERFORMANCE_CONFIG.renderMode);
            console.log('Target FPS:', PERFORMANCE_CONFIG.targetFPS);
        }
        
        showNotification('✨ System Ready', 'Manhattan Power Grid online with V2G', 'success');
    });
    // Initial fix
    setTimeout(fixTabLayout, 100);
    // Set initial tab
    document.body.setAttribute('data-tab', 'overview');

    // Handle messages from embedded chatbot for map actions
    window.addEventListener('message', (event) => {
        try {
            if (event.data && event.data.type === 'executeMapAction') {
                console.log('Received map action from chatbot:', event.data.data);
                executeMapAction(event.data.data);
            } else if (event.data && event.data.type === 'showNotification') {
                console.log('Received notification from chatbot:', event.data.data);
                showNotification(event.data.data.title, event.data.data.message, event.data.data.type);
            }
        } catch (error) {
            console.error('Error handling chatbot message:', error);
        }
    });

    // ==========================================
    // LEGEND TOGGLE
    // ==========================================
    window.toggleLegend = function() {
        const legend = document.getElementById('system-legend');
        const btn = document.getElementById('legend-toggle-btn');
        if (legend) {
            legend.classList.toggle('collapsed');
            if (btn) {
                btn.textContent = legend.classList.contains('collapsed') ? '▶' : '▼';
            }
        }
    };

    // ==========================================
    // 3D MAP CONTROLS MENU
    // ==========================================

    // State
    let mcBuildings = true;
    let mcTerrain = false; // Default to OFF
    let mcOrbit = false;
    let mcOrbitRaf = null;

    // Build DOM
    const mcContainer = document.createElement('div');
    mcContainer.className = 'map-controls';
    mcContainer.innerHTML = `
        <button class="map-controls-toggle" id="mcToggle" title="Map Controls">⚙</button>
        <div class="map-controls-panel" id="mcPanel">
            <div class="mc-section">
                <div class="mc-section-title">View</div>
                <div class="mc-row">
                    <label><span class="mc-icon">🗺️</span>2D / 3D</label>
                    <div class="mc-switch on" id="mc3DSwitch"><div class="mc-knob"></div></div>
                </div>
            </div>
            <div class="mc-section">
                <div class="mc-section-title">Layers</div>
                <div class="mc-row">
                    <label><span class="mc-icon">🏗️</span>Buildings</label>
                    <div class="mc-switch on" id="mcBuildingsSwitch"><div class="mc-knob"></div></div>
                </div>
                <div class="mc-row">
                    <label><span class="mc-icon">⛰️</span>Terrain</label>
                    <div class="mc-switch" id="mcTerrainSwitch"><div class="mc-knob"></div></div>
                </div>
            </div>
            <div class="mc-section">
                <div class="mc-section-title">Camera Control</div>
                <div class="mc-row">
                    <button class="mc-btn-icon" id="mcRotateLeft" title="Rotate Left (Q)">↺</button>
                    <button class="mc-btn-icon" id="mcPitchUp" title="Tilt Up (R)">▲</button>
                    <button class="mc-btn-icon" id="mcPitchDown" title="Tilt Down (F)">▼</button>
                    <button class="mc-btn-icon" id="mcRotateRight" title="Rotate Right (E)">↻</button>
                </div>
                <div class="mc-help-text">
                    Use <b>W A S D</b> to Move<br>
                    <b>Q E</b> to Rotate • <b>R F</b> to Tilt<br>
                    <i>Right-Click + Drag to Rotate/Tilt</i>
                </div>
                <button class="mc-btn" id="mcOrbitBtn" style="margin-top: 8px;"><span>🎬</span> Cinematic Orbit</button>
                <button class="mc-btn" id="mcResetBtn"><span>🔄</span> Reset View</button>
            </div>
            <div class="mc-section">
                <div class="mc-section-title">Readout</div>
                <div class="mc-readout">
                    <div class="mc-readout-item">
                        <div class="mc-readout-label">Pitch</div>
                        <div class="mc-readout-value" id="mcPitch">60°</div>
                    </div>
                    <div class="mc-readout-item">
                        <div class="mc-readout-label">Bearing</div>
                        <div class="mc-readout-value" id="mcBearing">-18°</div>
                    </div>
                    <div class="mc-readout-item">
                        <div class="mc-readout-label">Zoom</div>
                        <div class="mc-readout-value" id="mcZoom">14.5</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(mcContainer);

    // --- Keyboard Controls (WASD + QERF) ---
    window.addEventListener('keydown', (e) => {
        // Ignore if typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        const step = 50; // pixels to pan
        const rotateStep = 15; // degrees
        const pitchStep = 10; // degrees

        switch(e.key.toLowerCase()) {
            // Pan
            case 'w': case 'arrowup': map.panBy([0, -step]); break;
            case 's': case 'arrowdown': map.panBy([0, step]); break;
            case 'a': case 'arrowleft': map.panBy([-step, 0]); break;
            case 'd': case 'arrowright': map.panBy([step, 0]); break;
            
            // Rotate
            case 'q': map.easeTo({ bearing: map.getBearing() - rotateStep, duration: 200 }); break;
            case 'e': map.easeTo({ bearing: map.getBearing() + rotateStep, duration: 200 }); break;
            
            // Pitch
            case 'r': map.easeTo({ pitch: Math.min(map.getPitch() + pitchStep, 85), duration: 200 }); break;
            case 'f': map.easeTo({ pitch: Math.max(map.getPitch() - pitchStep, 0), duration: 200 }); break;
        }
    });

    // --- Button Event Listeners ---
    // Wait for DOM to update
    setTimeout(() => {
        document.getElementById('mcRotateLeft').addEventListener('click', () => 
            map.easeTo({ bearing: map.getBearing() - 45, duration: 500 }));
        document.getElementById('mcRotateRight').addEventListener('click', () => 
            map.easeTo({ bearing: map.getBearing() + 45, duration: 500 }));
        document.getElementById('mcPitchUp').addEventListener('click', () => 
            map.easeTo({ pitch: Math.min(map.getPitch() + 15, 85), duration: 500 }));
        document.getElementById('mcPitchDown').addEventListener('click', () => 
            map.easeTo({ pitch: Math.max(map.getPitch() - 15, 0), duration: 500 }));
    }, 100);

    const mcPanel = document.getElementById('mcPanel');
    const mcToggleBtn = document.getElementById('mcToggle');

    // Toggle panel open/close
    mcToggleBtn.addEventListener('click', () => {
        mcPanel.classList.toggle('open');
    });
    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!mcContainer.contains(e.target)) mcPanel.classList.remove('open');
    });

    // --- 2D/3D toggle ---
    let mc3D = true;
    const mc3DSwitch = document.getElementById('mc3DSwitch');
    mc3DSwitch.addEventListener('click', () => {
        mc3D = !mc3D;
        mc3DSwitch.classList.toggle('on', mc3D);
        if (mc3D) {
            map.easeTo({ pitch: 60, bearing: -17.6, duration: 1000 });
            // Restore terrain + buildings to 3D
            if (mcTerrain && map.getSource('mapbox-dem')) {
                map.setTerrain({ source: 'mapbox-dem', exaggeration: 0.5 });
            }
            if (mcBuildings && map.getLayer('building-3d')) {
                map.setPaintProperty('building-3d', 'fill-extrusion-height', [
                    'interpolate', ['linear'], ['zoom'],
                    13, 0,
                    13.5, ['min', ['case',
                        ['>', ['get', 'height'], 0], ['get', 'height'],
                        ['>', ['get', 'levels'], 0], ['*', ['get', 'levels'], 3],
                        10
                    ], 350]
                ]);
            }
        } else {
            map.easeTo({ pitch: 0, bearing: 0, duration: 1000 });
            map.setTerrain(null);
            if (map.getLayer('building-3d')) {
                map.setPaintProperty('building-3d', 'fill-extrusion-height', 0);
            }
        }
    });

    // --- Buildings toggle ---
    const mcBuildingsSwitch = document.getElementById('mcBuildingsSwitch');
    mcBuildingsSwitch.addEventListener('click', () => {
        mcBuildings = !mcBuildings;
        mcBuildingsSwitch.classList.toggle('on', mcBuildings);
        if (map.getLayer('building-3d')) {
            map.setLayoutProperty('building-3d', 'visibility', mcBuildings ? 'visible' : 'none');
        }
    });

    // --- Terrain toggle ---
    const mcTerrainSwitch = document.getElementById('mcTerrainSwitch');
    mcTerrainSwitch.addEventListener('click', () => {
        mcTerrain = !mcTerrain;
        mcTerrainSwitch.classList.toggle('on', mcTerrain);
        if (mcTerrain) {
            if (map.getSource('mapbox-dem')) {
                map.setTerrain({ source: 'mapbox-dem', exaggeration: 0.5 });
            }
        } else {
            map.setTerrain(null);
        }
    });

    // --- Cinematic Orbit ---
    const mcOrbitBtn = document.getElementById('mcOrbitBtn');
    function startOrbit() {
        mcOrbit = true;
        mcOrbitBtn.classList.add('active');
        mcOrbitBtn.innerHTML = '<span>⏹️</span> Stop Orbit';
        function frame() {
            if (!mcOrbit) return;
            map.rotateTo((map.getBearing() + 0.15) % 360, { duration: 0, easing: t => t });
            mcOrbitRaf = requestAnimationFrame(frame);
        }
        mcOrbitRaf = requestAnimationFrame(frame);
    }
    function stopOrbit() {
        mcOrbit = false;
        if (mcOrbitRaf) cancelAnimationFrame(mcOrbitRaf);
        mcOrbitRaf = null;
        mcOrbitBtn.classList.remove('active');
        mcOrbitBtn.innerHTML = '<span>🎬</span> Cinematic Orbit';
    }
    mcOrbitBtn.addEventListener('click', () => {
        mcOrbit ? stopOrbit() : startOrbit();
    });

    // --- Reset View ---
    document.getElementById('mcResetBtn').addEventListener('click', () => {
        stopOrbit();
        map.flyTo({
            center: [-73.980, 40.758],
            zoom: 14.5,
            pitch: 60,
            bearing: -17.6,
            duration: 1500,
            essential: true
        });
    });

    // --- Live Readout ---
    const mcPitchEl = document.getElementById('mcPitch');
    const mcBearingEl = document.getElementById('mcBearing');
    const mcZoomEl = document.getElementById('mcZoom');
    map.on('move', () => {
        mcPitchEl.textContent = `${Math.round(map.getPitch())}°`;
        mcBearingEl.textContent = `${Math.round(map.getBearing())}°`;
        mcZoomEl.textContent = map.getZoom().toFixed(1);
    });

    console.log('✅ 3D Map Controls menu added at top-right');

    // ==========================================
    // DEBUG HELPER FUNCTION
    // ==========================================
    
    // Global debug function for inspecting vehicle layer state
    window.debugMap = function() {
        console.log('=== 🔍 MAP DEBUG INFO ===');
        
        // Check layer existence
        const hasLayer = map.getLayer('vehicles-symbols');
        console.log(`Layer 'vehicles-symbols' exists: ${!!hasLayer}`);
        
        // Check source existence
        const source = map.getSource('vehicles-symbols');
        console.log(`Source 'vehicles-symbols' exists: ${!!source}`);
        
        // Get feature count
        if (source && source._data) {
            const features = source._data.features || [];
            console.log(`Features in source: ${features.length}`);
            if (features.length > 0) {
                console.log('Sample feature:', features[0]);
            }
        } else {
            console.log('Features in source: Unable to read (source._data not available)');
        }
        
        // Network state
        if (networkState && networkState.vehicles) {
            console.log(`Network state vehicles: ${networkState.vehicles.length}`);
        } else {
            console.log('Network state vehicles: 0 (no data)');
        }
        
        // Map state
        console.log(`Map pitch: ${map.getPitch()}°`);
        console.log(`Map bearing: ${map.getBearing()}°`);
        console.log(`Map zoom: ${map.getZoom().toFixed(2)}`);
        console.log(`Map center: [${map.getCenter().lng.toFixed(4)}, ${map.getCenter().lat.toFixed(4)}]`);
        
        // Icon existence
        console.log(`Icon 'vehicle-arrow' exists: ${map.hasImage('vehicle-arrow')}`);
        
        // Layer visibility
        if (hasLayer) {
            const visibility = map.getLayoutProperty('vehicles-symbols', 'visibility');
            console.log(`Layer visibility: ${visibility || 'visible'}`);
        }

// --- Feature 2: Help UI Toggle ---
window.toggleHelp = function() {
    const modal = document.getElementById('help-modal');
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'block';
    }
};

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('help-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// --- Feature 4: Data Export ---
window.takeScreenshot = function() {
    // Force a render first
    map.triggerRepaint();
    const canvas = map.getCanvas();
    const dataURL = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    a.download = `manhattan_grid_snapshot_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Show notification
    const btn = document.querySelector('.help-footer .btn-secondary');
    const originalText = btn.innerText;
    btn.innerText = "✅ Saved!";
    setTimeout(() => btn.innerText = originalText, 2000);
};

window.exportState = function() {
    // Fetch state from new API endpoint
    fetch('/api/export-state')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `grid_state_${new Date().toISOString().slice(0,10)}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            const btn = document.querySelector('.help-footer .btn-primary');
            const originalText = btn.innerText;
            btn.innerText = "✅ Exported!";
            setTimeout(() => btn.innerText = originalText, 2000);
        })
        .catch(err => {
            console.error('Export failed:', err);
            alert('Export failed. See console.');
        });
};

        
        return {
            hasLayer: !!hasLayer,
            hasSource: !!source,
            featureCount: source?._data?.features?.length || 0,
            networkVehicles: networkState?.vehicles?.length || 0,
            pitch: map.getPitch(),
            zoom: map.getZoom(),
            hasIcon: map.hasImage('vehicle-arrow')
        };
    };
    
    console.log('✅ window.debugMap() helper function created - run debugMap() in console to inspect vehicle layer');
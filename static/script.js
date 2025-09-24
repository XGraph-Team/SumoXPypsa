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
    // PERFORMANCE CONFIGURATION FOR HIGH-END HARDWARE
    // ==========================================
    const PERFORMANCE_CONFIG = {
        renderMode: 'webgl',
        targetFPS: 240,
        dataUpdateRate: 120,
        interpolationSteps: 2,
        useWebWorkers: true,
        useGPUAcceleration: true,
        vehiclePoolSize: 5000,
        enableAdvancedEffects: false,
        enablePrediction: false,
        smoothingFactor: 0.85,
        enableDebugMode: window.location.hash === '#debug'
    };

    // ==========================================
    // MAPBOX INITIALIZATION WITH PREMIUM SETTINGS
    // ==========================================
    mapboxgl.accessToken = 'pk.eyJ1IjoibWFyb25veCIsImEiOiJjbWV1ODE5bHEwNGhoMmlvY2RleW51dWozIn0.FMrYdXLqnOwOEFi8qHSwxg';

    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [-73.980, 40.758],
        zoom: 14.5,
        pitch: 0,
        bearing: 0,
        antialias: true,
        preserveDrawingBuffer: PERFORMANCE_CONFIG.enableDebugMode,
        refreshExpiredTiles: false,
        fadeDuration: 0,
        maxZoom: 20,
        minZoom: 10
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
                            // Moderate size that scales nicely with zoom
                            float baseSize = 2.2;
                            float zoomFactor = smoothstep(12.0, 18.0, u_zoom);
                            float size = a_scale * baseSize * (1.0 + zoomFactor * 0.3);
                            
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
                            
                            this.arrays.scales[idx] = (vehicle.scale || 1) * 1.05;
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
            gl.bufferData(gl.ARRAY_BUFFER, data.subarray(0, count * size), gl.DYNAMIC_DRAW);
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
                        scale: 0,
                        targetScale: 1,
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
                        scale: 0,
                        targetScale: 1,
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
                            vehicle.angle = Math.atan2(dy, dx);
                        }
                    }
                    
                    vehicle.data = data;
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
                
                const easeInOutCubic = (t) => {
                    return t < 0.5 
                        ? 4 * t * t * t 
                        : 1 - Math.pow(-2 * t + 2, 3) / 2;
                };
                
                const easedProgress = easeInOutCubic(vehicle.interpolationProgress);
                
                vehicle.currentLon = vehicle.previousLon + 
                    (vehicle.targetLon - vehicle.previousLon) * easedProgress;
                vehicle.currentLat = vehicle.previousLat + 
                    (vehicle.targetLat - vehicle.previousLat) * easedProgress;
                
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
            }
            
           if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
                if (!this.map.getLayer('vehicle-webgl-layer')) {
                    this.map.addLayer(this.customLayer);
                }
            }
        }
        
        getColor(data) {
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
    let layers = {
        lights: true,
        vehicles: true,
        primary: true,
        secondary: true,
        ev: true
    };
    let sumoRunning = false;

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
                
                if (PERFORMANCE_CONFIG.enableDebugMode) {
                    this.updateDebugDisplay();
                }
            }
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
        
        async fetchData() {
            if (this.fetching) return this.cache;
            
            const now = performance.now();
            if (this.cache && now - this.lastFetch < PERFORMANCE_CONFIG.dataUpdateRate) {
                return this.cache;
            }
            
            this.fetching = true;
            try {
                const response = await fetch('/api/network_state');
                const data = await response.json();
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
    // MAIN LOOPS
    // ==========================================
    async function updateLoop() {
        try {
            const response = await fetch('/api/network_state', { cache: 'no-store' });
            const data = await response.json();
            
            if (data) {
                networkState = data;
                updateUI();
                
                if (data.vehicles && layers.vehicles && vehicleRenderer) {
                    // WebGL renderer handles vehicle positions efficiently
                    vehicleRenderer.updateVehicles(data.vehicles);
                }
                
                // Decimate heavier layers for smoothness
                _uiLoopCounter = (_uiLoopCounter + 1) % UI_DECIMATION_FACTOR;
                if (_uiLoopCounter === 0) {
                    renderNetwork();
                    renderEVStations();
                    renderVehicleClicks();
                }
                updateVehicleSymbolLayer();
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        
        setTimeout(updateLoop, PERFORMANCE_CONFIG.dataUpdateRate);
    }

    let lastAnimationTime = performance.now();
    let animationFrameId = null;

    function animationLoop(currentTime) {
        const deltaTime = currentTime - lastAnimationTime;
        lastAnimationTime = currentTime;
        
        const cappedDeltaTime = Math.min(deltaTime, 50);
        
        if (vehicleRenderer && layers.vehicles) {
            vehicleRenderer.interpolate(cappedDeltaTime);
        }
        
        performanceMonitor.update();
        
        animationFrameId = requestAnimationFrame(animationLoop);
    }

    // ==========================================
    // UI UPDATES WITH SMOOTH ANIMATIONS
    // ==========================================
    function updateUI() {
        if (!networkState) return;
        
        requestAnimationFrame(() => {
            const stats = networkState.statistics;
            
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
                'legend-red': stats.red_lights || 0
            };
            
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
                updateWithAnimation('active-vehicles', active);
                updateWithAnimation('ev-count', networkState.vehicle_stats.ev_vehicles || 0);
                updateWithAnimation('vehicle-count', active);
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
        if (PERFORMANCE_CONFIG.renderMode === 'webgl') {
            vehicleRenderer = new WebGLVehicleRenderer(map);
        } else {
            vehicleRenderer = new HybridVehicleRenderer(map);
        }
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
        if (!map.getSource('vehicles-symbols')) {
            map.addSource('vehicles-symbols', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }});
        }
        if (!map.getLayer('vehicles-symbols')) {
            map.addLayer({
                id: 'vehicles-symbols',
                type: 'symbol',
                source: 'vehicles-symbols',
                layout: {
                    'text-field': '⬤',
                    'text-size': [
                        'interpolate', ['linear'], ['zoom'],
                        12, 18,
                        14, 24,
                        16, 30,
                        18, 36
                    ],
                    'text-allow-overlap': true,
                    'text-ignore-placement': true
                },
                paint: {
                    'text-color': [
                        'case', 
                        ['get', 'is_stranded'], '#ff00ff',
                        ['get', 'is_charging'], '#00ffff',
                        ['get', 'is_queued'], '#ffff00',
                        ['to-boolean', ['get', 'is_ev']], '#00ff88',
                        '#6464ff'
                    ],
                    'text-halo-color': '#000000',
                    'text-halo-width': 3,
                    'text-halo-blur': 1.5
                }
            });
        }
        try { map.moveLayer('vehicles-symbols'); } catch (e) {}
    }

    function updateVehicleSymbolLayer() {
        const src = map.getSource('vehicles-symbols');
        if (!src || !networkState || !networkState.vehicles) return;
        const now = performance.now();
        const total = networkState.vehicles.length;
        // Skip or thin symbol layer when WebGL is active and vehicle count is high
        if (PERFORMANCE_CONFIG.renderMode === 'webgl' && total > VEHICLE_SYMBOL_THRESHOLD && !PERFORMANCE_CONFIG.enableDebugMode) {
            if (now - _lastVehicleSymbolUpdate < VEHICLE_SYMBOL_UPDATE_MS) return;
        }
        _lastVehicleSymbolUpdate = now;

        // Thin sampling to cap symbol features for Mapbox
        let stride = 1;
        if (PERFORMANCE_CONFIG.renderMode === 'webgl' && total > VEHICLE_SYMBOL_THRESHOLD) {
            stride = Math.ceil(total / VEHICLE_SYMBOL_THRESHOLD);
        }

        const features = networkState.vehicles.filter((_, idx) => (idx % stride) === 0).map(v => ({
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
        
        // Premium substations visualization
        const substationFeatures = networkState.substations.map(sub => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [sub.lon, sub.lat] },
            properties: {
                name: sub.name,
                capacity_mva: sub.capacity_mva,
                load_mw: sub.load_mw,
                operational: !!sub.operational,
                coverage_area: sub.coverage_area,
                color: sub.operational ? '#ff0066' : '#666666'
            }
        }));
        
        if (!substationLayerInitialized && map.loaded()) {
            if (!map.getSource('substations')) {
                map.addSource('substations', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }});
            }
            if (!map.getLayer('substations-layer')) {
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
                        'text-ignore-placement': true
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
                        'text-ignore-placement': true
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
                        geometry: { type: 'LineString', coordinates: cable.path },
                        properties: { operational: cable.operational }
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
                        geometry: { type: 'LineString', coordinates: cable.path },
                        properties: { operational: cable.operational, substation: cable.substation || 'unknown' }
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
                    paint: {
                        'circle-radius': ['interpolate', ['linear'], ['zoom'], 12, 3, 14, 4, 16, 6],
                        'circle-color': ['get', 'color'],
                        'circle-opacity': 0.95,
                        'circle-stroke-width': 1,
                        'circle-stroke-color': '#ffffff',
                        'circle-stroke-opacity': 0.5,
                        'circle-blur': 0.2
                    }
                });
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
            sumoRunning = true;
            document.getElementById('start-sumo-btn').disabled = true;
            document.getElementById('stop-sumo-btn').disabled = false;
            document.getElementById('spawn10-btn').disabled = false;
            showNotification('✅ Vehicles Started', result.message, 'success');
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
            sumoRunning = false;
            document.getElementById('start-sumo-btn').disabled = false;
            document.getElementById('stop-sumo-btn').disabled = true;
            document.getElementById('spawn10-btn').disabled = true;
            
            if (vehicleRenderer) {
                vehicleRenderer.clear();
            }
            showNotification('⏹️ Vehicles Stopped', 'Simulation halted', 'info');
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
        
        await loadNetworkState();
    }

    async function restoreAll() {
        await fetch('/api/restore_all', { method: 'POST' });
        await loadNetworkState();
        showNotification('🔧 System Restored', 'All substations back online', 'success');
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

    async function loadNetworkState() {
        try {
            const response = await fetch('/api/network_state');
            networkState = await response.json();
            updateUI();
            renderNetwork();
            if (layers.vehicles && vehicleRenderer && networkState.vehicles) {
                vehicleRenderer.updateVehicles(networkState.vehicles);
            }
            renderEVStations();
            updateVehicleSymbolLayer();
        } catch (error) {
            console.error('Error loading network state:', error);
        }
    }

    function toggleLayer(layer) {
        layers[layer] = !layers[layer];
        
        const layerMappings = {
            'lights': ['traffic-lights'],
            'primary': ['primary-cables', 'primary-cables-glow'],
            'secondary': ['secondary-cables', 'secondary-cables-glow'],
            'vehicles': ['vehicle-webgl-layer', 'vehicles-symbols', 'vehicles-click-layer'],
            'ev': ['ev-stations-layer', 'ev-stations-badge-bg', 'ev-stations-badge-text', 'ev-stations-icon']
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

    function updateTime() {
        const now = new Date();
        document.getElementById('time').textContent = 
            now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
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
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            background: ${colors[type]};
            color: rgba(0, 0, 0, 0.9);
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            z-index: 10000;
            max-width: 320px;
            animation: slideInRight 0.3s ease;
            font-weight: 500;
        `;
        notification.innerHTML = `<strong>${title}</strong><br>${message}`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
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
        box.innerHTML = '<div class="typing">Loading latest insights…</div>';
        try {
            const resp = await fetch('/api/ai/advice');
            const data = await resp.json();
            if (data.advice) {
                box.innerHTML = `<div class="msg ai" style="padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;color:var(--text-secondary);">${data.advice.replace(/\\n/g,'<br>')}</div>`;
            } else {
                box.innerHTML = `<div style="color:#ff6b6b;">${data.error||'No response'}</div>`;
            }
        } catch(e) {
            box.innerHTML = '<div style="color:#ff6b6b;">AI request failed.</div>';
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
    // CHATBOT FUNCTIONS
    // ==========================================
    function toggleChatbot() {
        const launcher = document.getElementById('chatbot-launcher');
        const win = document.getElementById('chatbot-window');
        if (win.style.display === 'flex') {
            win.style.display = 'none';
            launcher.style.display = 'flex';
        } else {
            win.style.display = 'flex';
            launcher.style.display = 'none';
            const box = document.getElementById('chat-messages');
            box.innerHTML = '<div class="msg ai">Loading system status…</div>';
            fetch('/api/ai/advice').then(r=>r.json()).then(data=>{
                if (data.advice) {
                    box.innerHTML = `<div class="msg ai" style="padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;">${data.advice.replace(/\\n/g,'<br>')}</div>`;
                } else {
                    box.innerHTML = `<div class="msg ai" style="color:#ff6b6b;">${data.error||'No response'}</div>`;
                }
            }).catch(()=>{
                box.innerHTML = '<div class="msg ai" style="color:#ff6b6b;">AI request failed.</div>';
            });
        }
    }

    function handleChatKeyPress(event) {
        if (event.key === 'Enter') {
            sendChatMessage();
        }
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
        const box = document.getElementById('chat-messages');
        box.innerHTML += `<div class="msg user" style="margin:8px 0;padding:10px;background:linear-gradient(135deg,rgba(0,170,255,0.1),rgba(0,120,255,0.05));border-radius:10px;border:1px solid rgba(0,170,255,0.2);"><strong>You:</strong> ${text}</div>`;
        box.innerHTML += `<div class="typing">AI is typing…</div>`;
        const typingRef = box.querySelector('.typing');
        input.value = '';
        // Use the enhanced AI chat endpoint
        fetch('/api/ai/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:text, user_id:'web_user'})})
        .then(r=>r.json()).then(data=>{
            if (typingRef) typingRef.remove();
            if (data.response) {
                let responseHtml = `<div class="msg ai" style="margin:8px 0;padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;border:1px solid rgba(255,255,255,0.05);">`;
                responseHtml += `<strong style="color:#c8a2ff;">AI:</strong> ${data.response.replace(/\\n/g,'<br>')}`;
                
                // Optional debug: show intent and data only in debug mode
                if (PERFORMANCE_CONFIG && PERFORMANCE_CONFIG.enableDebugMode) {
                    if (data.intent && data.intent !== 'general') {
                        responseHtml += `<div style="margin-top:8px;padding:6px;background:rgba(0,255,136,0.1);border-radius:6px;font-size:12px;color:#00ff88;">Intent: ${data.intent}</div>`;
                    }
                    if (data.data && Object.keys(data.data).length > 0) {
                        responseHtml += `<div style="margin-top:8px;padding:6px;background:rgba(200,162,255,0.1);border-radius:6px;font-size:12px;color:#c8a2ff;">Data: ${JSON.stringify(data.data, null, 2)}</div>`;
                    }
                }
                responseHtml += `</div>`;
                box.innerHTML += responseHtml;
            } else {
                box.innerHTML += `<div class="msg ai" style="color:#ff6b6b;"><strong>AI:</strong> ${data.error||'No response'}</div>`;
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
    let v2gUpdateInterval = null;

    function initV2G() {
        // Start V2G update loop
        v2gUpdateInterval = setInterval(updateV2GDashboard, 500); // Update every 500ms for smooth real-time
        updateV2GDashboard();
    }

    async function updateV2GDashboard() {
        try {
            const response = await fetch('/api/v2g/status');
            const data = await response.json();
            

            // Update metrics with animation
            updateWithAnimation('v2g-active-sessions', data.active_sessions);
            updateWithAnimation('v2g-power', data.total_power_kw);
            updateWithAnimation('v2g-vehicles', data.vehicles_participated);
            updateWithAnimation('v2g-rate', `$${data.current_rate.toFixed(2)}`);
            
            // Animate earnings with counting effect
            const earningsEl = document.getElementById('v2g-earnings');
            if (earningsEl) {
                const currentVal = parseFloat(earningsEl.textContent.replace('$', '') || 0);
                const newVal = data.total_earnings;
                if (Math.abs(currentVal - newVal) > 0.01) {
                    animateValue(earningsEl, currentVal, newVal, 500, '$');
                }
            }
            
            // Update substation list with REAL-TIME power needs
            await updateV2GSubstationList();
            
            // Update active sessions with REAL-TIME data
            const sessionList = document.getElementById('v2g-session-list');
            if (data.active_vehicles && data.active_vehicles.length > 0) {
                sessionList.innerHTML = data.active_vehicles.map(v => {
                    // Calculate real-time progress
                    const progress = ((v.power_delivered || 0) / (v.min_energy_required || 10)) * 100;
                    const progressBar = `
                        <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 4px;">
                            <div style="width: ${Math.min(progress, 100)}%; height: 100%; background: linear-gradient(90deg, #00ffff, #00ff88); border-radius: 2px; transition: width 0.3s;"></div>
                        </div>
                    `;
                    
                    // Calculate real power rate in kW
                    const powerRate = v.duration > 0 ? (v.power_delivered * 3600 / v.duration).toFixed(0) : '0';
                    
                    return `
                        <div class="v2g-session-item" style="animation: v2gPulse 2s ease-in-out infinite;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 20px;">🚗</span>
                                <div>
                                    <div style="font-weight: 600; color: #00ffff;">${v.vehicle_id}</div>
                                    <div style="font-size: 11px; color: var(--text-muted);">
                                        SOC: ${v.soc.toFixed(0)}% | ${v.duration}s
                                    </div>
                                </div>
                            </div>
                            <div style="flex: 1; padding: 0 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 12px; color: #00ff88;">
                                        💵 $${v.earnings.toFixed(2)}
                                    </span>
                                    <span style="font-size: 11px; color: var(--text-muted);">
                                        ${v.power_delivered.toFixed(2)} kWh
                                    </span>
                                </div>
                                ${progressBar}
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
            
        } catch (error) {
            console.error('Error updating V2G dashboard:', error);
        }
    }

    async function updateV2GSubstationList() {
        // Get current network state to find failed substations
        const response = await fetch('/api/network_state');
        const networkState = await response.json();
        
        const v2gResponse = await fetch('/api/v2g/status');
        const v2gData = await v2gResponse.json();
        
        const failedSubstations = networkState.substations.filter(s => !s.operational);

        
        const listElement = document.getElementById('v2g-substation-list');
        
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
        
        updateLoop();
        if (!animationFrameId) {
            animationFrameId = requestAnimationFrame(animationLoop);
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        setInterval(updateMLDashboard, 8000);
        updateMLDashboard();
        
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

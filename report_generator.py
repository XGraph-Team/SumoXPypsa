"""
Manhattan Power Grid — Comprehensive PDF Report Generator

Generates a professional multi-section PDF report with:
  1. Executive Summary with key KPIs
  2. Grid Status — per-substation table
  3. Traffic & EV — vehicle breakdown and EV station utilization
  4. V2G Operations — sessions, power flow, earnings
  5. Cable Network integrity
  6. KPIs Dashboard
  7. AI-Powered Detailed Analysis (OpenAI / local LLM, with rule-based fallback)
  8. Optional embedded map screenshot
"""

from fpdf import FPDF
from datetime import datetime
import base64
import json
import os
import tempfile
import textwrap

# ---------------------------------------------------------------------------
# Color palette (RGB tuples)
# ---------------------------------------------------------------------------
CLR_HEADER_BG = (15, 23, 42)        # Dark navy
CLR_HEADER_FG = (255, 255, 255)     # White
CLR_SECTION_BG = (30, 41, 59)       # Slate-800
CLR_SECTION_FG = (148, 163, 184)    # Slate-400
CLR_ACCENT = (0, 255, 136)          # Green accent
CLR_BLACK = (0, 0, 0)
CLR_WHITE = (255, 255, 255)
CLR_GOOD = (34, 197, 94)            # Green-500
CLR_WARN = (234, 179, 8)            # Yellow-500
CLR_BAD = (239, 68, 68)             # Red-500
CLR_TABLE_HEAD = (51, 65, 85)       # Slate-700
CLR_TABLE_ROW1 = (241, 245, 249)    # Slate-100
CLR_TABLE_ROW2 = (255, 255, 255)    # White
CLR_MUTED = (100, 116, 139)         # Slate-500


def _safe(val, decimals=2):
    """Safely format a numeric value."""
    if val is None:
        return "N/A"
    try:
        return f"{float(val):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)


def _sanitize(text: str) -> str:
    """Replace Unicode characters unsupported by built-in PDF fonts (latin-1)."""
    replacements = {
        '\u2014': '--',   # em dash
        '\u2013': '-',    # en dash
        '\u2018': "'",    # left single quote
        '\u2019': "'",    # right single quote
        '\u201c': '"',    # left double quote
        '\u201d': '"',    # right double quote
        '\u2026': '...',  # ellipsis
        '\u2022': '*',    # bullet
        '\u00b0': ' deg', # degree sign
        '\u2192': '->',   # right arrow
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Fallback: encode to latin-1, replacing unknown chars
    return text.encode('latin-1', errors='replace').decode('latin-1')


# ---------------------------------------------------------------------------
# AI Analysis helper
# ---------------------------------------------------------------------------
def _generate_ai_analysis(state: dict) -> str:
    """Call OpenAI (or local compatible API) to generate a detailed analysis.
    Falls back to rule-based summary if the API is unavailable."""

    # Build a concise data summary for the LLM (avoid sending huge arrays)
    stats = state.get('statistics', {})
    kpis = state.get('kpis', {})
    v2g = state.get('v2g', {})
    v_stats = state.get('vehicle_stats', {})
    scenario = state.get('scenario', {})
    subs = state.get('substations', [])

    data_summary = {
        "grid": {
            "total_load_mw": stats.get('total_load_mw', 0),
            "substations_online": f"{stats.get('operational_substations', 0)}/{stats.get('total_substations', 0)}",
            "offline_substations": [s['name'] for s in subs if not s.get('operational')],
            "capacity_utilization_pct": kpis.get('capacity_utilization_pct', 0),
            "grid_health_pct": kpis.get('grid_health_pct', 100),
            "cable_integrity_pct": kpis.get('cable_integrity_pct', 100),
        },
        "traffic": {
            "total_vehicles": v_stats.get('active_vehicles', 0),
            "ev_count": v_stats.get('ev_vehicles', 0),
            "avg_speed_kmh": round((v_stats.get('avg_speed_mps', 0) or 0) * 3.6, 1),
            "vehicles_charging": v_stats.get('vehicles_charging', 0),
            "vehicles_stranded": v_stats.get('vehicles_stranded', 0),
        },
        "v2g": {
            "active_sessions": v2g.get('active_sessions_count', 0),
            "total_power_kw": v2g.get('total_power_kw', 0),
            "total_earnings_usd": v2g.get('total_earnings', 0),
            "total_kwh_provided": v2g.get('total_kwh_provided', 0),
        },
        "scenario": {
            "temperature_f": scenario.get('temperature_f'),
            "time_description": scenario.get('time_description'),
            "weather": scenario.get('weather'),
        },
        "kpis": kpis,
    }

    system_prompt = textwrap.dedent("""\
        You are an expert power-grid analyst for the Manhattan Power Grid simulation.
        Given the JSON data below, write a concise (300-500 word) professional analysis covering:
        1. Executive Assessment — overall grid health in plain language
        2. Risk Factors — any substations offline, low cable integrity, stranded vehicles
        3. V2G Impact — how vehicle-to-grid is contributing to resilience
        4. Recommendations — 3-5 actionable items to improve the situation
        Be specific, cite numbers from the data, and keep the tone professional.
        Do NOT use markdown formatting — output plain text with numbered sections.""")

    user_prompt = f"Current Manhattan Grid State:\n{json.dumps(data_summary, indent=2)}"

    try:
        from openai import OpenAI
    except ImportError:
        return _rule_based_analysis(state)

    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model = os.getenv('LLM_MODEL', '')

    client = None
    if base_url:
        client = OpenAI(base_url=base_url, api_key=api_key or "local")
        if not model:
            try:
                models = client.models.list()
                model = models.data[0].id if models.data else "default"
            except Exception:
                model = "default"
    elif api_key:
        client = OpenAI(api_key=api_key)
        if not model:
            model = "gpt-4o"

    if not client:
        return _rule_based_analysis(state)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[REPORT] AI analysis failed ({e}), using rule-based fallback")
        return _rule_based_analysis(state)


def _rule_based_analysis(state: dict) -> str:
    """Generate a deterministic analysis when LLM is unavailable."""
    stats = state.get('statistics', {})
    kpis = state.get('kpis', {})
    v2g = state.get('v2g', {})
    v_stats = state.get('vehicle_stats', {})
    subs = state.get('substations', [])

    offline = [s['name'] for s in subs if not s.get('operational')]
    health = kpis.get('grid_health_pct', 100)
    util = kpis.get('capacity_utilization_pct', 0)
    cable = kpis.get('cable_integrity_pct', 100)

    lines = []
    lines.append("1. EXECUTIVE ASSESSMENT")
    if health >= 100:
        lines.append(f"   All substations are operational. Grid health is at {health}%.")
    else:
        lines.append(f"   Grid health is at {health}%. {len(offline)} substation(s) offline: {', '.join(offline)}.")

    lines.append(f"   Total load: {_safe(stats.get('total_load_mw', 0))} MW at {util}% capacity utilization.")
    lines.append(f"   Cable network integrity: {cable}%.")

    lines.append("")
    lines.append("2. RISK FACTORS")
    risks = []
    if offline:
        risks.append(f"- Substations offline ({', '.join(offline)}) - reduced redundancy.")
    if util > 80:
        risks.append(f"- High capacity utilization ({util}%) - approaching thermal limits.")
    if v_stats.get('vehicles_stranded', 0) > 0:
        risks.append(f"- {v_stats['vehicles_stranded']} EV(s) stranded due to depleted batteries.")
    if cable < 95:
        risks.append(f"- Cable integrity below target ({cable}%).")
    if not risks:
        risks.append("- No critical risk factors identified at this time.")
    lines.extend(risks)

    lines.append("")
    lines.append("3. V2G IMPACT")
    active = v2g.get('active_sessions_count', 0)
    power = v2g.get('total_power_kw', 0)
    kwh = v2g.get('total_kwh_provided', 0)
    if active > 0:
        lines.append(f"   {active} V2G session(s) active, providing {_safe(power, 1)} kW of power.")
        lines.append(f"   Total energy delivered: {_safe(kwh)} kWh. Total earnings: ${_safe(v2g.get('total_earnings', 0))}.")
        if offline:
            lines.append("   V2G is actively compensating for offline substation(s).")
    else:
        lines.append("   No active V2G sessions. Grid is operating on conventional supply only.")

    lines.append("")
    lines.append("4. RECOMMENDATIONS")
    recs = []
    if offline:
        recs.append("- Prioritize restoration of offline substation(s) to improve redundancy.")
    if util > 70:
        recs.append("- Consider load shedding or activating additional V2G capacity.")
    if v_stats.get('vehicles_stranded', 0) > 0:
        recs.append("- Deploy mobile charging units for stranded EVs.")
    if active == 0 and len(offline) > 0:
        recs.append("- Activate V2G program to leverage EV batteries for grid support.")
    recs.append("- Continue monitoring real-time KPIs for emerging issues.")
    if not recs:
        recs.append("- System operating normally. Maintain current configuration.")
    lines.extend(recs)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main Report Generator
# ---------------------------------------------------------------------------
class ReportGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    # ------------------------------------------------------------------
    # Header / Footer
    # ------------------------------------------------------------------
    def header(self):
        self.set_fill_color(*CLR_HEADER_BG)
        self.rect(0, 0, 210, 28, 'F')
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(*CLR_WHITE)
        self.set_y(6)
        self.cell(0, 10, 'Manhattan Power Grid - System Report', align='C', ln=True)
        self.set_font('helvetica', '', 9)
        self.set_text_color(*CLR_SECTION_FG)
        self.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', align='C', ln=True)
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font('helvetica', 'I', 7)
        self.set_text_color(*CLR_MUTED)
        self.cell(0, 8, f'Manhattan Grid Control  |  Page {self.page_no()}/{{nb}}', align='C')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _section_title(self, title: str):
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(*CLR_BLACK)
        self.set_fill_color(*CLR_TABLE_ROW1)
        self.cell(0, 9, _sanitize(f'  {title}'), ln=True, fill=True)
        self.ln(2)

    def _kv(self, key: str, value, w_key=70, w_val=80):
        self.set_font('helvetica', '', 10)
        self.set_text_color(*CLR_MUTED)
        self.cell(w_key, 6, _sanitize(key), ln=False)
        self.set_text_color(*CLR_BLACK)
        self.set_font('helvetica', 'B', 10)
        self.cell(w_val, 6, _sanitize(str(value)), ln=True)

    def _table(self, headers: list, rows: list, col_widths: list = None):
        """Draw a simple table with alternating row colors."""
        n = len(headers)
        if not col_widths:
            avail = self.w - self.l_margin - self.r_margin
            col_widths = [avail / n] * n

        # Header row
        self.set_font('helvetica', 'B', 9)
        self.set_fill_color(*CLR_TABLE_HEAD)
        self.set_text_color(*CLR_WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, _sanitize(h), border=0, fill=True, align='C')
        self.ln()

        # Data rows
        self.set_font('courier', '', 9)
        for idx, row in enumerate(rows):
            bg = CLR_TABLE_ROW1 if idx % 2 == 0 else CLR_TABLE_ROW2
            self.set_fill_color(*bg)
            self.set_text_color(*CLR_BLACK)
            for i, cell_val in enumerate(row):
                align = 'L' if i == 0 else 'C'
                self.cell(col_widths[i], 6, _sanitize(str(cell_val)), border=0, fill=True, align=align)
            self.ln()
        self.ln(3)

    def _status_dot(self, operational: bool) -> str:
        return "ONLINE" if operational else "OFFLINE"

    # ------------------------------------------------------------------
    # Main generation method
    # ------------------------------------------------------------------
    def generate_status_report(self, state: dict, notes: str = None,
                                screenshot_base64: str = None) -> str:
        self.alias_nb_pages()
        self.add_page()

        report_id = f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        stats = state.get('statistics', {})
        kpis = state.get('kpis', {})
        v2g = state.get('v2g', {})
        v_stats = state.get('vehicle_stats', {})
        scenario = state.get('scenario', {})
        subs = state.get('substations', [])
        ev_stations = state.get('ev_stations', [])

        total_load = stats.get('total_load_mw', state.get('total_load_mw', 0))
        op_subs = stats.get('operational_substations', sum(1 for s in subs if s.get('operational')))
        total_subs = stats.get('total_substations', len(subs))

        # ── Report ID & simulation time ──────────────────────────────
        self.set_font('helvetica', '', 9)
        self.set_text_color(*CLR_MUTED)
        sim_time = scenario.get('time_formatted', 'N/A')
        temp = scenario.get('temperature_f', 'N/A')
        desc = scenario.get('time_description', '')
        self.cell(0, 5, _sanitize(f'Report ID: {report_id}   |   Simulation Time: {sim_time}   |   Temp: {temp} F   |   {desc}'), ln=True)
        self.ln(2)

        # ── User notes ───────────────────────────────────────────────
        if notes:
            self.set_font('helvetica', 'I', 10)
            self.set_text_color(*CLR_MUTED)
            self.multi_cell(0, 6, _sanitize(f'Notes: {notes}'))
            self.ln(3)

        # ── 1. EXECUTIVE SUMMARY ─────────────────────────────────────
        self._section_title('1. Executive Summary')
        self._kv('Total Load:', f'{_safe(total_load)} MW')
        self._kv('Substations Online:', f'{op_subs} / {total_subs}')
        self._kv('Grid Health:', f'{kpis.get("grid_health_pct", 100)}%')
        self._kv('Capacity Utilization:', f'{kpis.get("capacity_utilization_pct", 0)}%')
        self._kv('Cable Integrity:', f'{kpis.get("cable_integrity_pct", 100)}%')

        total_vehicles = v_stats.get('active_vehicles', v_stats.get('total_vehicles', 0))
        ev_count = v_stats.get('ev_vehicles', 0)
        self._kv('Active Vehicles:', f'{total_vehicles}  (EV: {ev_count})')
        self._kv('V2G Active Sessions:', f'{v2g.get("active_sessions_count", 0)}')
        self._kv('V2G Total Earnings:', f'${_safe(v2g.get("total_earnings", 0))}')
        self.ln(3)

        # ── 2. GRID STATUS - per-substation table ─────────────────────
        self._section_title('2. Grid Status - Substations')
        headers = ['Substation', 'Status', 'Load (MW)', 'Capacity (MVA)', 'Util %']
        widths = [50, 25, 30, 35, 30]
        rows = []
        for sub in subs:
            cap = sub.get('capacity_mva', 0)
            load = sub.get('load_mw', 0)
            util = round(load / cap * 100, 1) if cap else 0
            rows.append([
                sub.get('name', '?'),
                self._status_dot(sub.get('operational', False)),
                _safe(load),
                _safe(cap),
                f'{util}%'
            ])
        if rows:
            self._table(headers, rows, widths)
        else:
            self.set_font('helvetica', 'I', 10)
            self.cell(0, 6, 'No substation data available.', ln=True)
            self.ln(3)

        # ── 3. TRAFFIC & EV ──────────────────────────────────────────
        self._section_title('3. Traffic & EV Status')
        self._kv('Total Vehicles:', str(total_vehicles))
        self._kv('EV Count:', str(ev_count))
        self._kv('Gas Vehicles:', str(total_vehicles - ev_count))
        self._kv('Avg Speed:', f'{_safe((v_stats.get("avg_speed_mps", 0) or 0) * 3.6, 1)} km/h')
        self._kv('Vehicles Charging:', str(v_stats.get('vehicles_charging', 0)))
        self._kv('Vehicles Low Battery:', str(v_stats.get('vehicles_low_battery', 0)))
        self._kv('Vehicles Stranded:', str(v_stats.get('vehicles_stranded', 0)))
        self._kv('Total Energy Consumed:', f'{_safe(v_stats.get("total_energy_consumed_kwh", 0))} kWh')
        self._kv('Total Distance:', f'{_safe(v_stats.get("total_distance_km", 0))} km')
        self.ln(2)

        # EV Stations table
        if ev_stations:
            self.set_font('helvetica', 'B', 10)
            self.set_text_color(*CLR_BLACK)
            self.cell(0, 7, 'EV Charging Stations:', ln=True)
            headers_ev = ['Station', 'Status', 'Chargers', 'Charging', 'Load (kW)']
            widths_ev = [55, 25, 25, 25, 35]
            rows_ev = []
            for st in ev_stations:
                rows_ev.append([
                    st.get('name', st.get('id', '?')),
                    self._status_dot(st.get('operational', True)),
                    str(st.get('chargers', 0)),
                    str(st.get('vehicles_charging', 0)),
                    _safe(st.get('current_load_kw', 0), 1)
                ])
            self._table(headers_ev, rows_ev, widths_ev)

        # ── 4. V2G OPERATIONS ────────────────────────────────────────
        self._section_title('4. V2G Operations')
        if v2g.get('active_sessions_count', 0) > 0 or v2g.get('total_earnings', 0) > 0:
            self._kv('Active Sessions:', str(v2g.get('active_sessions_count', 0)))
            self._kv('Total Power:', f'{_safe(v2g.get("total_power_kw", 0), 1)} kW')
            self._kv('Discharge Rate:', f'{_safe(v2g.get("discharge_rate_kw", 0), 1)} kW per vehicle')
            self._kv('Total Energy Provided:', f'{_safe(v2g.get("total_kwh_provided", 0))} kWh')
            self._kv('Total Earnings:', f'${_safe(v2g.get("total_earnings", 0))}')
            self._kv('Earnings Rate:', f'${_safe(v2g.get("earnings_rate_per_hour", 0))}/hr')
            self._kv('Peak Power:', f'{_safe(v2g.get("peak_power", 0), 1)} kW')
            self._kv('Locked Vehicles:', str(v2g.get('locked_vehicles', 0)))
            self._kv('Enabled Substations:', ', '.join(v2g.get('enabled_substations', [])) or 'None')
            self._kv('Restored Substations:', ', '.join(v2g.get('restored_substations', [])) or 'None')
            self.ln(2)

            # Per-substation delivery
            energy_del = v2g.get('energy_delivered', {})
            energy_req = v2g.get('energy_required', {})
            if energy_del:
                self.set_font('helvetica', 'B', 10)
                self.cell(0, 7, 'Per-Substation V2G Delivery:', ln=True)
                headers_v = ['Substation', 'Delivered (kWh)', 'Required (kWh)', 'Progress']
                widths_v = [50, 40, 40, 35]
                rows_v = []
                for name in sorted(set(list(energy_del.keys()) + list(energy_req.keys()))):
                    d = energy_del.get(name, 0)
                    r = energy_req.get(name, 0)
                    pct = round(d / r * 100, 1) if r > 0 else 0
                    rows_v.append([name, _safe(d), _safe(r), f'{pct}%'])
                self._table(headers_v, rows_v, widths_v)
        else:
            self.set_font('helvetica', 'I', 10)
            self.set_text_color(*CLR_MUTED)
            self.cell(0, 6, 'No active V2G operations at this time.', ln=True)
            self.ln(3)

        # ── 5. CABLE NETWORK ─────────────────────────────────────────
        self._section_title('5. Cable Network Integrity')
        tp = stats.get('total_primary_cables', 0)
        op = stats.get('operational_primary_cables', 0)
        ts = stats.get('total_secondary_cables', 0)
        os_c = stats.get('operational_secondary_cables', 0)
        self._kv('Primary Cables:', f'{op} / {tp} operational')
        self._kv('Secondary Cables:', f'{os_c} / {ts} operational')
        self._kv('Overall Integrity:', f'{kpis.get("cable_integrity_pct", 100)}%')
        self.ln(3)

        # ── 6. KPIs DASHBOARD ────────────────────────────────────────
        self._section_title('6. Key Performance Indicators')
        headers_k = ['KPI', 'Value']
        widths_k = [100, 65]
        rows_k = [
            ['Capacity Utilization', f'{kpis.get("capacity_utilization_pct", 0)}%'],
            ['Grid Health', f'{kpis.get("grid_health_pct", 100)}%'],
            ['EV Adoption Rate', f'{kpis.get("ev_adoption_pct", 0)}%'],
            ['V2G Participation', f'{kpis.get("v2g_participation_pct", 0)}%'],
            ['Cable Integrity', f'{kpis.get("cable_integrity_pct", 100)}%'],
            ['Vehicles Charging', f'{kpis.get("vehicles_charging_pct", 0)}%'],
        ]
        self._table(headers_k, rows_k, widths_k)

        # ── 7. MAP SCREENSHOT (optional) ─────────────────────────────
        if screenshot_base64:
            try:
                self.add_page()
                self._section_title('7. Map View at Time of Report')
                # Decode base64 image and save to temp file
                img_data = screenshot_base64
                if ',' in img_data:
                    img_data = img_data.split(',', 1)[1]
                img_bytes = base64.b64decode(img_data)
                tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                tmp.write(img_bytes)
                tmp.close()
                # Embed in PDF — fit to page width with margin
                img_w = self.w - self.l_margin - self.r_margin
                self.image(tmp.name, x=self.l_margin, w=img_w)
                os.unlink(tmp.name)
                self.ln(5)
            except Exception as e:
                print(f"[REPORT] Could not embed screenshot: {e}")
                self.set_font('helvetica', 'I', 9)
                self.set_text_color(*CLR_MUTED)
                self.cell(0, 6, '(Map screenshot could not be embedded)', ln=True)

        # ── 8. AI-POWERED ANALYSIS ───────────────────────────────────
        self.add_page()
        section_num = '8' if screenshot_base64 else '7'
        self._section_title(f'{section_num}. Detailed Analysis (AI-Generated)')
        self.set_font('helvetica', '', 10)
        self.set_text_color(*CLR_BLACK)

        analysis = _sanitize(_generate_ai_analysis(state))
        text_w = self.w - self.l_margin - self.r_margin
        for line in analysis.split('\n'):
            if line.strip():
                self.set_x(self.l_margin)
                self.multi_cell(text_w, 5, line.strip())
            else:
                self.ln(3)
        self.ln(5)

        # ── Scenario details (footer section) ────────────────────────
        self.set_draw_color(*CLR_SECTION_FG)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(*CLR_MUTED)
        weather = scenario.get('weather', 'N/A')
        self.cell(0, 4, _sanitize(f'Scenario: {desc}  |  Weather: {weather}  |  Temperature: {temp} F'), ln=True)
        self.cell(0, 4, _sanitize(f'Report generated by Manhattan Grid Control Dashboard  |  {report_id}'), ln=True)

        # ── Save ─────────────────────────────────────────────────────
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.getcwd(), 'static', 'reports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.output(filepath)

        return f"/static/reports/{filename}"


if __name__ == "__main__":
    gen = ReportGenerator()
    test_state = {
        'statistics': {
            'total_load_mw': 250, 'total_substations': 8,
            'operational_substations': 7,
            'total_primary_cables': 20, 'operational_primary_cables': 19,
            'total_secondary_cables': 50, 'operational_secondary_cables': 48,
        },
        'substations': [
            {'name': 'Times Square', 'operational': True, 'load_mw': 35, 'capacity_mva': 50},
            {'name': 'Penn Station', 'operational': False, 'load_mw': 0, 'capacity_mva': 45},
        ],
        'kpis': {
            'capacity_utilization_pct': 52.6, 'grid_health_pct': 87.5,
            'ev_adoption_pct': 70, 'v2g_participation_pct': 15,
            'cable_integrity_pct': 95.7, 'vehicles_charging_pct': 8.3,
        },
        'v2g': {'active_sessions_count': 3, 'total_earnings': 42.50, 'total_power_kw': 150},
        'vehicle_stats': {'active_vehicles': 60, 'ev_vehicles': 42, 'avg_speed_mps': 8.5},
        'scenario': {'time_formatted': '14:30', 'temperature_f': 95, 'time_description': 'Afternoon Peak'},
        'ev_stations': [],
    }
    url = gen.generate_status_report(test_state, "Test run")
    print(f"Generated: {url}")

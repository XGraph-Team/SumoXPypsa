"""
ULTRA INTELLIGENT CHATBOT - WORLD CLASS CONVERSATIONAL AI
This is the most advanced AI possible - understands typos, gives suggestions,
provides ChatGPT-like experience specialized for Manhattan Power Grid
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
try:
    from openai import OpenAI
    import openai
except ImportError:
    OpenAI = None
    openai = None

from dataclasses import dataclass
import re
from difflib import SequenceMatcher, get_close_matches

# Try to import Levenshtein, fallback if not available
try:
    import Levenshtein
except ImportError:
    # Fallback implementation
    class Levenshtein:
        @staticmethod
        def distance(s1, s2):
            if len(s1) < len(s2):
                return Levenshtein.distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = None

if OPENAI_API_KEY and OpenAI:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("[ULTRA CHATBOT] OpenAI client initialized successfully")
    except Exception as e:
        print(f"[ULTRA CHATBOT] Failed to initialize OpenAI client: {e}")
        openai_client = None
else:
    print("[ULTRA CHATBOT] OpenAI not available - API key missing or package not installed")

class UltraIntelligentChatbot:
    """The most advanced conversational AI possible - like ChatGPT but specialized"""

    def __init__(self, integrated_system, ml_engine, v2g_manager, flask_app):
        self.integrated_system = integrated_system
        self.ml_engine = ml_engine
        self.v2g_manager = v2g_manager
        self.flask_app = flask_app

        # ADVANCED CONVERSATION MEMORY & CONTEXT
        self.conversation_history = []
        self.last_suggestions = []  # Track recent suggestions for context
        self.pending_confirmations = {}  # Track pending confirmations
        self.conversation_context = {}  # Track conversation state
        self.conversation_context = {
            'last_mentioned_location': None,
            'last_mentioned_substation': None,
            'last_action': None,
            'conversation_topics': [],
            'entity_references': {},  # Track "it", "that", "the station" etc.
            'session_entities': set(),  # All entities mentioned in session
        }

        # ULTIMATE WORLD-CLASS COMMAND KNOWLEDGE BASE
        self.command_knowledge = {
            # Substation commands
            'substation_commands': [
                'turn off times square', 'turn on times square', 'disable times square',
                'turn off central park', 'turn on central park', 'disable central park',
                'turn off wall street', 'turn on wall street', 'disable wall street',
                'turn off broadway', 'turn on broadway', 'disable broadway',
                'shut down substation', 'power off substation', 'restart substation',
                'substation status', 'check substation', 'substation health'
            ],

            # Location/Map commands
            'location_commands': [
                'show times square', 'show central park', 'show wall street', 'show broadway',
                'map times square', 'location of times square', 'where is times square',
                'zoom to times square', 'highlight times square', 'focus on times square',
                'show me the map', 'display location', 'map view', 'coordinates'
            ],

            # EV Charging Station commands
            'ev_charging_commands': [
                'show charging near', 'show ev near', 'show ev station near', 'show charging station near',
                'ev charging near', 'charging near', 'ev stations near', 'charging stations near',
                'show chargers near', 'chargers near', 'ev charger near', 'charging for'
            ],

            # Map control commands (zoom, camera, view)
            'map_control_commands': [
                'zoom in', 'zoom out', 'zoom in more', 'zoom out more', 'reset zoom',
                'bird view', 'top view', 'aerial view', 'birds eye',
                'tilt camera', 'angle view', '3d view', 'tilted view',
                'show overview', 'overview mode'
            ],

            # WORLD-CLASS ROUTE & NAVIGATION COMMANDS
            'route_commands': [
                'route from', 'route to', 'path from', 'path to', 'directions from', 'directions to',
                'navigate from', 'navigate to', 'how to get from', 'how to get to',
                'shortest route', 'fastest route', 'best route', 'optimal route',
                'distance from', 'distance to', 'how far from', 'how far to'
            ],

            # ADVANCED VISUALIZATION COMMANDS
            # POWER GRID VISUALIZATION COMMANDS (World-Class Feature)
            'power_grid_visualization_commands': [
                'show power grid', 'visualize grid', 'display grid', 'grid overlay',
                'show substations', 'visualize substations', 'substation map', 'power network',
                'show grid status', 'grid health', 'power distribution', 'electrical network',
                'show connections', 'power lines', 'transmission lines', 'grid topology'
            ],

            # INTELLIGENCE & ANALYSIS COMMANDS
            'intelligence_commands': [
                'analyze route', 'optimize route', 'find best location', 'suggest placement',
                'predict demand', 'forecast load', 'assess coverage', 'evaluate efficiency',
                'identify bottlenecks', 'find gaps', 'detect patterns', 'recommend actions'
            ],

            # V2G commands
            'v2g_commands': [
                'activate v2g', 'turn on v2g', 'enable v2g', 'start v2g',
                'deactivate v2g', 'turn off v2g', 'disable v2g', 'stop v2g', 'shutdown v2g',
                'v2g status', 'vehicle to grid', 'electric vehicles', 'ev status',
                'charge vehicles', 'discharge vehicles', 'v2g capacity'
            ],

            # System analysis
            'analysis_commands': [
                'analyze system', 'system status', 'grid status', 'overview',
                'health check', 'system report', 'performance analysis',
                'power grid analysis', 'infrastructure status', 'diagnostics'
            ],

            # Emergency commands
            'emergency_commands': [
                'emergency', 'help', 'shutdown everything', 'emergency stop',
                'crisis mode', 'emergency response', 'urgent', 'critical'
            ]
        }

        # TYPO CORRECTION PATTERNS
        self.common_typos = {
            # Location typos
            'times squar': 'times square',
            'time square': 'times square',
            'times squere': 'times square',
            'tims square': 'times square',
            'times sqaure': 'times square',
            'central pak': 'central park',
            'centrel park': 'central park',
            'central prak': 'central park',
            'wal street': 'wall street',
            'wall st': 'wall street',
            'broadwy': 'broadway',
            'brodway': 'broadway',

            # Charging/Station typos
            'charing': 'charging',
            'chargin': 'charging',
            'chraging': 'charging',
            'chagring': 'charging',
            'staion': 'station',
            'sattion': 'station',
            'sttion': 'station',
            'statoin': 'station',

            # Command typos
            'turn of': 'turn off',
            'trun off': 'turn off',
            'turnn off': 'turn off',
            'turn on': 'turn on',
            'trun on': 'turn on',
            'sho me': 'show me',
            'shwo me': 'show me',
            'show mi': 'show me',
            'activate': 'activate',
            'activat': 'activate',
            'analys': 'analyze',
            'analize': 'analyze',
            'statu': 'status',
            'satatus': 'status',
            'systme': 'system',
            'sytem': 'system',

            # Confirmation typos
            'confrim': 'confirm',
            'confrm': 'confirm',
            'comfirm': 'confirm',
            'cofirm': 'confirm',
            'cancle': 'cancel',
            'cancl': 'cancel',
            'cansel': 'cancel',

            # Vehicle/spawn typos
            'stat vehicles': 'start vehicles',
            'strart vehicles': 'start vehicles',
            'strat vehicles': 'start vehicles',
            'start vehicels': 'start vehicles',
            'start vehi': 'start vehicles',
            'start vehic': 'start vehicles',
            'strt vehicles': 'start vehicles',
            'satrt vehicles': 'start vehicles',
            'sart vehicles': 'start vehicles',
            'startvehicles': 'start vehicles',
            'start veh': 'start vehicles',
            'spwan vehicles': 'spawn vehicles',
            'spawn vehicels': 'spawn vehicles',
            'strart': 'start',
            'strat': 'start',
            'spwan': 'spawn'
        }

        # Complete Manhattan power grid locations from your REAL backend system
        self.manhattan_locations = {
            'times square': {
                'name': 'Times Square',
                'coords': [-73.9857, 40.7580],
                'type': 'commercial',
                'substation': 'Times Square',
                'capacity_mva': 850,
                'aliases': ['times sq', 'time square', 'times squere', 'tims square', 'ts'],
                'description': 'Major commercial hub - 850MVA capacity'
            },
            'penn station': {
                'name': 'Penn Station',
                'coords': [-73.9904, 40.7505],
                'type': 'transport',
                'substation': 'Penn Station',
                'capacity_mva': 900,
                'aliases': ['penn', 'penn st', 'pennsylv', 'pennsylvania'],
                'description': 'Major transport hub - 900MVA capacity'
            },
            'grand central': {
                'name': 'Grand Central',
                'coords': [-73.9772, 40.7527],
                'type': 'transport',
                'substation': 'Grand Central',
                'capacity_mva': 1000,
                'aliases': ['grand', 'central', 'gc', 'grand central station'],
                'description': 'Largest substation - 1000MVA capacity'
            },
            'chelsea': {
                'name': 'Chelsea',
                'coords': [-73.9969, 40.7439],
                'type': 'residential',
                'substation': 'Chelsea',
                'capacity_mva': 600,
                'aliases': ['chel', 'chelsea area'],
                'description': 'Residential area - 600MVA capacity'
            },
            'murray hill': {
                'name': 'Murray Hill',
                'coords': [-73.9816, 40.7486],
                'type': 'residential',
                'substation': 'Murray Hill',
                'capacity_mva': 650,
                'aliases': ['murray', 'murrayhill', 'mur hill'],
                'description': 'Residential area - 650MVA capacity'
            },
            'turtle bay': {
                'name': 'Turtle Bay',
                'coords': [-73.9665, 40.7519],
                'type': 'mixed',
                'substation': 'Turtle Bay',
                'capacity_mva': 700,
                'aliases': ['turtle', 'turtlebay', 'tb'],
                'description': 'Mixed use area - 700MVA capacity'
            },
            'hells kitchen': {
                'name': 'Hells Kitchen',
                'coords': [-73.9897, 40.7648],
                'type': 'residential',
                'substation': "Hell's Kitchen",
                'capacity_mva': 750,
                'aliases': ['hells', 'hell kitchen', 'hk', 'clinton'],
                'description': 'Residential area - 750MVA capacity'
            },
            'midtown east': {
                'name': 'Midtown East',
                'coords': [-73.9735, 40.7549],
                'type': 'commercial',
                'substation': 'Midtown East',
                'capacity_mva': 800,
                'aliases': ['midtown', 'mideast', 'me'],
                'description': 'Commercial district - 800MVA capacity'
            },
            'central park': {
                'name': 'Central Park',
                'coords': [-73.9654, 40.7829],
                'type': 'park',
                'substation': 'Central Park',
                'capacity_mva': 400,
                'aliases': ['cp', 'central', 'park'],
                'description': 'Central Park area - 400MVA capacity'
            },

            # MAJOR STREETS & AVENUES
            'broadway': {
                'name': 'Broadway',
                'coords': [-73.9857, 40.7580],
                'type': 'street',
                'substation': 'Times Square',
                'aliases': ['broadway ave', 'great white way'],
                'description': 'Famous street running through Times Square'
            },
            'fifth avenue': {
                'name': 'Fifth Avenue',
                'coords': [-73.9772, 40.7527],
                'type': 'street',
                'substation': 'Grand Central',
                'aliases': ['5th ave', '5th avenue', 'fifth ave'],
                'description': 'Luxury shopping avenue'
            },
            'madison avenue': {
                'name': 'Madison Avenue',
                'coords': [-73.9735, 40.7549],
                'type': 'street',
                'substation': 'Midtown East',
                'aliases': ['madison ave', 'mad ave'],
                'description': 'Advertising and business district'
            },
            'park avenue': {
                'name': 'Park Avenue',
                'coords': [-73.9735, 40.7549],
                'type': 'street',
                'substation': 'Midtown East',
                'aliases': ['park ave'],
                'description': 'Prestigious avenue'
            },
            'lexington avenue': {
                'name': 'Lexington Avenue',
                'coords': [-73.9665, 40.7519],
                'type': 'street',
                'substation': 'Turtle Bay',
                'aliases': ['lex ave', 'lexington ave'],
                'description': 'Major north-south avenue'
            },

            # FAMOUS LANDMARKS & BUILDINGS
            'empire state building': {
                'name': 'Empire State Building',
                'coords': [-73.9857, 40.7484],
                'type': 'landmark',
                'substation': 'Murray Hill',
                'aliases': ['empire state', 'esb'],
                'description': 'Iconic Art Deco skyscraper'
            },
            'chrysler building': {
                'name': 'Chrysler Building',
                'coords': [-73.9753, 40.7516],
                'type': 'landmark',
                'substation': 'Turtle Bay',
                'aliases': ['chrysler'],
                'description': 'Art Deco masterpiece'
            },
            'flatiron building': {
                'name': 'Flatiron Building',
                'coords': [-73.9897, 40.7411],
                'type': 'landmark',
                'substation': 'Chelsea',
                'aliases': ['flatiron', 'flat iron'],
                'description': 'Triangular-shaped historic building'
            },
            'madison square garden': {
                'name': 'Madison Square Garden',
                'coords': [-73.9934, 40.7505],
                'type': 'venue',
                'substation': 'Penn Station',
                'aliases': ['msg', 'the garden'],
                'description': 'Famous sports and entertainment arena'
            },

            # EV CHARGING STATIONS
            'times square garage': {
                'name': 'Times Square EV Garage',
                'coords': [-73.9857, 40.7580],
                'type': 'ev_station',
                'substation': 'Times Square',
                'aliases': ['times square ev', 'ts garage'],
                'description': 'EV charging station with 20 ports'
            },
            'penn station hub': {
                'name': 'Penn Station EV Hub',
                'coords': [-73.9904, 40.7505],
                'type': 'ev_station',
                'substation': 'Penn Station',
                'aliases': ['penn ev', 'penn hub'],
                'description': 'EV charging hub with 20 ports'
            },
            'grand central charging': {
                'name': 'Grand Central EV Charging',
                'coords': [-73.9772, 40.7527],
                'type': 'ev_station',
                'substation': 'Grand Central',
                'aliases': ['grand central ev', 'gc charging'],
                'description': 'EV charging at Grand Central - 20 ports'
            },
            'bryant park station': {
                'name': 'Bryant Park EV Station',
                'coords': [-73.9832, 40.7536],
                'type': 'ev_station',
                'substation': 'Midtown East',
                'aliases': ['bryant park ev', 'bp station'],
                'description': 'EV charging at Bryant Park - 20 ports'
            },
            'columbus circle ev': {
                'name': 'Columbus Circle EV',
                'coords': [-73.9819, 40.7681],
                'type': 'ev_station',
                'substation': 'Hells Kitchen',
                'aliases': ['columbus ev', 'cc ev'],
                'description': 'EV charging at Columbus Circle - 20 ports'
            },
            'murray hill garage': {
                'name': 'Murray Hill EV Garage',
                'coords': [-73.9816, 40.7486],
                'type': 'ev_station',
                'substation': 'Murray Hill',
                'aliases': ['murray hill ev', 'mh garage'],
                'description': 'EV charging in Murray Hill - 20 ports'
            },
            'turtle bay charging': {
                'name': 'Turtle Bay EV Charging',
                'coords': [-73.9665, 40.7519],
                'type': 'ev_station',
                'substation': 'Turtle Bay',
                'aliases': ['turtle bay ev', 'tb charging'],
                'description': 'EV charging in Turtle Bay - 20 ports'
            },
            'midtown east station': {
                'name': 'Midtown East EV Station',
                'coords': [-73.9735, 40.7549],
                'type': 'ev_station',
                'substation': 'Midtown East',
                'aliases': ['midtown east ev', 'me station'],
                'description': 'EV charging in Midtown East - 20 ports'
            },

            # DISTRICTS & NEIGHBORHOODS
            'garment district': {
                'name': 'Garment District',
                'coords': [-73.9897, 40.7548],
                'type': 'district',
                'substation': 'Hells Kitchen',
                'aliases': ['garment', 'fashion district'],
                'description': 'Fashion and textile industry center'
            },
            'koreatown': {
                'name': 'Koreatown',
                'coords': [-73.9882, 40.7486],
                'type': 'district',
                'substation': 'Murray Hill',
                'aliases': ['k-town', 'korea town'],
                'description': 'Korean cultural district'
            },
            'diamond district': {
                'name': 'Diamond District',
                'coords': [-73.9799, 40.7589],
                'type': 'district',
                'substation': 'Times Square',
                'aliases': ['diamond', 'jewelry district'],
                'description': 'Diamond and jewelry trading center'
            },

            # TRANSPORTATION HUBS
            'port authority': {
                'name': 'Port Authority Bus Terminal',
                'coords': [-73.9902, 40.7570],
                'type': 'transport',
                'substation': 'Times Square',
                'aliases': ['port authority', 'pabt', 'bus terminal'],
                'description': 'Major bus terminal'
            },
            'subway stations': {
                'name': 'NYC Subway Network',
                'coords': [-73.9857, 40.7580],
                'type': 'transport',
                'substation': 'Times Square',
                'aliases': ['subway', 'metro', 'mta'],
                'description': 'NYC subway system'
            },

            # PARKS & OPEN SPACES
            'bryant park': {
                'name': 'Bryant Park',
                'coords': [-73.9832, 40.7536],
                'type': 'park',
                'substation': 'Midtown East',
                'aliases': ['bryant'],
                'description': 'Popular midtown park'
            },
            'madison square park': {
                'name': 'Madison Square Park',
                'coords': [-73.9881, 40.7424],
                'type': 'park',
                'substation': 'Chelsea',
                'aliases': ['madison square', 'mad sq park'],
                'description': 'Historic park with Shake Shack'
            },
            'columbus circle': {
                'name': 'Columbus Circle',
                'coords': [-73.9819, 40.7681],
                'type': 'landmark',
                'substation': 'Hells Kitchen',
                'aliases': ['columbus', 'cc'],
                'description': 'Traffic circle and landmark'
            },

            # SHOPPING & ENTERTAINMENT
            'herald square': {
                'name': 'Herald Square',
                'coords': [-73.9876, 40.7505],
                'type': 'commercial',
                'substation': 'Penn Station',
                'aliases': ['herald', 'macys'],
                'description': 'Shopping district with Macys flagship'
            },
            'lincoln center': {
                'name': 'Lincoln Center',
                'coords': [-73.9832, 40.7697],
                'type': 'venue',
                'substation': 'Hells Kitchen',
                'aliases': ['lincoln', 'performing arts'],
                'description': 'Performing arts complex'
            },

            # TRAFFIC & INFRASTRUCTURE
            'traffic lights': {
                'name': 'Traffic Light Network',
                'coords': [-73.9857, 40.7580],
                'type': 'infrastructure',
                'substation': 'Times Square',
                'aliases': ['traffic', 'lights', 'signals'],
                'description': 'NYC traffic light system - 3,481 controlled lights'
            },
            'power grid': {
                'name': 'Manhattan Power Grid',
                'coords': [-73.9857, 40.7580],
                'type': 'infrastructure',
                'substation': 'Times Square',
                'aliases': ['grid', 'power system', 'electrical grid'],
                'description': 'Complete Manhattan electrical infrastructure'
            }
        }

        # Initialize dynamic system state
        self.system_state = {
            'substations': {},
            'failed_substations': [],
            'v2g_enabled_substations': [],
            'last_updated': None
        }

        print("[ULTRA CHATBOT] Initialized with MAXIMUM conversational intelligence!")

    async def _update_system_state(self):
        """Update system state from backend APIs"""
        try:
            import requests

            # Get current system status
            system_response = requests.get("http://127.0.0.1:5000/api/status", timeout=5)
            v2g_response = requests.get("http://127.0.0.1:5000/api/v2g/status", timeout=5)

            if system_response.status_code == 200:
                system_data = system_response.json()
                substations = system_data.get('substations', {})

                self.system_state['substations'] = substations
                self.system_state['failed_substations'] = [
                    name for name, info in substations.items()
                    if info.get('status') == 'failed'
                ]

            if v2g_response.status_code == 200:
                v2g_data = v2g_response.json()
                self.system_state['v2g_enabled_substations'] = v2g_data.get('enabled_substations', [])

            self.system_state['last_updated'] = datetime.now()
            print(f"[ULTRA CHATBOT] System updated: {len(self.system_state['failed_substations'])} failed substations, {len(self.system_state['v2g_enabled_substations'])} V2G enabled")

        except Exception as e:
            print(f"[ULTRA CHATBOT] Failed to update system state: {e}")

    async def chat(self, user_input: str, user_id: str = 'web_user') -> Dict[str, Any]:
        """Ultra intelligent chat processing - understands everything like ChatGPT"""

        print(f"[ULTRA CHATBOT] Processing: '{user_input}' from user: '{user_id}'")

        # SPECIAL HANDLING: Skip greeting for system scenario completion messages
        if user_id == 'system' and any(phrase in user_input.lower() for phrase in ['scenario just completed', 'scenario complete', 'acknowledge this restoration', 'acknowledge this dramatic scenario']):
            print(f"[ULTRA CHATBOT] Detected scenario completion message from system - providing brief acknowledgment")
            # Provide very brief acknowledgment without greeting
            if 'v2g' in user_input.lower() and 'restored' in user_input.lower():
                response_text = "✅ V2G scenario completed successfully!"
            elif 'blackout' in user_input.lower() and 'crisis' in user_input.lower():
                response_text = "🚨 Blackout scenario complete. System requires manual restoration."
            else:
                response_text = "✅ Scenario acknowledged."

            return {
                'success': True,
                'text': response_text,
                'scenario_acknowledgment': True,
                'timestamp': datetime.now().isoformat()
            }

        # Update system state first to understand current situation
        await self._update_system_state()

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # CRITICAL FIX: Handle numbered responses referring to previous suggestions
        numbered_response = self._detect_numbered_response(user_input.strip())
        if numbered_response:
            print(f"[ULTRA CHATBOT] Detected numbered response: {numbered_response}")
            return await self._handle_numbered_response(numbered_response)

        # CRITICAL FIX: Handle confirmation responses
        confirmation_response = self._detect_confirmation_response(user_input.strip())
        if confirmation_response:
            print(f"[ULTRA CHATBOT] Detected confirmation response: {confirmation_response}")
            return await self._handle_confirmation_response(confirmation_response)

        # Handle map control commands (zoom, camera, view)
        map_command_response = self._handle_map_command(user_input.strip())
        if map_command_response:
            print(f"[ULTRA CHATBOT] Detected map command: {user_input.strip()}")
            return map_command_response

        try:
            # ENHANCED INTELLIGENCE: First, understand what the user REALLY wants
            understanding = await self._deep_understanding(user_input)

            # If understanding is unclear, ask for clarification intelligently
            if understanding['needs_clarification']:
                return understanding['clarification_response']

            # STEP 1: Intelligent typo correction and preprocessing
            simple_commands = ['hi', 'hello', 'hey', 'greetings', 'status', 'help', 'v2g', 'yes', 'no', 'ok', 'cancel']
            if user_input.lower().strip() in simple_commands or len(user_input.strip()) <= 3:
                corrected_input = user_input  # Don't autocorrect simple commands
                corrections_made = []
            else:
                corrected_input, corrections_made = self._intelligent_typo_correction(user_input)

            # STEP 2: Fuzzy command matching with context awareness
            best_match, confidence = self._fuzzy_command_matching(corrected_input)

            # ENHANCED: Handle greetings more naturally
            if any(greeting in corrected_input.lower() for greeting in ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon']):
                greeting_text = """# 👋 Manhattan Power Grid AI

**I control** substations, time, temperature & scenarios via natural language.

**Quick Start:**
• `"turn off times square"` • `"set time to 8"` • `"morning rush"` • `"status"`

Type **`help`** for all commands | Just ask naturally! 🚀"""

                return {
                    'original_input': user_input,
                    'corrected_input': corrected_input,
                    'corrections_made': corrections_made,
                    'best_match': None,
                    'confidence': 1.0,
                    'intent': 'greeting',
                    'success': True,
                    'text': greeting_text,
                    'suggestions': self._track_suggestions([
                        "help",
                        "set time for 8",
                        "morning rush",
                        "status"
                    ]),
                    'timestamp': datetime.now().isoformat()
                }

            # ENHANCED: Subsection-based help system
            # Check for general help command
            if corrected_input.lower().strip() in ['help', 'commands', 'what can you do', 'show commands', 'list commands']:
                help_menu = """# 📚 **Help Menu**

| Section | What It Does |
|---------|--------------|
| 🔌 **Grid** | Substations on/off |
| 🕐 **Time** | Set time (auto-spawns traffic) |
| 🌡️ **Temperature** | Adjust temp |
| 🎯 **Scenarios** | Pre-configured tests |
| 🗺️ **Navigation** | Find locations |
| ⚡ **V2G** | Emergency power |
| 📊 **Analysis** | System status |
| 💡 **Examples** | Quick workflows |

**Type:** `"help grid"`, `"help time"`, `"help scenarios"`, etc.

Or just ask naturally! 🚀"""

                return {
                    'original_input': user_input,
                    'corrected_input': corrected_input,
                    'corrections_made': corrections_made,
                    'best_match': None,
                    'confidence': 1.0,
                    'intent': 'help_menu',
                    'success': True,
                    'text': help_menu,
                    'suggestions': self._track_suggestions([
                        "help grid",
                        "help scenarios",
                        "help time"
                    ]),
                    'timestamp': datetime.now().isoformat()
                }

            # Handle section-specific help commands
            help_section_result = self._handle_help_section(corrected_input, user_input, corrections_made)
            if help_section_result:
                return help_section_result

            # STEP 3: Enhanced context understanding
            intent, entities = self._understand_context_enhanced(corrected_input, understanding)

            # STEP 4: Generate intelligent response with safety checks
            response = await self._generate_ultra_intelligent_response_enhanced(
                user_input, corrected_input, corrections_made,
                best_match, confidence, intent, entities, understanding
            )

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.get('text', 'Response generated')
            })

            return response

        except Exception as e:
            print(f"[ULTRA CHATBOT ERROR] {str(e)}")
            return await self._fallback_intelligent_response(user_input, str(e))

    async def _deep_understanding(self, user_input: str) -> Dict[str, Any]:
        """Deep contextual understanding - like ChatGPT"""

        text_lower = user_input.lower().strip()

        # Check for unclear/ambiguous inputs that need clarification
        unclear_patterns = [
            # Too vague
            r'^(it|that|this|show|turn)$',
            r'^(do|can|will|should)\s*(it|that|this)?\s*$',
            r'^(what|where|how|when|why)\s*$',
            # Incomplete commands
            r'^(turn|show|activate|disable)\s*(me|it)?\s*$',
            r'^(where|what)\s+is\s*$',
            r'^(can|could|will|would)\s+you\s*$'
        ]

        needs_clarification = any(re.match(pattern, text_lower) for pattern in unclear_patterns)

        if needs_clarification:
            # Generate intelligent clarification based on what they said
            suggestions = []

            if any(word in text_lower for word in ['turn', 'off', 'on', 'disable', 'activate']):
                suggestions = [
                    "turn off times square substation",
                    "turn on penn station substation",
                    "activate v2g system",
                    "disable murray hill substation"
                ]
                clarification = "I understand you want to control something. Could you be more specific? For example:"

            elif any(word in text_lower for word in ['show', 'display', 'see', 'view']):
                suggestions = [
                    "show power network of times square",
                    "show me central park location",
                    "display system status",
                    "show all substations"
                ]
                clarification = "I understand you want to see something. What would you like me to show you? For example:"

            elif any(word in text_lower for word in ['where', 'location', 'find']):
                suggestions = [
                    "where is times square substation?",
                    "show me penn station location",
                    "find murray hill on map"
                ]
                clarification = "I can help you find locations! What are you looking for? For example:"

            else:
                suggestions = [
                    "show power network of times square",
                    "turn off penn station substation",
                    "what's the system status?",
                    "where is central park?"
                ]
                clarification = "I'd be happy to help! Could you be more specific about what you'd like me to do? Here are some examples:"

            return {
                'needs_clarification': True,
                'clarification_response': {
                    'original_input': user_input,
                    'corrected_input': user_input,
                    'corrections_made': [],
                    'intent': 'clarification_needed',
                    'success': True,
                    'text': f"{clarification}",
                    'suggestions': self._track_suggestions(suggestions),
                    'timestamp': datetime.now().isoformat()
                }
            }

        return {'needs_clarification': False}

    def _handle_help_section(self, corrected_input: str, user_input: str, corrections_made: list) -> Optional[Dict[str, Any]]:
        """Handle section-specific help requests"""

        lower_input = corrected_input.lower().strip()

        # Define help sections with their content
        help_sections = {
            'grid': {
                'title': '🔌 **Power Grid Control**',
                'content': """**Commands:**
• `"turn off times square"` - Fail substation
• `"restore central park"` - Restore substation
• `"restore all"` - Turn everything back on

**Major Substations:** Times Square, Central Park, Penn Station, Murray Hill, Midtown East

Type `"help"` to return.""",
                'suggestions': ["turn off times square", "restore all", "help"]
            },
            'time': {
                'title': '🕐 **Time Control**',
                'content': """**Commands:** `"set time to 8"`, `"set time for 18"`

**Traffic Auto-Spawns by Time:**
| Time | Vehicles | Time | Vehicles |
|------|----------|------|----------|
| 0-5 AM | 10-20 | 11-14 PM | 70-90 |
| 5-7 AM | 40-60 | 14-17 PM | 75-95 |
| 7-9 AM 🚗 | 85-100 | 17-19 PM 🚗 | 90-100 |
| 9-11 AM | 60-80 | 19-24 PM | 20-85 |

Type `"help"` to return.""",
                'suggestions': ["set time to 8", "set time for 18", "help"]
            },
            'temperature': {
                'title': '🌡️ **Temperature Control**',
                'content': """**Commands:** `"set temperature to 98"`, `"temp 72"`

**Impact:** 60-75°F ❄️ Normal | 75-90°F ☀️ Warm | 90-105°F 🔥 Heatwave | 105-120°F ☢️ Crisis
Higher temps = more AC load.

Type `"help"` to return.""",
                'suggestions': ["set temperature to 98", "set temp to 72", "help"]
            },
            'scenarios': {
                'title': '🎯 **Test Scenarios**',
                'content': """**Time/Weather Scenarios** (set time + temp + vehicles):

| Scenario | Time | Temp | Vehicles |
|----------|------|------|----------|
| 🌅 **morning rush** | 8 AM | 75°F | 100 |
| 🌆 **evening rush** | 6 PM | 80°F | 120 |
| ☀️ **normal day** | 12 PM | 72°F | 60 |
| 🔥 **heatwave crisis** | 3 PM | 98°F | 90 |
| ☢️ **catastrophic heat** | 2 PM | 115°F | 100 |
| 🌙 **late night** | 3 AM | 65°F | 15 |

**Emergency Scenarios** (different - test grid resilience):
• 🔌 **blackout scenario** - Fails multiple substations, tests emergency response
• ⚡ **v2g scenario** - Tests Vehicle-to-Grid emergency power restoration

**Why different?** Time scenarios control environment. Emergency scenarios test system failures.

Type `"help"` to return.""",
                'suggestions': ["morning rush", "blackout scenario", "help"]
            },
            'navigation': {
                'title': '🗺️ **Map Navigation**',
                'content': """**Commands:**
• `"show me central park"` - Show location
• `"zoom to times square"` - Focus area
• `"where is penn station"` - Find place

**Locations:** Central Park, Times Square, Penn Station, Rockefeller Center, Broadway, Empire State

Type `"help"` to return.""",
                'suggestions': ["show me central park", "zoom to times square", "help"]
            },
            'v2g': {
                'title': '⚡ **V2G Emergency System**',
                'content': """Emergency power from EVs with ≥70% battery.

**Commands:**
• `"activate v2g rescue"` - Start emergency response
• `"v2g status"` - Check capacity

Auto-suggested during blackouts.

Type `"help"` to return.""",
                'suggestions': ["activate v2g rescue", "v2g status", "help"]
            },
            'analysis': {
                'title': '📊 **System Analysis**',
                'content': """**Commands:**
• `"status"` - Full system status
• `"analyze grid"` - Grid performance
• `"show substation status"` - Substation info

**Shows:** Substations, traffic lights, vehicles, EVs, charging, power load (MW), health

Type `"help"` to return.""",
                'suggestions': ["status", "analyze grid", "help"]
            },
            'examples': {
                'title': '💡 **Quick Workflows**',
                'content': """**Morning Test:** `set time for 8` → `status`
**Heatwave:** `set temperature to 115` → `catastrophic heat`
**Emergency:** `turn off times square` → `activate v2g rescue`
**Navigation:** `show me central park` → `zoom to times square`

**Natural language works:** `"Show me what's happening at times square"` ✓

Type `"help"` to return.""",
                'suggestions': ["morning rush", "status", "help"]
            }
        }

        # Check if input matches any help section
        for section_key, section_data in help_sections.items():
            # Match patterns like "help grid", "help time control", "grid help", etc.
            if (f'help {section_key}' in lower_input or
                f'{section_key} help' in lower_input or
                (section_key in lower_input and 'help' in lower_input)):

                return {
                    'original_input': user_input,
                    'corrected_input': corrected_input,
                    'corrections_made': corrections_made,
                    'best_match': None,
                    'confidence': 1.0,
                    'intent': f'help_{section_key}',
                    'success': True,
                    'text': f"{section_data['title']}\n\n{section_data['content']}",
                    'suggestions': self._track_suggestions(section_data['suggestions']),
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def _understand_context_enhanced(self, text: str, understanding: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Enhanced context understanding with better natural language processing"""

        # Use the existing context understanding but enhance it
        original_intent, original_entities = self._understand_context(text)

        # Enhanced entity extraction for natural language
        text_lower = text.lower()
        enhanced_entities = original_entities.copy()

        # Better location extraction
        location_patterns = [
            r'(?:show|find|where|locate).*?(?:me\s+)?([\w\s]+?)(?:\s+(?:on|in|at|substation|location|map))?$',
            r'(?:power\s+network\s+of|grid\s+of|network\s+for)\s+([\w\s]+?)(?:\s+substation)?$',
            r'([\w\s]+?)\s+(?:substation|location|area|place)(?:\s+on\s+map)?$'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text_lower)
            if match and 'location_data' not in enhanced_entities:
                location = match.group(1).strip()
                # Clean up common words
                location = re.sub(r'\b(the|a|an|this|that|show|me|find|where|is)\b', '', location).strip()
                if location and len(location) > 2:
                    enhanced_entities['location_data'] = {'name': location}
                    break

        return original_intent, enhanced_entities

    async def _generate_ultra_intelligent_response_enhanced(self, original_input: str, corrected_input: str,
                                                          corrections: List[str], best_match: Optional[str],
                                                          confidence: float, intent: str, entities: Dict[str, Any],
                                                          understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced response generation with safety checks and confirmations"""

        # Check if action needs confirmation
        if self._needs_confirmation(intent, entities, corrected_input):
            return await self._request_confirmation(original_input, corrected_input, intent, entities)

        # Use the existing response generation but enhance it
        response = await self._generate_ultra_intelligent_response(
            original_input, corrected_input, corrections, best_match, confidence, intent, entities
        )

        # Enhance the response with more natural language
        if response.get('success') and response.get('text'):
            original_text = response['text']

            # Make responses more conversational
            if intent == 'power_grid_visualization':
                if 'network' in corrected_input.lower():
                    response['text'] = f"🔌 **Power Network Visualization**\n\n{original_text}\n\n💡 The highlighting shows exactly which cables and infrastructure are connected to this specific substation."

            elif intent == 'substation_control':
                action = entities.get('action', 'unknown')
                location = entities.get('location_data', {}).get('name', 'the substation')
                if action in ['turn_off', 'fail', 'disable']:
                    response['text'] = f"⚠️ **Substation Control**\n\n{original_text}\n\n🔒 This is a critical infrastructure operation. The {location} substation will be safely shut down."

        return response

    def _needs_confirmation(self, intent: str, entities: Dict[str, Any], corrected_input: str) -> bool:
        """Determine if an action needs user confirmation"""

        # Critical actions that need confirmation
        critical_intents = ['substation_control']

        if intent in critical_intents:
            action = entities.get('action', '')
            critical_actions = ['turn_off', 'fail', 'disable', 'shut_down']
            if any(action_word in action for action_word in critical_actions):
                return True

        # Also check for potentially destructive keywords
        destructive_keywords = ['shut down', 'turn off', 'disable', 'fail', 'stop', 'kill']
        if any(keyword in corrected_input.lower() for keyword in destructive_keywords):
            return True

        return False

    async def _request_confirmation(self, original_input: str, corrected_input: str,
                                  intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Request confirmation for critical actions"""

        location = entities.get('location_data', {}).get('name', 'the substation')
        action = entities.get('action', 'perform this action')

        # Store the pending action with timestamp for retrieval
        timestamp = datetime.now().isoformat()
        self.pending_confirmations[timestamp] = {
            'intent': intent,
            'entities': entities,
            'corrected_input': corrected_input,
            'original_input': original_input
        }

        print(f"[CONFIRMATION] Stored pending action: {action} {location}")

        return {
            'original_input': original_input,
            'corrected_input': corrected_input,
            'intent': 'confirmation_required',
            'success': False,
            'needs_confirmation': True,
            'text': f"⚠️ **Confirmation Required**\n\nYou're about to {action} {location}. This is a critical infrastructure operation that could affect power distribution.\n\n**Are you sure you want to proceed?**\n\nType 'yes confirm' to proceed, or 'cancel' to abort.",
            'suggestions': self._track_suggestions([
                "yes confirm",
                "cancel",
                "show me system status first",
                "what would happen if I do this?"
            ]),
            'pending_action': {
                'intent': intent,
                'entities': entities,
                'corrected_input': corrected_input
            },
            'timestamp': timestamp
        }

    def _intelligent_typo_correction(self, text: str) -> Tuple[str, List[str]]:
        """Advanced typo correction using multiple algorithms"""

        corrected_text = text.lower().strip()
        corrections_made = []

        # STEP 1: Direct typo mapping (only exact word matches, not substrings)
        words = corrected_text.split()
        for i, word in enumerate(words):
            if word in self.common_typos:
                original_word = word
                words[i] = self.common_typos[word]
                corrections_made.append(f"'{original_word}' -> '{self.common_typos[word]}'")
        corrected_text = ' '.join(words)

        # STEP 2: Conservative fuzzy matching (only for obvious typos)
        words = corrected_text.split()
        for i, word in enumerate(words):
            for location, data in self.manhattan_locations.items():
                # Only fix obvious typos with distance <= 1 and length > 3
                location_words = location.split()
                for loc_word in location_words:
                    if len(word) > 3 and len(loc_word) > 3 and Levenshtein.distance(word, loc_word) == 1:
                        words[i] = loc_word
                        corrections_made.append(f"'{word}' -> '{loc_word}'")
                        break

        corrected_text = ' '.join(words)

        return corrected_text, corrections_made

    def _fuzzy_command_matching(self, text: str) -> Tuple[Optional[str], float]:
        """Find best matching command using fuzzy logic"""

        all_commands = []
        for category, commands in self.command_knowledge.items():
            all_commands.extend(commands)

        # Find best matches
        matches = get_close_matches(text, all_commands, n=1, cutoff=0.4)

        if matches:
            best_match = matches[0]
            confidence = SequenceMatcher(None, text, best_match).ratio()
            return best_match, confidence

        # Try partial matching
        best_partial_match = None
        best_partial_score = 0

        for command in all_commands:
            # Check if any words from the command appear in text
            command_words = set(command.split())
            text_words = set(text.split())
            common_words = command_words.intersection(text_words)

            if common_words:
                score = len(common_words) / len(command_words)
                if score > best_partial_score:
                    best_partial_score = score
                    best_partial_match = command

        return best_partial_match, best_partial_score

    def _resolve_pronouns(self, text: str) -> str:
        """Resolve pronouns and contextual references like 'the station', 'it', 'that'"""

        text_lower = text.lower()
        resolved_text = text

        # Track what we're resolving for debugging
        resolutions = []

        # Handle "the station" references
        if 'the station' in text_lower and self.conversation_context['last_mentioned_substation']:
            resolved_text = resolved_text.replace('the station', self.conversation_context['last_mentioned_substation'])
            resolutions.append(f"'the station' -> '{self.conversation_context['last_mentioned_substation']}'")

        # Handle "it" references for locations/substations
        if ' it ' in text_lower or text_lower.startswith('it ') or text_lower.endswith(' it'):
            if self.conversation_context['last_mentioned_location']:
                resolved_text = resolved_text.replace(' it ', f" {self.conversation_context['last_mentioned_location']} ")
                resolved_text = resolved_text.replace('it ', f"{self.conversation_context['last_mentioned_location']} ")
                resolved_text = resolved_text.replace(' it', f" {self.conversation_context['last_mentioned_location']}")
                resolutions.append(f"'it' -> '{self.conversation_context['last_mentioned_location']}'")
            elif self.conversation_context['last_mentioned_substation']:
                resolved_text = resolved_text.replace(' it ', f" {self.conversation_context['last_mentioned_substation']} ")
                resolved_text = resolved_text.replace('it ', f"{self.conversation_context['last_mentioned_substation']} ")
                resolved_text = resolved_text.replace(' it', f" {self.conversation_context['last_mentioned_substation']}")
                resolutions.append(f"'it' -> '{self.conversation_context['last_mentioned_substation']}'")

        # Handle "that" references
        if 'that location' in text_lower or 'that place' in text_lower or 'that area' in text_lower:
            if self.conversation_context['last_mentioned_location']:
                resolved_text = resolved_text.replace('that location', self.conversation_context['last_mentioned_location'])
                resolved_text = resolved_text.replace('that place', self.conversation_context['last_mentioned_location'])
                resolved_text = resolved_text.replace('that area', self.conversation_context['last_mentioned_location'])
                resolutions.append(f"'that location/place/area' -> '{self.conversation_context['last_mentioned_location']}'")

        # Handle "that station" or "that substation"
        if 'that station' in text_lower or 'that substation' in text_lower:
            if self.conversation_context['last_mentioned_substation']:
                resolved_text = resolved_text.replace('that station', self.conversation_context['last_mentioned_substation'])
                resolved_text = resolved_text.replace('that substation', self.conversation_context['last_mentioned_substation'])
                resolutions.append(f"'that station/substation' -> '{self.conversation_context['last_mentioned_substation']}'")

        # Handle "there" references
        if ' there' in text_lower and self.conversation_context['last_mentioned_location']:
            resolved_text = resolved_text.replace(' there', f" {self.conversation_context['last_mentioned_location']}")
            resolutions.append(f"'there' -> '{self.conversation_context['last_mentioned_location']}'")

        if resolutions:
            print(f"[CONTEXT] Pronoun resolution: {'; '.join(resolutions)}")
            print(f"[CONTEXT] Original: '{text}' -> Resolved: '{resolved_text}'")

        return resolved_text

    def _update_conversation_context(self, text: str, intent: str, entities: Dict[str, Any]):
        """Update conversation context for future pronoun resolution"""

        # Update last mentioned location
        if entities.get('location'):
            self.conversation_context['last_mentioned_location'] = entities['location']
            self.conversation_context['session_entities'].add(entities['location'])

            # Also track if this is a substation
            location_data = entities.get('location_data', {})
            if location_data.get('type') == 'substation' or entities.get('location') in [
                'times square', 'penn station', 'grand central', 'wall street',
                'murray hill', 'turtle bay', 'hells kitchen', 'midtown east'
            ]:
                self.conversation_context['last_mentioned_substation'] = entities['location']

        # Update last action
        if entities.get('action'):
            self.conversation_context['last_action'] = entities['action']

        # Add to conversation topics
        if intent not in self.conversation_context['conversation_topics']:
            self.conversation_context['conversation_topics'].append(intent)
            # Keep only last 5 topics
            if len(self.conversation_context['conversation_topics']) > 5:
                self.conversation_context['conversation_topics'] = self.conversation_context['conversation_topics'][-5:]

        # Track entity references for pronouns
        text_lower = text.lower()
        if any(pronoun in text_lower for pronoun in ['it', 'that', 'the station', 'there']):
            # User is using pronouns, so they expect context awareness
            self.conversation_context['entity_references']['user_expects_context'] = True

        print(f"[CONTEXT] Updated context - Last location: {self.conversation_context['last_mentioned_location']}, "
              f"Last substation: {self.conversation_context['last_mentioned_substation']}, "
              f"Last action: {self.conversation_context['last_action']}")

    def _understand_context(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Advanced LLM-like context understanding with pronoun resolution"""

        # First resolve pronouns and contextual references
        resolved_text = self._resolve_pronouns(text)
        text_lower = resolved_text.lower()
        entities = {}

        # CRITICAL: Check for scenario commands FIRST before OpenAI (highest priority!)
        intent = None
        v2g_scenario_phrases = ['v2g scenario', 'run v2g scenario', 'trigger v2g scenario', 'execute v2g scenario',
                               'show v2g scenario', 'demonstrate v2g', 'simulate v2g', 'v2g rescue scenario']
        blackout_scenario_phrases = ['blackout scenario', 'trigger blackout scenario', 'run blackout scenario',
                                    'citywide blackout scenario', 'execute blackout scenario', 'simulate blackout',
                                    'demonstrate blackout', 'show blackout scenario']

        if any(phrase in text_lower for phrase in v2g_scenario_phrases):
            intent = 'scenario_simulation'
            print(f"[ULTRA CHATBOT] PRE-CHECK: SCENARIO SIMULATION detected (v2g scenario)")
        elif any(phrase in text_lower for phrase in blackout_scenario_phrases):
            intent = 'scenario_simulation'
            print(f"[ULTRA CHATBOT] PRE-CHECK: SCENARIO SIMULATION detected (blackout scenario)")
        elif any(phrase in text_lower for phrase in ['start vehicles', 'spawn vehicles', 'start sumo', 'launch vehicles']):
            intent = 'start_vehicles'
            print(f"[ULTRA CHATBOT] PRE-CHECK: START_VEHICLES detected")

        # Use OpenAI for sophisticated intent understanding if available (skip if already detected scenario)
        if not intent and openai_client:
            try:
                intent_prompt = f"""Analyze this power grid command with advanced intelligence:
"{text}"

Determine intent (one word only):
- scenario_simulation: Running demo scenarios like "v2g scenario", "blackout scenario", "run v2g scenario". Examples: "v2g scenario", "trigger blackout scenario", "simulate v2g"
- v2g_control: V2G activation/deactivation (NOT scenarios). Examples: "activate v2g", "turn off v2g", "disable v2g", "deactivate v2g", "v2g status"
- substation_control: turn on/off, fail, restore substations. Examples: "fail penn station", "turn off times square", "restore murray hill"
- power_grid_visualization: visualize, show, display power grid. Examples: "show power grid", "visualize grid", "display substations"
- map_control: zoom commands, camera controls. Examples: "zoom in", "zoom out", "bird view", "tilt camera"
- location_query: show, find locations. Examples: "show me central park", "where is penn station", "find chelsea"
- system_analysis: status, analysis, overview. Examples: "system status", "analyze grid"
- educational_query: how does, what is, explain. Examples: "how does a transformer work", "what is V2G"
- infrastructure_query: asking about system components. Examples: "which substations", "how many substations"
- greeting: hi, hello, hey
- conversational: questions, general discussion

CRITICAL: "scenario" keyword = scenario_simulation, NOT v2g_control
Use advanced reasoning to understand context, typos, and implied meanings.

Return format: intent"""

                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": intent_prompt}],
                    max_tokens=20,
                    temperature=0.1
                )

                ai_intent = response.choices[0].message.content.strip().lower()
                print(f"[ULTRA CHATBOT] OpenAI raw response: '{ai_intent}' for text: '{text}'")

                if ai_intent in ['scenario_simulation', 'start_vehicles', 'substation_control', 'location_query', 'v2g_control', 'power_grid_visualization', 'map_control', 'system_analysis', 'educational_query', 'infrastructure_query', 'greeting', 'conversational', 'ev_charging_query']:
                    intent = ai_intent
                    print(f"[ULTRA CHATBOT] OpenAI detected intent: {intent}")
                else:
                    print(f"[ULTRA CHATBOT] OpenAI returned invalid intent '{ai_intent}', falling back to rule-based")
                    raise Exception("Invalid AI intent")

            except Exception as e:
                print(f"[ULTRA CHATBOT] OpenAI failed: {e}, using rule-based")
                # Enhanced fallback to rule-based intent detection
                # Priority 0: SCENARIO COMMANDS (highest priority - before everything else!)
                # STRICT scenario detection - must include "scenario" OR "run/trigger/execute/demonstrate/simulate/show"
                v2g_scenario_phrases = ['v2g scenario', 'run v2g scenario', 'trigger v2g scenario', 'execute v2g scenario',
                                       'show v2g scenario', 'demonstrate v2g', 'simulate v2g', 'v2g rescue scenario']
                blackout_scenario_phrases = ['blackout scenario', 'trigger blackout scenario', 'run blackout scenario',
                                            'citywide blackout scenario', 'execute blackout scenario', 'simulate blackout',
                                            'demonstrate blackout', 'show blackout scenario']

                if any(phrase in text_lower for phrase in v2g_scenario_phrases):
                    intent = 'scenario_simulation'
                    print(f"[ULTRA CHATBOT] Rule-based: SCENARIO SIMULATION detected (v2g scenario)")
                elif any(phrase in text_lower for phrase in blackout_scenario_phrases):
                    intent = 'scenario_simulation'
                    print(f"[ULTRA CHATBOT] Rule-based: SCENARIO SIMULATION detected (blackout scenario)")
                elif any(phrase in text_lower for phrase in ['start vehicles', 'spawn vehicles', 'start sumo', 'launch vehicles']):
                    intent = 'start_vehicles'
                    print(f"[ULTRA CHATBOT] Rule-based: START_VEHICLES detected")
                # Priority 1: V2G control (real V2G activation - NOT scenarios)
                elif any(word in text_lower for word in ['v2g', 'vehicle to grid', 'vehicle-to-grid']):
                    intent = 'v2g_control'
                    print(f"[ULTRA CHATBOT] Rule-based: v2g_control detected (v2g keyword found)")
                # Priority 2: EV Charging Station Query
                elif any(phrase in text_lower for phrase in ['show charging near', 'show ev near', 'show ev station near', 'charging near', 'ev near', 'chargers near', 'charging station near', 'ev station near']):
                    intent = 'ev_charging_query'
                    print(f"[ULTRA CHATBOT] Rule-based: ev_charging_query detected")
                # Priority 3: Power Grid Visualization
                elif any(phrase in text_lower for phrase in ['show power grid', 'visualize grid', 'display grid', 'grid overlay', 'show substations', 'visualize substations', 'substation map', 'power network', 'show grid status', 'grid health', 'power distribution', 'electrical network', 'show connections', 'power lines', 'transmission lines', 'grid topology', 'hide power grid', 'hide grid', 'hide it', 'turn off grid', 'turn it off', 'hide all', 'only substations', 'only cables', 'only 13.8', 'only 480', 'only ev', 'keep only']):
                    intent = 'power_grid_visualization'
                    print(f"[ULTRA CHATBOT] Rule-based: power_grid_visualization detected")
                # Priority 3: V2G control (general EV/emergency power)
                elif any(word in text_lower for word in ['vehicle', 'ev', 'charging', 'emergency power', 'backup power']):
                    intent = 'v2g_control'
                    print(f"[ULTRA CHATBOT] Rule-based: v2g_control detected (ev/emergency)")
                # Priority 4: Substation control
                elif any(word in text_lower for word in ['turn off', 'turn on', 'disable', 'enable', 'shut down', 'shut off',
                                          'power down', 'power up', 'fail', 'restore', 'switch off', 'switch on',
                                          'take down', 'bring up', 'offline', 'online', 'disconnect', 'connect']):
                    intent = 'substation_control'
                    print(f"[ULTRA CHATBOT] Rule-based: substation_control detected")
                # Priority 3: Location/map queries
                elif any(phrase in text_lower for phrase in ['show me', 'where is', 'take me to', 'go to', 'find']) or any(word in text_lower for word in ['location', 'map', 'display', 'coordinates', 'locate', 'zoom to', 'highlight']):
                    intent = 'location_query'
                # Priority 4: Infrastructure queries - catch ANY question about system components
                elif (any(word in text_lower for word in ['substations', 'substation', 'stations', 'station', 'cables', 'cable', 'ev', 'electric', 'charging']) and
                      any(word in text_lower for word in ['?', 'which', 'what', 'how many', 'how much', 'list', 'names', 'name', 'are', 'is', 'have', 'do we', 'tell me', 'show me']) or
                      text_lower.endswith('?') or 'we have' in text_lower or 'do we' in text_lower or 'are they' in text_lower):
                    intent = 'infrastructure_query'
                # Priority 5: System analysis
                elif any(word in text_lower for word in ['analyze', 'status', 'health', 'report', 'overview', 'check']):
                    intent = 'system_analysis'
                # Priority 6: Greetings
                elif any(word in text_lower for word in ['hi', 'hello', 'hey', 'greetings']):
                    intent = 'greeting'
                # Priority 7: Any question pattern (ends with ?, or starts with question words)
                elif (text_lower.strip().endswith('?') or
                      any(text_lower.startswith(word) for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you', 'could you', 'will you', 'do you', 'are you', 'is there', 'are there'])):
                    intent = 'conversational'
                else:
                    intent = 'general_conversation'
        else:
            # Enhanced rule-based intent detection when OpenAI is not available
            # Priority 0: SCENARIO COMMANDS (highest priority - before everything else!)
            # STRICT scenario detection - must include "scenario" OR "run/trigger/execute/demonstrate/simulate/show"
            v2g_scenario_phrases = ['v2g scenario', 'run v2g scenario', 'trigger v2g scenario', 'execute v2g scenario',
                                   'show v2g scenario', 'demonstrate v2g', 'simulate v2g', 'v2g rescue scenario']
            blackout_scenario_phrases = ['blackout scenario', 'trigger blackout scenario', 'run blackout scenario',
                                        'citywide blackout scenario', 'execute blackout scenario', 'simulate blackout',
                                        'demonstrate blackout', 'show blackout scenario']

            if any(phrase in text_lower for phrase in v2g_scenario_phrases):
                intent = 'scenario_simulation'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): SCENARIO SIMULATION detected (v2g scenario)")
            elif any(phrase in text_lower for phrase in blackout_scenario_phrases):
                intent = 'scenario_simulation'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): SCENARIO SIMULATION detected (blackout scenario)")
            elif any(phrase in text_lower for phrase in ['start vehicles', 'spawn vehicles', 'start sumo', 'launch vehicles']):
                intent = 'start_vehicles'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): START_VEHICLES detected")
            # Priority 1: V2G control (real V2G activation - NOT scenarios)
            elif any(word in text_lower for word in ['v2g', 'vehicle to grid', 'vehicle-to-grid']):
                intent = 'v2g_control'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): v2g_control detected (v2g keyword found)")
            # Priority 2: EV Charging Station Query
            elif any(phrase in text_lower for phrase in ['show charging near', 'show ev near', 'show ev station near', 'charging near', 'ev near', 'chargers near', 'charging station near', 'ev station near']):
                intent = 'ev_charging_query'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): ev_charging_query detected")
            # Priority 3: Power Grid Visualization
            elif any(phrase in text_lower for phrase in ['show power grid', 'visualize grid', 'display grid', 'grid overlay', 'show substations', 'visualize substations', 'substation map', 'power network', 'show grid status', 'grid health', 'power distribution', 'electrical network', 'show connections', 'power lines', 'transmission lines', 'grid topology', 'hide power grid', 'hide grid', 'hide it', 'turn off grid', 'turn it off', 'hide all', 'only substations', 'only cables', 'only 13.8', 'only 480', 'only ev', 'keep only']):
                intent = 'power_grid_visualization'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): power_grid_visualization detected")
            # Priority 3: V2G control (general EV/emergency power)
            elif any(word in text_lower for word in ['vehicle', 'ev', 'charging', 'emergency power', 'backup power', 'activate']):
                intent = 'v2g_control'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): v2g_control detected (ev/emergency)")
            # Priority 4: Substation control
            elif any(word in text_lower for word in ['turn off', 'turn on', 'disable', 'enable', 'shut down', 'shut off',
                                      'power down', 'power up', 'fail', 'restore', 'switch off', 'switch on',
                                      'take down', 'bring up', 'offline', 'online', 'disconnect', 'connect']):
                intent = 'substation_control'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): substation_control detected")
            # Priority 3: Location/map queries
            elif any(phrase in text_lower for phrase in ['show me', 'where is', 'take me to', 'go to', 'find']) or any(word in text_lower for word in ['location', 'map', 'display', 'coordinates', 'locate', 'zoom to', 'highlight']):
                intent = 'location_query'
            # Priority 4: Infrastructure queries - catch ANY question about system components
            elif (any(word in text_lower for word in ['substations', 'substation', 'stations', 'station', 'cables', 'cable', 'ev', 'electric', 'charging']) and
                  any(word in text_lower for word in ['?', 'which', 'what', 'how many', 'how much', 'list', 'names', 'name', 'are', 'is', 'have', 'do we', 'tell me', 'show me']) or
                  text_lower.endswith('?') or 'we have' in text_lower or 'do we' in text_lower or 'are they' in text_lower):
                intent = 'infrastructure_query'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): infrastructure_query detected")
            # Priority 5: System analysis
            elif any(word in text_lower for word in ['analyze', 'status', 'health', 'report', 'overview', 'check']):
                intent = 'system_analysis'
            # Priority 6: Emergency
            elif any(word in text_lower for word in ['help', 'emergency', 'urgent', 'crisis']):
                intent = 'emergency'
            # Priority 7: Greetings
            elif any(word in text_lower for word in ['hi', 'hello', 'hey', 'greetings']):
                intent = 'greeting'
            # Priority 8: Any question pattern (ends with ?, or starts with question words)
            elif (text_lower.strip().endswith('?') or
                  any(text_lower.startswith(word) for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you', 'could you', 'will you', 'do you', 'are you', 'is there', 'are there'])):
                intent = 'conversational'
                print(f"[ULTRA CHATBOT] Rule-based (no-OpenAI): conversational detected (question pattern)")
            else:
                intent = 'general_conversation'

        # Extract location entities with PRECISE matching for all substations
        location_found = False

        # EXACT matching first - highest priority (prioritize longer matches)
        exact_matches = []
        for location, data in self.manhattan_locations.items():
            # Check if the ENTIRE location name is present as a complete phrase
            if location in text_lower:
                exact_matches.append((location, data, len(location)))
                print(f"[ULTRA CHATBOT] Direct exact match found: '{location}' in '{text_lower}'")

        if exact_matches:
            # Sort by length descending to prioritize longer matches
            exact_matches.sort(key=lambda x: x[2], reverse=True)
            location, data, _ = exact_matches[0]
            entities['location'] = location
            entities['location_data'] = data
            location_found = True
            print(f"[ULTRA CHATBOT] Exact location match: '{location}'")

        # Alias matching - second priority (be more restrictive)
        if not location_found:
            alias_matches = []
            for location, data in self.manhattan_locations.items():
                for alias in data.get('aliases', []):
                    # Only match aliases that are at least 4 characters OR are the full location name
                    if len(alias) >= 4 and alias in text_lower:
                        alias_matches.append((location, data, alias, len(alias)))

            if alias_matches:
                # Sort by alias length descending to prioritize longer matches
                alias_matches.sort(key=lambda x: x[3], reverse=True)
                location, data, matched_alias, _ = alias_matches[0]
                entities['location'] = location
                entities['location_data'] = data
                location_found = True
                print(f"[ULTRA CHATBOT] Alias match: '{matched_alias}' -> '{location}'")

        # Word-based matching - third priority (be more precise)
        if not location_found:
            for location, data in self.manhattan_locations.items():
                location_words = location.split()
                # Check if ALL significant words are present
                if len(location_words) == 1:
                    # Single word locations need exact match
                    if location_words[0] in text_lower:
                        entities['location'] = location
                        entities['location_data'] = data
                        location_found = True
                        print(f"[ULTRA CHATBOT] Single word match: '{location}'")
                        break
                elif len(location_words) >= 2:
                    # Multi-word locations need at least 2 words to match
                    matched_words = [word for word in location_words if len(word) > 3 and word in text_lower]
                    if len(matched_words) >= 2:
                        entities['location'] = location
                        entities['location_data'] = data
                        location_found = True
                        print(f"[ULTRA CHATBOT] Multi-word match: '{matched_words}' -> '{location}'")

        # FUZZY MATCHING - fourth priority (handle typos)
        if not location_found:
            def levenshtein_distance(s1, s2):
                """Calculate Levenshtein distance between two strings"""
                if len(s1) < len(s2):
                    return levenshtein_distance(s2, s1)
                if len(s2) == 0:
                    return len(s1)
                previous_row = range(len(s2) + 1)
                for i, c1 in enumerate(s1):
                    current_row = [i + 1]
                    for j, c2 in enumerate(s2):
                        insertions = previous_row[j + 1] + 1
                        deletions = current_row[j] + 1
                        substitutions = previous_row[j] + (c1 != c2)
                        current_row.append(min(insertions, deletions, substitutions))
                    previous_row = current_row
                return previous_row[-1]

            # Extract potential location words from user input
            words = text_lower.split()
            best_match = None
            best_distance = float('inf')

            # Check all locations and aliases for fuzzy matches
            for location, data in self.manhattan_locations.items():
                # Check main location name
                for word_combo in [' '.join(words[i:i+len(location.split())]) for i in range(len(words))]:
                    distance = levenshtein_distance(location, word_combo)
                    # Allow max 2 character difference for fuzzy match
                    if distance <= 2 and distance < best_distance:
                        best_match = (location, data, word_combo, distance)
                        best_distance = distance

                # Check aliases
                for alias in data.get('aliases', []):
                    for word in words:
                        distance = levenshtein_distance(alias, word)
                        if distance <= 2 and distance < best_distance:
                            best_match = (location, data, word, distance)
                            best_distance = distance

            if best_match:
                location, data, matched_text, distance = best_match
                entities['location'] = location
                entities['location_data'] = data
                location_found = True
                print(f"[ULTRA CHATBOT] Fuzzy match: '{matched_text}' -> '{location}' (distance: {distance})")

        # Extract action entities with NATURAL LANGUAGE UNDERSTANDING
        # Turn off/disable/fail synonyms
        turn_off_variants = ['turn off', 'turn of', 'disable', 'fail', 'shut down', 'shut off',
                            'switch off', 'power down', 'take down', 'offline', 'stop', 'disconnect']

        # Turn on/enable/restore synonyms
        turn_on_variants = ['turn on', 'enable', 'restore', 'bring back', 'power up', 'switch on',
                           'start up', 'bring online', 'reactivate', 'fix', 'repair', 'recover']

        # Show/display/location synonyms
        show_variants = ['show', 'display', 'find', 'locate', 'where is', 'take me to',
                        'go to', 'navigate to', 'zoom to', 'focus on', 'highlight']

        # Activate/start synonyms
        activate_variants = ['activate', 'start', 'begin', 'initiate', 'launch', 'trigger', 'deploy']

        # Deactivate/stop synonyms
        deactivate_variants = ['deactivate', 'stop', 'halt', 'shutdown', 'turn off', 'disable', 'cease', 'end']

        # Check for turn off actions
        if any(variant in text_lower for variant in turn_off_variants):
            entities['action'] = 'turn_off'
            print(f"[ULTRA CHATBOT] Detected turn_off action from: {[v for v in turn_off_variants if v in text_lower]}")

        # Check for turn on actions
        elif any(variant in text_lower for variant in turn_on_variants):
            entities['action'] = 'turn_on'
            print(f"[ULTRA CHATBOT] Detected turn_on action from: {[v for v in turn_on_variants if v in text_lower]}")

        # Check for show/location actions
        elif any(variant in text_lower for variant in show_variants):
            entities['action'] = 'show'
            print(f"[ULTRA CHATBOT] Detected show action from: {[v for v in show_variants if v in text_lower]}")

        # Check for activate actions
        elif any(variant in text_lower for variant in activate_variants):
            entities['action'] = 'activate'
            print(f"[ULTRA CHATBOT] Detected activate action from: {[v for v in activate_variants if v in text_lower]}")

        # Check for deactivate actions
        elif any(variant in text_lower for variant in deactivate_variants):
            entities['action'] = 'deactivate'
            print(f"[ULTRA CHATBOT] Detected deactivate action from: {[v for v in deactivate_variants if v in text_lower]}")

        else:
            # Default action inference based on context
            if any(word in text_lower for word in ['v2g', 'emergency', 'backup']):
                entities['action'] = 'activate'
            elif any(word in text_lower for word in ['status', 'info', 'state']):
                entities['action'] = 'status'

        # Update conversation context for future pronoun resolution
        self._update_conversation_context(text, intent, entities)

        return intent, entities

    async def _generate_ultra_intelligent_response(self, original_input: str, corrected_input: str,
                                                 corrections: List[str], best_match: Optional[str],
                                                 confidence: float, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ChatGPT-quality response with suggestions and corrections"""

        response_data = {
            'original_input': original_input,
            'corrected_input': corrected_input,
            'corrections_made': corrections,
            'best_match': best_match,
            'confidence': confidence,
            'intent': intent,
            'entities': entities,
            'timestamp': datetime.now().isoformat()
        }

        # CASE 1: Typos were corrected - show corrections and suggestions
        if corrections:
            suggestions_text = "I corrected some typos: " + ", ".join(corrections)
            if confidence > 0.7 and best_match:
                suggestions_text += f"\n\nDid you mean: '{best_match}'?"
        else:
            suggestions_text = ""

        # CASE 2: Low confidence match - provide suggestions
        if best_match and confidence < 0.5:
            suggestions = self._get_smart_suggestions(corrected_input, intent)
            suggestion_text = f"\n\nDid you mean one of these?\n" + "\n".join([f"- {s}" for s in suggestions[:3]])
        else:
            suggestion_text = ""

        # CASE 3: Execute the command if confidence is decent OR intent is clear
        if confidence > 0.5 or intent in ['start_vehicles', 'scenario_simulation', 'substation_control', 'location_query', 'v2g_control', 'power_grid_visualization', 'system_analysis', 'ev_charging_query']:
            execution_result = await self._execute_intelligent_command(corrected_input, intent, entities)

            response_text = execution_result.get('text', 'Command executed successfully')
            if suggestions_text:
                response_text = suggestions_text + "\n\n" + response_text

            # IMPORTANT: Transfer backend execution status from execution result
            backend_executed = execution_result.get('backend_executed', False)
            map_action = execution_result.get('map_action')
            system_changes = execution_result.get('system_changes', [])

            response_data.update({
                'success': True,
                'text': response_text,
                'execution_result': execution_result,
                'suggestions_provided': bool(suggestions_text or suggestion_text),
                'backend_executed': backend_executed,  # This was missing!
                'map_action': map_action,
                'system_changes': system_changes
            })

            print(f"[ULTRA CHATBOT] Command executed. Backend: {backend_executed}, Map action: {bool(map_action)}")

            return response_data

        # CASE 4: Use GPT-4 for conversational response
        gpt_response = await self._gpt4_conversational_response(original_input, corrected_input, intent, entities)

        # If GPT-4 gives a good response, use it. Otherwise provide helpful suggestions.
        if gpt_response and len(gpt_response.strip()) > 10:
            final_response = gpt_response
        else:
            # Provide helpful suggestions when we don't understand
            final_response = f"I'm not sure I understand '{original_input}'. Could you ask about:\n\n• Substation control (turn on/off substations)\n• System status and monitoring\n• Technical questions about power grids\n• Location information and mapping\n• V2G emergency power systems\n\nWhat would you like to know?"

        # Add context-aware suggestions
        smart_suggestions = self._get_smart_suggestions(corrected_input, intent)

        # Enhanced map action generation with better coordination detection
        map_action = None
        if intent == 'location_query' or any(word in corrected_input.lower() for word in ['show', 'display', 'zoom', 'location', 'where', 'map']):
            location = entities.get('location', 'times square')
            location_data = entities.get('location_data', self.manhattan_locations.get('times square', {}))

            map_action = {
                'type': 'focus_and_highlight',
                'location': location,
                'name': location_data.get('name', location.title()),
                'coordinates': location_data.get('coords', [-73.9857, 40.7549]),
                'zoom': 17,
                'highlight': True,
                'showConnections': True
            }

        # Add map updates for system actions
        map_updates = []
        if intent == 'substation_control' and entities.get('location_data'):
            map_updates = [{
                'action': 'highlight_failure' if entities.get('action') == 'turn_off' else 'highlight_restore',
                'location': entities.get('location_data', {}).get('name', ''),
                'coords': entities.get('location_data', {}).get('coords', [])
            }]

        response_data.update({
            'success': True,
            'text': final_response,
            'conversation_mode': True,
            'suggestions_provided': True,  # Always provide suggestions now
            'suggestions': self._track_suggestions(smart_suggestions[:4]),  # Add suggestions array for frontend
            'map_action': map_action,  # Enhanced map integration
            'map_updates': map_updates,  # Additional map updates
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        })

        return response_data

    def _get_smart_suggestions(self, input_text: str, intent: str) -> List[str]:
        """Generate intelligent suggestions based on context and conversation history"""

        suggestions = []

        # Context-aware suggestions based on recent activity
        last_location = self.conversation_context.get('last_mentioned_location')
        last_substation = self.conversation_context.get('last_mentioned_substation')
        last_action = self.conversation_context.get('last_action')

        if intent == 'substation_control':
            if last_substation and last_action != 'turn_off':
                suggestions.append(f"turn off {last_substation}")
            if last_substation and last_action != 'turn_on':
                suggestions.append(f"turn on {last_substation}")
            suggestions.extend([
                "check substation status",
                "show times square substation"
            ])
        elif intent == 'location_query':
            # Suggest related locations based on last mentioned location
            if last_location:
                # Find nearby locations
                if last_location in ['times square', 'penn station']:
                    suggestions.extend([f"show me {last_location} on map", "display broadway", "where is empire state building"])
                elif last_location in ['central park', 'murray hill']:
                    suggestions.extend([f"show me {last_location} on map", "display fifth avenue", "where is chrysler building"])
                else:
                    suggestions.append(f"show me {last_location} on map")

            suggestions.extend([
                "show me times square on map",
                "display central park location",
                "where is wall street"
            ])
        elif intent == 'v2g_control':
            suggestions.extend([
                "activate v2g system",
                "check v2g status",
                "show electric vehicles"
            ])
            if last_substation:
                suggestions.append(f"activate v2g for {last_substation}")
        elif intent == 'infrastructure_query':
            suggestions.extend([
                "how many substations do we have",
                "which substations are they",
                "list all EV stations",
                "what cables do we have"
            ])
        # Removed complex intents that weren't working - focusing on 100% working features
        elif intent == 'system_analysis':
            suggestions.extend([
                "analyze entire system",
                "system health report",
                "grid performance overview"
            ])
            if last_location:
                suggestions.append(f"analyze {last_location} area")
        else:
            # General ChatGPT-style suggestions based on context and system capabilities
            if any(word in input_text.lower() for word in ['hi', 'hello', 'help', 'what', 'can', 'do']):
                suggestions.extend([
                    "turn off times square substation",
                    "show me central park on map",
                    "activate v2g system",
                    "analyze system status",
                    "zoom to times square",
                    "highlight wall street",
                    "system health report",
                    "show all vehicles"
                ])
            elif any(word in input_text.lower() for word in ['map', 'location', 'where', 'show']):
                suggestions.extend([
                    "show times square on map",
                    "zoom to central park",
                    "highlight broadway area",
                    "pan to wall street",
                    "display manhattan overview"
                ])
            elif any(word in input_text.lower() for word in ['power', 'grid', 'electric']):
                suggestions.extend([
                    "analyze power grid status",
                    "check all substations",
                    "show power flow data",
                    "system performance report"
                ])
            else:
                # Most comprehensive suggestions for unclear queries
                suggestions.extend([
                    "turn off times square substation",
                    "show me central park on map",
                    "activate v2g system",
                    "zoom to times square",
                    "analyze system status",
                    "highlight broadway",
                    "system health report",
                    "show electric vehicles"
                ])

        return suggestions

    async def _execute_intelligent_command(self, command: str, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute commands intelligently based on intent and entities"""

        print(f"[EXECUTE COMMAND] Intent: '{intent}', Command: '{command}'")
        try:
            if intent == 'start_vehicles':
                # Start SUMO vehicles
                print(f"[EXECUTE COMMAND] → Routing to start_vehicles")
                return await self._execute_start_vehicles(command)
            elif intent == 'scenario_simulation':
                # Delegate to ai_chatbot.py for scenario handling
                print(f"[EXECUTE COMMAND] → Routing to scenario_simulation delegate")
                return self._delegate_to_scenario_handler(command)
            elif intent == 'substation_control':
                return await self._execute_substation_command(command, entities)
            elif intent == 'location_query':
                return await self._execute_location_command(command, entities)
            elif intent == 'v2g_control':
                return await self._execute_v2g_command(command, entities)
            elif intent == 'infrastructure_query':
                return await self._execute_infrastructure_query(command, entities)
            elif intent == 'system_analysis':
                return await self._execute_analysis_command(command, entities)
            elif intent == 'power_grid_visualization':
                return await self._execute_power_grid_visualization(command, entities)
            elif intent == 'ev_charging_query':
                return await self._execute_ev_charging_query(command, entities)
            else:
                # Smart suggestions for unrecognized commands
                return self._provide_smart_suggestions(command, intent)

        except Exception as e:
            return {'text': f"I encountered an issue: {str(e)}. Let me suggest alternatives."}

    async def _execute_start_vehicles(self, command: str) -> Dict[str, Any]:
        """Start SUMO vehicles"""
        try:
            import requests

            # Start SUMO
            start_resp = requests.post('http://127.0.0.1:5000/api/sumo/start', timeout=10)
            if start_resp.status_code == 200:
                # Wait a moment for SUMO to initialize
                import time
                time.sleep(2)

                # Spawn vehicles
                spawn_resp = requests.post('http://127.0.0.1:5000/api/sumo/spawn',
                                          json={'count': 50, 'ev_percentage': 70},
                                          timeout=15)

                if spawn_resp.status_code == 200:
                    return {
                        'success': True,
                        'text': '✅ **SUMO Started & Vehicles Spawned!**\n\n50 vehicles are now driving through Manhattan (35 EVs, 15 gas vehicles).\n\nYou can now run scenarios:\n• Type "run v2g scenario"\n• Type "trigger blackout scenario"',
                        'backend_executed': True
                    }
                else:
                    return {
                        'success': False,
                        'text': f'❌ Failed to spawn vehicles: {spawn_resp.text}',
                        'backend_error': True
                    }
            else:
                return {
                    'success': False,
                    'text': f'❌ Failed to start SUMO: {start_resp.text}',
                    'backend_error': True
                }

        except Exception as e:
            return {
                'success': False,
                'text': f'❌ Error starting vehicles: {str(e)}. Make sure the server is running.'
            }

    def _delegate_to_scenario_handler(self, command: str) -> Dict[str, Any]:
        """Delegate scenario commands to ai_chatbot.py"""
        command_lower = command.lower()
        print(f"[SCENARIO DELEGATE] Command: '{command_lower}'")

        # Determine scenario type with STRICT patterns
        v2g_scenario_phrases = ['v2g scenario', 'run v2g scenario', 'trigger v2g scenario', 'execute v2g scenario',
                               'show v2g scenario', 'demonstrate v2g', 'simulate v2g', 'v2g rescue scenario']
        blackout_scenario_phrases = ['blackout scenario', 'trigger blackout scenario', 'run blackout scenario',
                                    'citywide blackout scenario', 'execute blackout scenario', 'simulate blackout',
                                    'demonstrate blackout', 'show blackout scenario']

        if any(phrase in command_lower for phrase in v2g_scenario_phrases):
            print(f"[SCENARIO DELEGATE] ✅ V2G SCENARIO MATCHED! Returning [SCENARIO_PREP:v2g]")
            return {
                'success': True,
                'text': '[SCENARIO_PREP:v2g]',
                'backend_executed': False,  # Don't execute real V2G
                'is_scenario': True,
                'preparation_details': {
                    'vehicles_to_spawn': 50,  # FORCE 50 vehicles for V2G
                    'ev_percentage': 100,
                    'min_soc': 70,
                    'max_soc': 95
                }
            }
        elif any(phrase in command_lower for phrase in blackout_scenario_phrases):
            return {
                'success': True,
                'text': '[SCENARIO_PREP:blackout]',
                'backend_executed': False,  # Don't execute real blackout
                'is_scenario': True
            }
        else:
            # Fallback - shouldn't reach here
            return {
                'success': False,
                'text': 'Unknown scenario command. Available scenarios:\n• "run v2g scenario" - V2G emergency power demonstration\n• "trigger blackout scenario" - Citywide blackout simulation\n\nNote: Regular V2G activation uses "activate v2g" without "scenario"',
                'suggestions': ['run v2g scenario', 'trigger blackout scenario']
            }

    async def _execute_substation_command(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute substation control with REAL backend integration"""

        action = entities.get('action', 'turn_off')  # Default action
        location_data = entities.get('location_data')

        # Check for "restore all" or "turn on all" commands
        command_lower = command.lower()
        if any(phrase in command_lower for phrase in ['restore all', 'restore everything', 'turn on all', 'restore every', 'power up all']):
            try:
                import requests
                api_url = "http://127.0.0.1:5000/api/restore_all"
                print(f"[ULTRA CHATBOT] Restoring ALL substations: {api_url}")
                response = requests.post(api_url, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    restored_count = result.get('restored_count', 0)
                    print(f"[ULTRA CHATBOT] Restored all substations: {result}")

                    return {
                        'success': True,
                        'text': f"**ALL SYSTEMS RESTORED!** ✅\n\nRestored {restored_count} substations - Full grid power restored to Manhattan. All systems operational.",
                        'action': 'restore_all',
                        'system_changes': [f"{restored_count} substations restored", "Full grid operational"],
                        'backend_executed': True
                    }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: Failed to restore all substations. Backend error: {response.status_code}",
                        'backend_error': True
                    }
            except Exception as e:
                return {
                    'success': False,
                    'text': f'❌ Error restoring all substations: {str(e)}',
                    'error': str(e)
                }

        if not location_data:
            # Default to times square if no location specified
            location_data = self.manhattan_locations['times square']

        substation_name = location_data['name']
        location_name = location_data['name']

        try:
            # ACTUALLY CALL THE BACKEND API
            import requests

            if action == 'turn_off':
                # Call the real fail API
                api_url = f"http://127.0.0.1:5000/api/fail/{substation_name}"
                print(f"[ULTRA CHATBOT] Calling backend API: {api_url}")
                response = requests.post(api_url, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    print(f"[ULTRA CHATBOT] Backend response: {result}")

                    return {
                        'success': True,
                        'text': f"**SUBSTATION OFFLINE** - {location_name} substation has been turned OFF! Area affected, power disrupted.",
                        'action': 'substation_off',
                        'location': location_name,
                        'coordinates': location_data['coords'],
                        'system_changes': [f"{location_name} substation offline"],
                        'map_action': {
                            'type': 'highlight_failure',
                            'location': location_name,
                            'coordinates': location_data['coords'],
                            'name': f"{location_name} Substation - FAILED",
                            'highlight': True
                        },
                        'backend_executed': True
                    }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: Failed to turn off {location_name} substation. Backend error: {response.status_code}",
                        'backend_error': True
                    }

            else:  # turn_on / restore
                # Call the real restore API
                api_url = f"http://127.0.0.1:5000/api/restore/{substation_name}"
                print(f"[ULTRA CHATBOT] Calling backend API: {api_url}")
                response = requests.post(api_url, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    print(f"[ULTRA CHATBOT] Backend response: {result}")

                    return {
                        'success': True,
                        'text': f"**POWER RESTORED** - {location_name} substation is back ONLINE! All systems operational.",
                        'action': 'substation_on',
                        'location': location_name,
                        'coordinates': location_data['coords'],
                        'system_changes': [f"{location_name} substation restored"],
                        'map_action': {
                            'type': 'focus_and_highlight',
                            'location': location_name,
                            'coordinates': location_data['coords'],
                            'name': f"{location_name} Substation - RESTORED",
                            'highlight': True
                        },
                        'backend_executed': True
                    }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: Failed to restore {location_name} substation. Backend error: {response.status_code}",
                        'backend_error': True
                    }

        except Exception as e:
            print(f"[ULTRA CHATBOT] Backend API error: {str(e)}")
            return {
                'success': False,
                'text': f"ERROR: Could not execute substation command: {str(e)}. Check if the backend server is running.",
                'error': str(e)
            }

    async def _execute_location_command(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute location/map commands with intelligent understanding and map highlighting"""

        location_data = entities.get('location_data')

        if not location_data:
            return {
                'success': False,
                'text': "I couldn't identify a specific location. Could you be more specific? I know about Times Square, Penn Station, Grand Central, Murray Hill, Turtle Bay, Chelsea, Hell's Kitchen, and Midtown East.",
                'suggestions': ["show me times square", "show me penn station", "where is grand central"]
            }

        location_name = location_data['name']
        coordinates = location_data['coords']
        substation = location_data.get('substation', location_name)

        return {
            'success': True,
            'text': f"[PIN] **Showing {location_name} on map!** Coordinates: ({coordinates[1]:.4f}, {coordinates[0]:.4f}). This area is served by {substation} substation with {location_data.get('capacity_mva', 'unknown')}MVA capacity. Map highlighting active.",
            'location': location_name,
            'coordinates': coordinates,
            'backend_executed': True,  # This is a successful map action
            'map_action': {
                'type': 'focus_and_highlight',
                'location': location_name,
                'coordinates': coordinates,
                'name': f"{location_name} - {substation}",
                'zoom': 17,
                'highlight': True,
                'showConnections': True
            },
            'system_changes': [f"Map focused on {location_name}"]
        }

    async def _execute_ev_charging_query(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute EV charging station query - show EV stations near a substation"""

        location_data = entities.get('location_data')

        if not location_data:
            return {
                'success': False,
                'text': "I couldn't identify which substation you're asking about. Please specify a substation name.\n\nAvailable substations: Times Square, Penn Station, Grand Central, Murray Hill, Turtle Bay, Chelsea, Hell's Kitchen, Midtown East",
                'suggestions': ["show charging near times square", "show ev station near penn station"]
            }

        location_name = location_data['name']
        substation_name = location_data.get('substation', location_name)
        coordinates = location_data['coords']

        return {
            'success': True,
            'text': f"📍 **Showing EV Charging Station near {substation_name}!**\n\nEach substation has a dedicated EV charging station nearby. The map will zoom to {location_name} and highlight the associated EV charging station with connections.",
            'location': location_name,
            'coordinates': coordinates,
            'backend_executed': True,
            'map_action': {
                'type': 'show_ev_charging',
                'substation': substation_name,
                'location': location_name,
                'coordinates': coordinates,
                'zoom': 16,
                'highlight': True
            },
            'system_changes': [f"Showing EV station for {substation_name}"]
        }

    async def _execute_v2g_command(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute V2G commands - Can activate for any substation or all failed substations"""

        try:
            import requests

            failed_substations = self.system_state.get('failed_substations', [])
            v2g_enabled = self.system_state.get('v2g_enabled_substations', [])

            if entities.get('action') == 'activate' or 'activate' in command:
                # Check for "all" keyword to activate V2G for all failed substations
                activate_all = any(word in command.lower() for word in ['all', 'every', 'everything', 'all failed'])

                if activate_all and failed_substations:
                    # Activate V2G for ALL failed substations
                    activated_substations = []
                    for sub_name in failed_substations:
                        api_url = f"http://127.0.0.1:5000/api/v2g/enable/{sub_name}"
                        print(f"[ULTRA CHATBOT] Activating V2G for {sub_name}: {api_url}")
                        response = requests.post(api_url, timeout=10)
                        if response.status_code == 200:
                            activated_substations.append(sub_name)

                    if activated_substations:
                        return {
                            'success': True,
                            'text': f"**V2G ACTIVATED FOR ALL FAILED SUBSTATIONS!** ({len(activated_substations)} substations)\n\n✅ V2G enabled for: {', '.join(activated_substations)}\n\nElectric vehicles are being dispatched to provide emergency power backup.",
                            'system_changes': [f"V2G enabled for {len(activated_substations)} failed substations"],
                            'backend_executed': True
                        }
                    else:
                        return {
                            'success': False,
                            'text': "Failed to activate V2G for any substations. Check backend status.",
                            'backend_executed': True
                        }

                # Check if there are failed substations that can use V2G
                if not failed_substations:
                    # Allow V2G activation even for operational substations (for testing/demo)
                    if entities.get('location_data'):
                        target_substation = entities['location_data']['substation']
                        return {
                            'success': True,
                            'text': f"NOTE: {target_substation} is operational. V2G is typically used for failed substations, but you can still activate it for testing purposes.",
                            'suggestions': [f"activate v2g for {target_substation}"],
                            'backend_executed': True
                        }
                    else:
                        return {
                            'success': True,
                            'text': f"INFO: All {len(self.system_state['substations'])} substations are operational. V2G is typically activated when substations fail. You can:\n• Fail a substation first, then activate V2G\n• Activate V2G for a specific substation for testing",
                            'suggestions': ["fail times square", "activate v2g for times square"],
                            'backend_executed': True
                        }

                # Determine which substation to activate V2G for
                target_substation = None
                if entities.get('location_data'):
                    substation_name = entities['location_data']['substation']
                    target_substation = substation_name  # Allow any substation, not just failed ones

                # If no specific substation mentioned, use the first failed one
                if not target_substation and failed_substations:
                    target_substation = failed_substations[0]

                if target_substation:
                    # Use the correct V2G enable endpoint for specific substation
                    api_url = f"http://127.0.0.1:5000/api/v2g/enable/{target_substation}"
                    print(f"[ULTRA CHATBOT] Activating V2G for failed substation: {api_url}")
                    response = requests.post(api_url, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        print(f"[ULTRA CHATBOT] V2G API response: {result}")

                        return {
                            'success': True,
                            'text': f"**V2G ACTIVATED FOR {target_substation.upper()}**! Electric vehicles are being dispatched to provide emergency power to the failed substation. V2G toggle enabled on control panel.",
                            'v2g_result': result,
                            'system_changes': [f"V2G enabled for {target_substation}", "V2G toggle activated"],
                            'backend_executed': True,
                            'map_action': {
                                'type': 'highlight_v2g_activation',
                                'substation': target_substation,
                                'coordinates': entities.get('location_data', {}).get('coords', [-73.9857, 40.7580]),
                                'name': f"{target_substation} V2G Activated"
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'text': f"ERROR: Failed to activate V2G for {target_substation}. Backend error: {response.status_code}. Check if substation is actually failed.",
                            'backend_error': True
                        }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: No failed substations found to activate V2G. Current failed substations: {', '.join(failed_substations) if failed_substations else 'None'}",
                        'system_info': f"V2G requires failed substations to work"
                    }

            elif entities.get('action') == 'deactivate' or any(word in command for word in ['deactivate', 'disable', 'stop', 'shutdown', 'turn off']):
                # Handle V2G deactivation
                if not v2g_enabled:
                    return {
                        'success': True,
                        'text': f"V2G system is already inactive. No V2G sessions are currently running.",
                        'system_info': f"V2G enabled substations: None",
                        'backend_executed': True
                    }

                # Determine which substation to deactivate V2G for
                target_substation = None
                if entities.get('location_data'):
                    substation_name = entities['location_data']['substation']
                    if substation_name in v2g_enabled:
                        target_substation = substation_name

                # If no specific substation mentioned, use the first enabled one
                if not target_substation and v2g_enabled:
                    target_substation = v2g_enabled[0]

                if target_substation:
                    # Use the V2G disable endpoint for specific substation
                    api_url = f"http://127.0.0.1:5000/api/v2g/disable/{target_substation}"
                    print(f"[ULTRA CHATBOT] Deactivating V2G for substation: {api_url}")
                    response = requests.post(api_url, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        print(f"[ULTRA CHATBOT] V2G Disable API response: {result}")

                        return {
                            'success': True,
                            'text': f"**V2G DEACTIVATED FOR {target_substation.upper()}**! Electric vehicles have been released and are no longer providing emergency power. V2G toggle disabled on control panel.",
                            'v2g_result': result,
                            'system_changes': [f"V2G disabled for {target_substation}", "V2G toggle deactivated"],
                            'backend_executed': True,
                            'map_action': {
                                'type': 'highlight_v2g_deactivation',
                                'substation': target_substation,
                                'coordinates': entities.get('location_data', {}).get('coords', [-73.9857, 40.7580]),
                                'name': f"{target_substation} V2G Deactivated"
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'text': f"ERROR: Failed to deactivate V2G for {target_substation}. Backend error: {response.status_code}.",
                            'backend_error': True
                        }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: No active V2G sessions found to deactivate. Current V2G enabled substations: {', '.join(v2g_enabled) if v2g_enabled else 'None'}",
                        'system_info': f"No V2G sessions are currently active"
                    }

            else:
                # Get V2G status and explain system intelligently
                api_url = "http://127.0.0.1:5000/api/v2g/status"
                print(f"[ULTRA CHATBOT] Calling V2G status API: {api_url}")
                response = requests.get(api_url, timeout=10)

                if response.status_code == 200:
                    status = response.json()

                    active_sessions = status.get('active_sessions', 0)
                    total_power = status.get('total_power_kw', 0)
                    total_earnings = status.get('total_earnings', 0)
                    enabled_substations = status.get('enabled_substations', [])

                    if not failed_substations:
                        status_text = f" **V2G SYSTEM STANDBY** - All {len(self.system_state['substations'])} substations operational. V2G ready for emergency deployment if any substation fails."
                    elif enabled_substations:
                        status_text = f" **V2G EMERGENCY ACTIVE** - Responding to {len(enabled_substations)} failed substations: {', '.join(enabled_substations)}. {active_sessions} vehicles providing {total_power:.1f}kW emergency power."
                    else:
                        status_text = f"**V2G NEEDED** - {len(failed_substations)} substations failed ({', '.join(failed_substations)}) but V2G not yet activated. Emergency power backup available."

                    return {
                        'success': True,
                        'text': status_text + f"\\n\\n**Current Stats**: {active_sessions} vehicles active - ${total_earnings:.2f} earned - Rate: ${status.get('current_rate', 0):.2f}/kWh",
                        'v2g_status': status,
                        'system_context': {
                            'failed_substations': failed_substations,
                            'v2g_enabled': enabled_substations,
                            'total_substations': len(self.system_state['substations'])
                        },
                        'backend_executed': True
                    }
                else:
                    return {
                        'success': False,
                        'text': f"ERROR: Failed to get V2G status. Backend error: {response.status_code}",
                        'backend_error': True
                    }

        except Exception as e:
            print(f"[ULTRA CHATBOT] V2G API error: {str(e)}")
            return {
                'success': False,
                'text': f"ERROR: Could not execute V2G command: {str(e)}. Check if the backend server is running.",
                'error': str(e)
            }

    async def _execute_analysis_command(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system analysis with REAL backend data"""

        try:
            import requests

            # Get real system status from backend
            api_url = "http://127.0.0.1:5000/api/status"
            print(f"[ULTRA CHATBOT] Calling system status API: {api_url}")
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                system_data = response.json()
                print(f"[ULTRA CHATBOT] System status: {system_data}")

                # Get V2G status too
                try:
                    v2g_response = requests.get("http://127.0.0.1:5000/api/v2g/status", timeout=5)
                    v2g_data = v2g_response.json() if v2g_response.status_code == 200 else {}
                except:
                    v2g_data = {}

                substations_online = system_data.get('substations_online', 0)
                total_substations = system_data.get('total_substations', 0)
                traffic_lights = system_data.get('traffic_lights_powered', 0)
                ev_stations = system_data.get('ev_stations_operational', 0)
                v2g_capacity = v2g_data.get('total_power_kw', 0)
                total_load = system_data.get('total_load_mw', 0)

                return {
                    'success': True,
                    'text': f" **REAL-TIME SYSTEM ANALYSIS**:\n- **Substations**: {substations_online}/{total_substations} online\n- **Traffic Lights**: {traffic_lights} powered\n- **EV Stations**: {ev_stations} operational\n- **V2G Power**: {v2g_capacity:.1f}kW available\n- **Grid Load**: {total_load:.1f}MW\n- **System Health**: {' EXCELLENT' if substations_online == total_substations else ' DEGRADED' if substations_online > 0 else ' CRITICAL'}",
                    'analysis_data': system_data,
                    'v2g_data': v2g_data,
                    'backend_executed': True,
                    'map_action': {
                        'type': 'show_system_overview',
                        'name': 'System Overview',
                        'highlight': True
                    }
                }
            else:
                # Fallback to local data if backend is unavailable
                return {
                    'success': True,
                    'text': f" **System Analysis** (Local Data):\n- Backend connection failed\n- Falling back to cached data\n- Check server connectivity",
                    'backend_error': True
                }

        except Exception as e:
            print(f"[ULTRA CHATBOT] System analysis error: {str(e)}")
            return {
                'success': False,
                'text': f"ERROR: Could not perform system analysis: {str(e)}. Check if the backend server is running.",
                'error': str(e)
            }

    async def _execute_infrastructure_query(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Answer ANY infrastructure question intelligently"""

        command_lower = command.lower()

        # Substation queries - handle ANY question format
        if any(word in command_lower for word in ['substations', 'substation']):
            if any(word in command_lower for word in ['which', 'what', 'list', 'names', 'name', 'are they', 'we have']):
                return {
                    'success': True,
                    'text': "The 8 substations are: Times Square, Penn Station, Grand Central, Wall Street, Murray Hill, Turtle Bay, Hell's Kitchen, and Midtown East."
                }
            elif any(word in command_lower for word in ['how many', 'count', 'number']):
                return {
                    'success': True,
                    'text': "We have 8 substations serving Manhattan."
                }
            else:
                # Any other substation question
                return {
                    'success': True,
                    'text': "We have 8 substations: Times Square (850MVA), Penn Station (900MVA), Grand Central (750MVA), Wall Street (800MVA), Murray Hill (650MVA), Turtle Bay (700MVA), Hell's Kitchen (750MVA), and Midtown East (800MVA)."
                }

        # EV station queries - handle ANY question format
        elif any(word in command_lower for word in ['ev', 'electric', 'charging', 'stations', 'station']):
            if any(word in command_lower for word in ['which', 'what', 'list', 'names', 'name', 'are they', 'we have']):
                return {
                    'success': True,
                    'text': "The EV stations are: EV-TS-001 (Times Square), EV-CP-001 (Central Park), EV-GC-001 (Grand Central), EV-WS-001 (Wall Street), EV-UE-001 (Upper East), EV-PS-001 (Penn Station), EV-HK-001 (Hell's Kitchen), and EV-ME-001 (Midtown East)."
                }
            elif any(word in command_lower for word in ['how many', 'count', 'number']):
                return {
                    'success': True,
                    'text': "We have 8 EV charging stations with 160 total charging ports."
                }
            else:
                # Any other EV question
                return {
                    'success': True,
                    'text': "We have 8 EV charging stations with 160 total ports: Times Square (20 ports), Central Park (15 ports), Grand Central (25 ports), Wall Street (18 ports), Upper East (12 ports), Penn Station (22 ports), Hell's Kitchen (16 ports), and Midtown East (20 ports)."
                }

        # Cable queries - handle ANY question format
        elif any(word in command_lower for word in ['cables', 'cable', 'wiring', 'lines']):
            return {
                'success': True,
                'text': "We have 42 miles of 13.8kV primary distribution cables and 127 miles of 480V secondary distribution cables, plus underground transmission lines connecting all substations."
            }

        # General infrastructure questions
        else:
            return {
                'success': True,
                'text': "Our Manhattan Power Grid includes 8 substations, 8 EV charging stations with 160 ports, 42 miles of primary cables, 127 miles of secondary cables, and comprehensive smart grid communication infrastructure."
            }

    async def _execute_power_grid_visualization(self, command: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Layer Control System for Power Grid using existing infrastructure"""

        command_lower = command.lower()

        # Individual substation network requests
        if ('network' in command_lower or 'power network' in command_lower) and any(sub in command_lower for sub in ['times square', 'penn station', 'grand central', 'wall street', 'murray hill', 'turtle bay', "hell's kitchen", 'hells kitchen', 'midtown east', 'chelsea', 'broadway', 'central park']):
            substation_name = None
            for sub in ['times square', 'penn station', 'grand central', 'wall street', 'murray hill', 'turtle bay', "hell's kitchen", 'hells kitchen', 'midtown east', 'chelsea', 'broadway', 'central park']:
                if sub in command_lower:
                    substation_name = sub.replace('hells kitchen', "hell's kitchen").title()
                    break

            if substation_name:
                return {
                    'success': True,
                    'text': f"🔌 **{substation_name.upper()} NETWORK**\n\n📍 **Focused on**: {substation_name} substation only\n⚡ **Showing**: Connected cables and EV station\n🎯 **View**: Isolated power distribution network\n\n🔌 Substation: {substation_name}\n⚡ 13.8kV primary cables (local area)\n🔗 480V secondary cables (local area)\n🚗 Associated EV charging station",
                    'map_action': {
                        'type': 'show_substation_network',
                        'substation_name': substation_name
                    }
                }

        # Specific layer control commands
        elif 'only 13.8' in command_lower or 'only primary' in command_lower or 'keep only 13.8' in command_lower:
            return {
                'success': True,
                'text': "⚡ **13.8kV PRIMARY CABLES ONLY**\n\n🔌 **Displaying**: Primary distribution network only\n⚡ **Layer**: 13.8kV transmission cables\n📊 **Coverage**: Manhattan primary power distribution\n\n💡 All other layers hidden - showing only primary power transmission infrastructure.",
                'map_action': {
                    'type': 'control_layers',
                    'layers': ['primary'],
                    'message': '13.8kV Primary Cables Only'
                }
            }

        elif 'only 480' in command_lower or 'only secondary' in command_lower or 'keep only 480' in command_lower:
            return {
                'success': True,
                'text': "🔗 **480V SECONDARY CABLES ONLY**\n\n🔌 **Displaying**: Secondary distribution network only\n🔗 **Layer**: 480V distribution cables\n📊 **Coverage**: Manhattan secondary power distribution\n\n💡 All other layers hidden - showing only secondary distribution infrastructure.",
                'map_action': {
                    'type': 'control_layers',
                    'layers': ['secondary'],
                    'message': '480V Secondary Cables Only'
                }
            }

        elif 'only substations' in command_lower or 'only substation' in command_lower:
            return {
                'success': True,
                'text': "🏭 **SUBSTATIONS ONLY**\n\n🔌 **Displaying**: Substation locations only\n📍 **Layer**: Manhattan power substations\n📊 **Count**: 8 major substations\n\n💡 All other layers hidden - showing only substation infrastructure.",
                'map_action': {
                    'type': 'control_layers',
                    'layers': ['substations'],
                    'message': 'Substations Only'
                }
            }

        elif 'only ev' in command_lower or 'only charging' in command_lower:
            return {
                'success': True,
                'text': "🚗 **EV STATIONS ONLY**\n\n🔌 **Displaying**: EV charging stations only\n🚗 **Layer**: Electric vehicle charging infrastructure\n📊 **Count**: 8 charging stations with 160 ports\n\n💡 All other layers hidden - showing only EV charging infrastructure.",
                'map_action': {
                    'type': 'control_layers',
                    'layers': ['ev'],
                    'message': 'EV Stations Only'
                }
            }

        # Show/Hide power grid commands
        elif any(phrase in command_lower for phrase in ['hide power grid', 'turn off power grid', 'hide it', 'hide grid', 'turn it off', 'hide all']):
            return {
                'success': True,
                'text': "🔌 **POWER GRID HIDDEN**\n\n🚫 **All power infrastructure turned OFF**\n📱 **Layers Disabled**:\n  • Substations\n  • 13.8kV Primary Cables  \n  • 480V Secondary Cables\n  • EV Charging Stations\n\n💡 Use manual toggles or chat commands to show specific layers",
                'map_action': {
                    'type': 'hide_power_grid'
                }
            }

        # Full power grid visualization
        else:
            return {
                'success': True,
                'text': "⚡ **COMPLETE POWER GRID**\n\n🗺️ **Showing**: All power infrastructure\n🔌 **Layers Active**:\n  • Substations (8 locations)\n  • 13.8kV Primary Cables\n  • 480V Secondary Cables\n  • EV Charging Stations\n\n📊 **Full Network**: Complete Manhattan power distribution visualization",
                'map_action': {
                    'type': 'show_power_grid'
                }
            }

    def _provide_smart_suggestions(self, command: str, intent: str) -> Dict[str, Any]:
        """Provide smart suggestions for unrecognized commands"""
        command_lower = command.lower()

        # Common typos and similar words for power grid commands
        power_suggestions = []

        if any(word in command_lower for word in ['hde', 'hide', 'turn of', 'turn off', 'close', 'remove']):
            power_suggestions.extend([
                "hide power grid",
                "hide it",
                "turn off grid"
            ])

        if any(word in command_lower for word in ['show', 'display', 'see', 'view']):
            if any(word in command_lower for word in ['power', 'grid', 'cables', 'substations']):
                power_suggestions.extend([
                    "show power grid",
                    "show substations",
                    "only 13.8kV cables",
                    "only 480V cables"
                ])

        if any(word in command_lower for word in ['times', 'square', 'penn', 'central', 'grand']):
            power_suggestions.extend([
                "show power network of times square",
                "show power network of penn station",
                "show power network of grand central"
            ])

        if any(word in command_lower for word in ['substation', 'substations']):
            power_suggestions.extend([
                "only substations",
                "show all substations",
                "turn off times square substation"
            ])

        # General suggestions if no specific matches
        if not power_suggestions:
            power_suggestions = [
                "show power grid",
                "hide power grid",
                "only 13.8kV cables",
                "show power network of times square",
                "turn off times square substation"
            ]

        # Create response with suggestions
        suggestion_text = "🤖 **I'm not sure what you mean.** Did you mean:\n\n"
        for i, suggestion in enumerate(power_suggestions[:4], 1):
            suggestion_text += f"{i}. {suggestion}\n"

        suggestion_text += f"\n💡 **Original**: \"{command}\"\n"
        suggestion_text += "🎯 **Try typing more clearly or use one of the suggestions above**"

        return {
            'success': True,
            'text': suggestion_text,
            'suggestions': power_suggestions[:4]
        }


    async def _gpt4_conversational_response(self, original_input: str, corrected_input: str,
                                          intent: str, entities: Dict[str, Any]) -> str:
        """Provide natural conversational responses using OpenAI or fallback"""

        # Get real system information for intelligent responses
        try:
            substations_online = sum(1 for sub in self.integrated_system.substations.values() if sub.get('operational', True))
            total_substations = len(self.integrated_system.substations)
            ev_stations = len(self.integrated_system.ev_stations)
            traffic_lights = len(self.integrated_system.traffic_lights)
            v2g_capacity = self.v2g_manager.get_v2g_status()['total_v2g_capacity_kw'] if self.v2g_manager else 0
        except:
            substations_online = 4
            total_substations = 4
            ev_stations = 12
            traffic_lights = 45
            v2g_capacity = 850.0

        # Try OpenAI first for advanced responses
        if openai_client:
            try:
                # Build conversation context for ChatGPT
                context_info = []
                if self.conversation_context['last_mentioned_location']:
                    context_info.append(f"Recently discussed location: {self.conversation_context['last_mentioned_location']}")
                if self.conversation_context['last_mentioned_substation']:
                    context_info.append(f"Recently discussed substation: {self.conversation_context['last_mentioned_substation']}")
                if self.conversation_context['last_action']:
                    context_info.append(f"Last action: {self.conversation_context['last_action']}")
                if self.conversation_context['conversation_topics']:
                    context_info.append(f"Recent topics: {', '.join(self.conversation_context['conversation_topics'][-3:])}")

                context_string = "\n".join(context_info) if context_info else "No previous context"

                system_context = f"""You are an intelligent Manhattan Power Grid assistant. Be concise, direct, and answer only what is asked.

CURRENT SYSTEM STATUS:
- Substations: {substations_online}/{total_substations} online
- EV Stations: {ev_stations} active with V2G capability
- Traffic Lights: {traffic_lights} connected
- V2G Capacity: {v2g_capacity:.0f}kW available

CONVERSATION CONTEXT:
{context_string}

MANHATTAN POWER GRID INFRASTRUCTURE:

SUBSTATIONS (8 total):
1. Times Square - 850MVA capacity, Commercial hub
2. Penn Station - 900MVA capacity, Transportation center
3. Grand Central - 750MVA capacity, Transportation/commercial
4. Wall Street - 800MVA capacity, Financial district
5. Murray Hill - 650MVA capacity, Residential area
6. Turtle Bay - 700MVA capacity, Mixed use area
7. Hell's Kitchen - 750MVA capacity, Residential area
8. Midtown East - 800MVA capacity, Commercial district

EV CHARGING STATIONS (8 total):
1. EV-TS-001 (Times Square) - 20 ports, Tesla Supercharger
2. EV-CP-001 (Central Park) - 15 ports, Universal fast charging
3. EV-GC-001 (Grand Central) - 25 ports, High-speed DC
4. EV-WS-001 (Wall Street) - 18 ports, Business district
5. EV-UE-001 (Upper East) - 12 ports, Residential
6. EV-PS-001 (Penn Station) - 22 ports, Transportation hub
7. EV-HK-001 (Hell's Kitchen) - 16 ports, Community charging
8. EV-ME-001 (Midtown East) - 20 ports, Commercial area

CABLE NETWORK:
- Primary Distribution: 13.8kV cables (42 miles total)
- Secondary Distribution: 480V cables (127 miles total)
- Underground transmission lines connecting all substations
- Smart grid communication cables throughout Manhattan

CORE CAPABILITIES:
• Control all 8 substations and show their exact locations
• Monitor all EV charging stations and their real-time usage
• Manage V2G emergency power systems with 160+ charging ports
• Show any location on interactive maps with precise coordinates
• Provide detailed infrastructure information and specifications
• Answer technical questions about power systems, electrical engineering, and grid operations

RESPONSE GUIDELINES:
• Answer the specific question asked - don't provide extra information unless requested
• Be direct and to the point
• If asked about system capabilities, explain what you can do
• If asked technical questions, provide clear explanations
• If the question is unclear or you don't understand, ask for clarification and offer helpful suggestions
• Use conversation context to understand pronouns and references
• Execute commands when requested

Examples of good responses:
Q: "What is a transformer?"
A: "A transformer uses electromagnetic induction to change voltage levels. It has primary and secondary coils around an iron core - AC current in the primary creates a magnetic field that induces voltage in the secondary."

Q: "Turn off times square"
A: [Execute command and confirm action]

Q: "How many substations do we have?"
A: "We have 8 substations serving Manhattan."

Q: "Which substations are they?"
A: "The 8 substations are: Times Square, Penn Station, Grand Central, Wall Street, Murray Hill, Turtle Bay, Hell's Kitchen, and Midtown East."

Q: "How many EV stations?"
A: "We have 8 EV charging stations with 160 total charging ports."

Q: "What are the EV station names?"
A: "The EV stations are: EV-TS-001 (Times Square), EV-CP-001 (Central Park), EV-GC-001 (Grand Central), EV-WS-001 (Wall Street), EV-UE-001 (Upper East), EV-PS-001 (Penn Station), EV-HK-001 (Hell's Kitchen), and EV-ME-001 (Midtown East)."

Q: "How many cables?"
A: "We have 42 miles of 13.8kV primary distribution cables and 127 miles of 480V secondary distribution cables, plus underground transmission lines connecting all substations."

Q: "Show me Times Square substation"
A: [Execute map action to show Times Square substation location]

Q: "Show me an EV station"
A: [Execute map action to show EV-TS-001 at Times Square with 20 Tesla Supercharger ports]

Q: "Activate V2G system"
A: [Execute V2G activation for failed substations]

Q: "Deactivate V2G system"
A: [Execute V2G deactivation and release vehicles]

Q: "Turn off V2G"
A: [Execute V2G shutdown and disable toggle]

Be helpful, accurate, and conversational while staying focused on the user's actual question."""

                # Build conversation history for better context
                messages = [{"role": "system", "content": system_context}]

                # Add recent conversation history (last 4 exchanges)
                recent_history = self.conversation_history[-8:] if len(self.conversation_history) > 8 else self.conversation_history
                for msg in recent_history:
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append(msg)

                # Add current input
                messages.append({"role": "user", "content": original_input})

                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=400,
                    temperature=0.8,
                    top_p=0.95,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"[ULTRA CHATBOT] OpenAI API error: {e}")
                # Continue to fallback

        input_lower = original_input.lower().strip()

        # Direct, focused responses like ChatGPT
        if any(word in input_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return f"Hello! I'm your Manhattan Power Grid assistant. How can I help you today?"

        elif any(word in input_lower for word in ['how are you', 'how do you do', 'whats up']):
            return f"I'm running well - all {substations_online} substations are online. What can I help you with?"

        elif any(word in input_lower for word in ['what can you do', 'capabilities', 'what do you do']):
            return f"I can control substations, show locations on maps, manage V2G systems, analyze grid performance, control time of day, set temperature, run test scenarios (morning rush, heatwave crisis, etc.), and answer technical questions about power systems.\n\n💡 Type **'help'** for a complete command reference. What would you like me to help with?"

        elif any(word in input_lower for word in ['status', 'overview', 'report', 'how is everything']):
            return f"Grid status: {substations_online}/{total_substations} substations online, {ev_stations} EV stations active, {v2g_capacity:.0f}kW V2G capacity available. All systems running normally."

        # Concise technical responses
        elif any(phrase in input_lower for phrase in ['how does', 'what is', 'explain', 'tell me about', 'how works']):
            if 'transformer' in input_lower:
                return "A transformer uses electromagnetic induction to change voltage levels. It has primary and secondary coils around an iron core - AC current in the primary creates a magnetic field that induces voltage in the secondary. The voltage ratio depends on the turns ratio between coils."

            elif 'substation' in input_lower:
                return f"Substations switch, transform, and protect electrical circuits. Manhattan has {total_substations} substations that step voltage up/down for efficient power distribution and isolate faults automatically using circuit breakers and protective relays."

            elif any(word in input_lower for word in ['v2g', 'vehicle to grid', 'electric vehicle']):
                return f"V2G allows electric vehicles to both charge from and discharge to the grid. Our {ev_stations} EV stations provide {v2g_capacity:.0f}kW of backup power for emergencies and help balance grid demand."

            else:
                # Let GPT-4 handle other technical questions
                return None

        # Handle specific power system questions
        elif any(word in input_lower for word in ['voltage', 'current', 'power', 'ac', 'dc']):
            if 'voltage' in input_lower:
                return "Voltage is electrical pressure that pushes current through circuits. Our grid uses different voltage levels: 13.8kV for distribution, 120/240V for buildings."
            elif 'current' in input_lower:
                return "Current is the flow of electrical charge, measured in amperes. In AC systems like ours, current alternates direction 60 times per second."
            elif 'power' in input_lower:
                return "Power is the rate of energy transfer, measured in watts (W) or kilowatts (kW). Power = Voltage × Current × Power Factor."
            elif 'ac' in input_lower:
                return "AC (Alternating Current) changes direction periodically. We use 60Hz AC because it's efficient for transmission and easy to transform to different voltages."
            elif 'dc' in input_lower:
                return "DC (Direct Current) flows in one direction. Used in batteries, electronics, and some modern transmission lines. Most grid power is AC."

        elif any(word in input_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome!"

        # Simple location info
        elif any(location in input_lower for location in ['times square', 'penn station', 'grand central', 'wall street', 'central park']):
            location_found = None
            for location in ['times square', 'penn station', 'grand central', 'wall street', 'central park']:
                if location in input_lower:
                    location_found = location
                    break

            if location_found:
                location_data = self.manhattan_locations.get(location_found, {})
                capacity = location_data.get('capacity_mva', 'N/A')
                return f"{location_found.title()} substation: {capacity} MVA capacity. I can show it on the map if you'd like."

        # Simple problem response
        elif any(word in input_lower for word in ['problem', 'issue', 'error', 'fault', 'trouble', 'broken', 'not working']):
            return "I can help troubleshoot grid issues. What specific problem are you experiencing?"

        # Let GPT-4 handle everything else or provide clarification
        else:
            # Return None to let GPT-4 handle complex questions intelligently
            return None

    async def _fallback_intelligent_response(self, original_input: str, error: str) -> Dict[str, Any]:
        """Intelligent fallback when something goes wrong"""

        suggestions = [
            "turn off times square substation",
            "show me central park location",
            "activate v2g system",
            "analyze system status"
        ]

        return {
            'success': True,
            'text': f"I had a small issue processing '{original_input}', but I'm still here to help! Here are some things you can try:\n\n" +
                   "\n".join([f"- {s}" for s in suggestions]),
            'fallback_mode': True,
            'suggestions': self._track_suggestions(suggestions),
            'error_info': error
        }

    def _detect_numbered_response(self, user_input: str) -> int:
        """Detect if user is responding with a number (1, 2, 3, etc.) referring to previous suggestions"""

        input_stripped = user_input.strip()

        # Check for simple number patterns
        if input_stripped.isdigit():
            number = int(input_stripped)
            if 1 <= number <= 10:  # Reasonable range for suggestions
                return number

        # Check for patterns like "1.", "option 1", "choice 2", "the first one", etc.
        import re

        # Pattern for "1.", "1)", "option 1", "choice 2", etc.
        patterns = [
            r'^(\d+)[.)]\s*$',                    # "1." or "1)"
            r'^(?:option|choice|number)\s*(\d+)$', # "option 1", "choice 2"
            r'^(\d+)(?:st|nd|rd|th)\s*(?:option|choice|one)?$', # "1st", "2nd option"
        ]

        for pattern in patterns:
            match = re.match(pattern, input_stripped, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                if 1 <= number <= 10:
                    return number

        # Handle text patterns like "the first one", "second", "third"
        text_numbers = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5
        }

        input_lower = input_stripped.lower()
        for text, number in text_numbers.items():
            if f"the {text}" in input_lower or input_lower == text:
                return number

        return None

    async def _handle_numbered_response(self, number: int) -> Dict[str, Any]:
        """Handle when user responds with a number referring to previous suggestions"""

        # Check if we have recent suggestions to reference
        if not self.last_suggestions or len(self.last_suggestions) < number:
            return {
                'success': False,
                'text': f"I don't have a suggestion #{number} to refer to. Could you please rephrase your request or ask me something specific?",
                'suggestions': self._track_suggestions([
                    "show me power grid status",
                    "turn off times square substation",
                    "where is central park?",
                    "activate v2g system"
                ]),
                'context_error': True
            }

        # Get the selected suggestion (convert to 0-based index)
        selected_suggestion = self.last_suggestions[number - 1]

        print(f"[CONVERSATION MEMORY] User selected suggestion #{number}: '{selected_suggestion}'")

        # Clear last suggestions since we're acting on one
        previous_suggestions = self.last_suggestions.copy()
        self.last_suggestions = []

        # Process the selected suggestion as if user typed it
        result = await self.chat(selected_suggestion)

        # Add context info to the result
        if isinstance(result, dict):
            result['conversation_context'] = {
                'user_selected_option': number,
                'original_suggestion': selected_suggestion,
                'all_previous_suggestions': previous_suggestions
            }

            # Update the response text to acknowledge the selection
            if result.get('text'):
                result['text'] = f"✅ **Selected option #{number}**: \"{selected_suggestion}\"\n\n{result['text']}"

        return result

    def _track_suggestions(self, suggestions: list) -> list:
        """Track suggestions for future numbered responses"""
        if suggestions:
            self.last_suggestions = suggestions.copy()
            print(f"[CONVERSATION MEMORY] Storing {len(suggestions)} suggestions: {suggestions}")
        return suggestions

    def _handle_map_command(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect and handle map control commands (zoom, camera, view)"""

        text_lower = user_input.lower().strip()

        # Zoom commands
        if any(phrase in text_lower for phrase in ['zoom in more', 'zoom way in', 'zoom closer']):
            return {
                'success': True,
                'text': 'Zooming in closer (4 levels)',
                'map_action': {
                    'type': 'zoom_change',
                    'delta': 4
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['zoom out more', 'zoom way out', 'zoom farther']):
            return {
                'success': True,
                'text': 'Zooming out farther (4 levels)',
                'map_action': {
                    'type': 'zoom_change',
                    'delta': -4
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['zoom in', 'zoom closer']):
            return {
                'success': True,
                'text': 'Zooming in (2 levels)',
                'map_action': {
                    'type': 'zoom_change',
                    'delta': 2
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['zoom out', 'zoom back']):
            return {
                'success': True,
                'text': 'Zooming out (2 levels)',
                'map_action': {
                    'type': 'zoom_change',
                    'delta': -2
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['reset zoom', 'default zoom', 'normal zoom']):
            return {
                'success': True,
                'text': 'Resetting zoom to default level',
                'map_action': {
                    'type': 'set_zoom',
                    'level': 12
                },
                'intent': 'map_control'
            }

        # Camera view commands
        elif any(phrase in text_lower for phrase in ['show overview', 'overview mode', 'overview view']):
            return {
                'success': True,
                'text': 'Showing Manhattan overview - centered on midtown',
                'map_action': {
                    'type': 'set_view',
                    'center': [-73.9857, 40.7580],  # Manhattan center (Times Square)
                    'zoom': 12,
                    'pitch': 45
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['bird view', 'birds eye', 'top view', 'aerial view', 'overhead view']):
            return {
                'success': True,
                'text': 'Switching to bird\'s eye view - top-down perspective',
                'map_action': {
                    'type': 'set_camera',
                    'pitch': 0,
                    'zoom': 11
                },
                'intent': 'map_control'
            }

        elif any(phrase in text_lower for phrase in ['tilt camera', 'angle view', 'tilted view', 'angled view', '3d view']):
            return {
                'success': True,
                'text': 'Tilting camera for angled 3D view',
                'map_action': {
                    'type': 'set_camera',
                    'pitch': 60,
                    'zoom': 14
                },
                'intent': 'map_control'
            }

        # No map command detected
        return None

    def _detect_confirmation_response(self, user_input: str) -> str:
        """Detect confirmation responses like 'yes confirm', 'cancel', 'yes', 'no' with typo tolerance"""

        input_lower = user_input.lower().strip()

        # Exact matches for confirmation phrases (including typos)
        confirmation_patterns = {
            # Confirm variations
            'yes confirm': 'confirm',
            'confirm': 'confirm',
            'confrim': 'confirm',  # typo
            'confrm': 'confirm',   # typo
            'comfirm': 'confirm',  # typo
            'cofirm': 'confirm',   # typo
            'yes': 'confirm',
            'y': 'confirm',
            'ok': 'confirm',
            'okay': 'confirm',
            'proceed': 'confirm',
            'do it': 'confirm',
            'go ahead': 'confirm',

            # Cancel variations
            'cancel': 'cancel',
            'cancle': 'cancel',    # typo
            'cancl': 'cancel',     # typo
            'cansel': 'cancel',    # typo
            'no': 'cancel',
            'n': 'cancel',
            'abort': 'cancel',
            'stop': 'cancel',
            'nevermind': 'cancel',
            'never mind': 'cancel'
        }

        return confirmation_patterns.get(input_lower)

    async def _handle_confirmation_response(self, response_type: str) -> Dict[str, Any]:
        """Handle confirmation responses for pending actions"""

        # Check if we have a pending confirmation
        if not self.pending_confirmations:
            return {
                'success': False,
                'text': "I don't have any pending actions to confirm. What would you like me to do?",
                'suggestions': self._track_suggestions([
                    "turn off times square substation",
                    "show me power grid status",
                    "where is central park?",
                    "activate v2g system"
                ]),
                'no_pending_action': True
            }

        # Get the most recent pending action
        latest_timestamp = max(self.pending_confirmations.keys())
        pending_action = self.pending_confirmations[latest_timestamp]

        if response_type == 'cancel':
            # Clear pending action and cancel
            del self.pending_confirmations[latest_timestamp]
            return {
                'success': True,
                'text': "❌ **Action Cancelled** - No changes were made to the system.",
                'suggestions': self._track_suggestions([
                    "show me system status",
                    "turn off a different substation",
                    "activate v2g system",
                    "where is penn station?"
                ]),
                'action_cancelled': True
            }

        elif response_type == 'confirm':
            # Execute the pending action
            del self.pending_confirmations[latest_timestamp]

            print(f"[CONFIRMATION] Executing confirmed action: {pending_action}")

            # Reconstruct the original command and execute it
            intent = pending_action['intent']
            entities = pending_action['entities']
            corrected_input = pending_action['corrected_input']

            # Execute the original action now that it's confirmed
            if intent == 'substation_control':
                result = await self._execute_substation_command(corrected_input, entities)
            elif intent == 'v2g_control':
                result = await self._execute_v2g_command(corrected_input, entities)
            elif intent == 'location_query':
                result = await self._execute_location_command(corrected_input, entities)
            else:
                result = {
                    'success': False,
                    'text': f"Unable to execute confirmed action for intent: {intent}",
                    'execution_error': True
                }

            # Add confirmation context to the result
            if isinstance(result, dict):
                result['confirmed_action'] = True
                result['original_request'] = corrected_input

                # Enhance success message
                if result.get('success') and result.get('text'):
                    result['text'] = f"✅ **CONFIRMED & EXECUTED**\n\n{result['text']}"

            return result

        else:
            return {
                'success': False,
                'text': f"I didn't understand your response '{response_type}'. Please type 'yes confirm' to proceed or 'cancel' to abort.",
                'suggestions': self._track_suggestions([
                    "yes confirm",
                    "cancel"
                ]),
                'confirmation_error': True
            }

def initialize_ultra_intelligent_chatbot(integrated_system, ml_engine, v2g_manager, flask_app):
    """Initialize the ULTRA INTELLIGENT CHATBOT"""

    try:
        chatbot = UltraIntelligentChatbot(integrated_system, ml_engine, v2g_manager, flask_app)
        print("[SUCCESS] ULTRA INTELLIGENT CHATBOT initialized - World-class conversational AI ready!")
        return chatbot
    except Exception as e:
        print(f"[ERROR] Failed to initialize Ultra Intelligent Chatbot: {str(e)}")
        return None
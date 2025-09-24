"""
WORLD-CLASS AI Chatbot for Manhattan Power Grid
Advanced conversational AI with deep system knowledge and V2G expertise
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ManhattanAIChatbot:
    """
    World-class AI chatbot with deep knowledge of:
    - Power grid operations
    - V2G (Vehicle-to-Grid) systems
    - Machine learning analytics
    - Traffic management
    - Energy trading
    - System optimization
    """
    
    def __init__(self, integrated_system, ml_engine, v2g_manager):
        self.integrated_system = integrated_system
        self.ml_engine = ml_engine
        self.v2g_manager = v2g_manager
        
        # Initialize OpenAI client
        self.openai_client = None
        if OpenAI and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Conversation memory
        self.conversation_history = []
        self.user_preferences = {}
        self.system_context = self._build_system_context()
        
        # Response templates for different scenarios
        self.response_templates = self._initialize_response_templates()
        
        # Knowledge base
        self.knowledge_base = self._build_knowledge_base()
        
        print("🤖 Manhattan AI Chatbot initialized with advanced capabilities")
    
    def _build_system_context(self):
        """Build comprehensive system context for AI responses"""
        return {
            "system_name": "Manhattan Power Grid",
            "capabilities": [
                "Real-time power grid monitoring",
                "V2G (Vehicle-to-Grid) energy trading",
                "Machine learning predictions",
                "Traffic light management",
                "EV charging optimization",
                "Substation control",
                "Anomaly detection",
                "Energy market analysis"
            ],
            "current_time": datetime.now().isoformat(),
            "system_status": "operational"
        }
    
    def _initialize_response_templates(self):
        """Initialize response templates for common scenarios"""
        return {
            "greeting": [
                "Hello! I'm your Manhattan Power Grid AI assistant. I can help you with power grid operations, V2G trading, ML insights, and system optimization. What would you like to know?",
                "Hi there! I'm here to help you manage the Manhattan Power Grid. I have deep knowledge of V2G systems, machine learning analytics, and grid operations. How can I assist you today?",
                "Welcome to the Manhattan Power Grid control center! I'm your AI assistant with expertise in energy trading, grid optimization, and V2G systems. What can I help you with?"
            ],
            "v2g_help": [
                "V2G (Vehicle-to-Grid) allows electric vehicles to discharge energy back to the grid during high demand periods. This creates revenue opportunities for vehicle owners while supporting grid stability.",
                "Our V2G system offers premium pricing (50x normal charging rates) for vehicles that provide energy during grid emergencies. Vehicles need 60%+ SOC to participate.",
                "V2G trading is currently active with dynamic pricing based on grid demand. I can show you current opportunities and optimal trading times."
            ],
            "ml_insights": [
                "Our ML models predict power demand, EV charging patterns, and V2G opportunities with 95%+ accuracy. They continuously learn from real-time data.",
                "The system uses advanced algorithms including Gradient Boosting, Neural Networks, and Isolation Forests for comprehensive grid analytics.",
                "ML predictions help optimize energy distribution, predict failures, and maximize V2G revenue opportunities."
            ],
            "system_status": [
                "The Manhattan Power Grid is currently operational with all systems functioning normally.",
                "I can provide real-time status updates on substations, traffic lights, EV stations, and V2G operations.",
                "The system includes advanced monitoring, predictive analytics, and automated optimization capabilities."
            ]
        }
    
    def _build_knowledge_base(self):
        """Build comprehensive knowledge base for all system components"""
        return {
            "v2g_concepts": {
                "definition": "Vehicle-to-Grid (V2G) technology allows electric vehicles to discharge stored energy back to the power grid",
                "benefits": ["Revenue generation for vehicle owners", "Grid stability support", "Peak demand management", "Renewable energy integration"],
                "requirements": ["60% minimum SOC", "V2G-compatible vehicle", "Grid connection", "Market participation"],
                "pricing": "Dynamic pricing based on grid demand, typically 50x normal charging rates during emergencies",
                "components": ["V2G stations", "Vehicle batteries", "Bidirectional chargers", "Energy management system"],
                "process": ["Vehicle recruitment", "Route optimization", "Energy discharge", "Revenue calculation"]
            },
            "power_grid": {
                "substations": {
                    "description": "Transform and distribute power throughout Manhattan",
                    "types": ["Primary substations", "Distribution substations", "Emergency substations"],
                    "components": ["Transformers", "Switchgear", "Protection systems", "Monitoring equipment"],
                    "voltage_levels": ["13.8kV primary", "480V secondary", "120V/240V residential"],
                    "capacity": "Ranges from 10MVA to 100MVA depending on location"
                },
                "distribution_lines": {
                    "primary": "13.8kV overhead and underground cables",
                    "secondary": "480V distribution to buildings",
                    "protection": "Circuit breakers, fuses, and protective relays",
                    "monitoring": "Real-time load monitoring and fault detection"
                },
                "load_management": {
                    "peak_demand": "Managed through load balancing and demand response",
                    "emergency_procedures": "Automatic load shedding and V2G activation",
                    "optimization": "ML-based load forecasting and distribution optimization"
                }
            },
            "traffic_management": {
                "traffic_lights": {
                    "description": "Smart traffic management with power monitoring and optimization",
                    "types": ["Fixed-time", "Actuated", "Adaptive", "Connected"],
                    "power_consumption": "LED lights with 80% energy savings",
                    "control_systems": ["SCADA integration", "Remote monitoring", "Emergency override"],
                    "optimization": "AI-based timing optimization for traffic flow"
                },
                "vehicle_simulation": {
                    "platform": "SUMO (Simulation of Urban Mobility)",
                    "vehicle_types": ["Gas cars", "Electric vehicles", "Buses", "Trucks"],
                    "routing": "Dynamic routing with real-time traffic conditions",
                    "behavior": "Realistic driving patterns and charging behavior"
                },
                "intersection_control": {
                    "adaptive_signals": "Real-time signal timing based on traffic flow",
                    "priority_systems": "Emergency vehicle and transit priority",
                    "coordination": "Network-wide signal coordination for optimal flow"
                }
            },
            "ev_charging": {
                "charging_stations": {
                    "types": ["Level 1 (120V)", "Level 2 (240V)", "DC Fast Charging (480V)"],
                    "locations": "Strategic placement throughout Manhattan",
                    "capacity": "Multiple charging ports per station",
                    "management": "Smart charging with load balancing"
                },
                "vehicle_types": {
                    "battery_electric": "Full electric vehicles with large battery packs",
                    "plug_in_hybrid": "Hybrid vehicles with charging capability",
                    "v2g_compatible": "Vehicles capable of bidirectional energy flow"
                },
                "charging_behavior": {
                    "soc_tracking": "State of charge monitoring and optimization",
                    "charging_patterns": "Peak hours, off-peak, and emergency charging",
                    "queue_management": "Intelligent queuing and reservation systems"
                }
            },
            "machine_learning": {
                "demand_prediction": {
                    "description": "Predicts power demand up to 24 hours ahead with 95%+ accuracy",
                    "algorithms": ["Gradient Boosting", "Neural Networks", "Time Series Analysis"],
                    "features": ["Historical demand", "Weather data", "Traffic patterns", "EV charging"],
                    "applications": ["Load planning", "Resource allocation", "Emergency preparedness"]
                },
                "anomaly_detection": {
                    "description": "Identifies grid anomalies and potential failures in real-time",
                    "methods": ["Isolation Forest", "Statistical analysis", "Pattern recognition"],
                    "detection_types": ["Equipment failures", "Load anomalies", "Traffic disruptions"],
                    "response": "Automatic alerts and recommended actions"
                },
                "optimization_models": {
                    "v2g_optimization": "Optimizes V2G pricing and vehicle routing for maximum revenue",
                    "traffic_optimization": "Optimizes traffic light timing for minimal congestion",
                    "energy_optimization": "Optimizes power distribution for maximum efficiency",
                    "predictive_maintenance": "Predicts equipment failures before they occur"
                }
            },
            "blackout_scenarios": {
                "emergency_protocols": {
                    "substation_failure": "Automatic V2G activation and load redistribution",
                    "grid_instability": "Emergency load shedding and stabilization procedures",
                    "elevator_emergencies": "V2G-powered elevator rescue operations",
                    "communication": "Emergency alert systems and public notifications"
                },
                "restoration_procedures": {
                    "priority_restoration": "Critical infrastructure first (hospitals, emergency services)",
                    "v2g_deployment": "Vehicle-to-grid emergency power activation",
                    "load_management": "Gradual load restoration to prevent cascading failures",
                    "monitoring": "Real-time monitoring of restoration progress"
                }
            },
            "system_monitoring": {
                "real_time_monitoring": {
                    "power_grid": "Continuous monitoring of voltage, current, and power flow",
                    "traffic_systems": "Real-time traffic flow and signal status monitoring",
                    "ev_charging": "Charging station status and utilization monitoring",
                    "v2g_operations": "V2G session monitoring and revenue tracking"
                },
                "alert_systems": {
                    "critical_alerts": "Immediate notification of system failures",
                    "warning_alerts": "Early warning of potential issues",
                    "maintenance_alerts": "Scheduled maintenance and equipment status",
                    "performance_alerts": "Performance degradation notifications"
                }
            }
        }
    
    def process_message(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Process user message and generate intelligent response
        """
        try:
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": user_message,
                "type": "user"
            })
            
            # Analyze message intent
            intent = self._analyze_intent(user_message)
            
            # Get system data
            system_data = self._get_current_system_data()
            
            # Generate response
            if self.openai_client and intent.get("use_openai", False):
                response = self._generate_openai_response(user_message, intent, system_data)
            else:
                response = self._generate_rule_based_response(user_message, intent, system_data)
            
            # Add response to history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": response["text"],
                "type": "assistant",
                "intent": intent,
                "data": response.get("data", {})
            })
            
            return response
            
        except Exception as e:
            error_response = {
                "text": f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question.",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }
            return error_response
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message intent using pattern matching and keywords"""
        message_lower = message.lower()
        
        # Comprehensive intent patterns for all system components
        intents = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"],
            "v2g_question": ["v2g", "vehicle to grid", "discharge", "energy trading", "revenue", "earnings", "bidirectional", "grid to vehicle"],
            "ml_question": ["ml", "machine learning", "prediction", "analytics", "insights", "model", "ai", "algorithm", "forecast"],
            "system_status": ["status", "operational", "working", "online", "offline", "failed", "health", "condition", "state"],
            "substation": ["substation", "power", "grid", "load", "capacity", "transformer", "switchgear", "distribution"],
            "traffic": ["traffic", "lights", "intersection", "vehicles", "cars", "sumo", "signal", "congestion", "flow"],
            "ev_charging": ["ev", "electric vehicle", "charging", "station", "battery", "soc", "plug", "charger"],
            "blackout": ["blackout", "outage", "emergency", "failure", "restoration", "elevator", "rescue", "scenario"],
            "monitoring": ["monitor", "watch", "track", "observe", "surveillance", "alert", "notification", "warning"],
            "anomalies": ["anomaly", "anomalies", "high", "medium", "low", "severity", "critical", "urgent", "alert", "problem", "issue", "error", "fault"],
            "optimization": ["optimize", "improve", "efficiency", "save", "reduce", "enhance", "maximize", "minimize"],
            "help": ["help", "assist", "support", "guide", "how to", "explain", "what is", "tell me about"],
            "data_request": ["show", "display", "get", "fetch", "data", "metrics", "stats", "numbers", "values"],
            "power_distribution": ["distribution", "voltage", "current", "power flow", "load balancing", "demand response"],
            "traffic_management": ["traffic management", "signal control", "intersection", "adaptive signals", "coordination"],
            "energy_market": ["energy market", "pricing", "rates", "cost", "economics", "financial", "profit"],
            "maintenance": ["maintenance", "repair", "service", "inspection", "upgrade", "replacement", "scheduled"],
            "safety": ["safety", "security", "protection", "emergency", "hazard", "risk", "precaution"],
            "performance": ["performance", "efficiency", "productivity", "throughput", "utilization", "effectiveness"],
            "configuration": ["configure", "setup", "settings", "parameters", "adjust", "modify", "change"],
            "reports": ["report", "summary", "analysis", "dashboard", "overview", "review", "assessment"]
        }
        
        # Check for intent matches
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Determine primary intent
        primary_intent = detected_intents[0] if detected_intents else "general"
        
        # Check if complex query requiring OpenAI
        complex_indicators = ["explain", "analyze", "compare", "why", "how", "what if", "recommend"]
        use_openai = any(indicator in message_lower for indicator in complex_indicators) or len(detected_intents) > 2
        
        return {
            "primary": primary_intent,
            "all": detected_intents,
            "use_openai": use_openai,
            "complexity": "high" if use_openai else "low"
        }
    
    def _get_current_system_data(self) -> Dict[str, Any]:
        """Get current system data for context"""
        try:
            # Get ML dashboard data
            ml_data = self.ml_engine.get_ml_dashboard_data() if self.ml_engine else {}
            
            # Get V2G data
            v2g_data = self.v2g_manager.get_v2g_dashboard_data() if self.v2g_manager else {}
            
            # Get basic system stats
            system_stats = {
                "substations_operational": sum(1 for s in self.integrated_system.substations.values() if s.get('operational', False)),
                "total_substations": len(self.integrated_system.substations),
                "traffic_lights_powered": sum(1 for tl in self.integrated_system.traffic_lights.values() if tl.get('powered', False)),
                "total_traffic_lights": len(self.integrated_system.traffic_lights),
                "ev_stations_operational": sum(1 for ev in self.integrated_system.ev_stations.values() if ev.get('operational', False)),
                "total_ev_stations": len(self.integrated_system.ev_stations),
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return {
                "system_stats": system_stats,
                "ml_data": ml_data,
                "v2g_data": v2g_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _generate_rule_based_response(self, message: str, intent: Dict, system_data: Dict) -> Dict[str, Any]:
        """Generate response using rule-based system"""
        primary_intent = intent["primary"]
        message_lower = message.lower()
        
        if primary_intent == "greeting":
            response_text = self.response_templates["greeting"][0]
            
        elif primary_intent == "v2g_question":
            v2g_data = system_data.get("v2g_data", {})
            if v2g_data:
                active_sessions = v2g_data.get("active_sessions", 0)
                total_earnings = v2g_data.get("total_earnings", 0)
                current_rate = v2g_data.get("current_rate", 0)
                
                response_text = f"""V2G System Status:
• Active V2G sessions: {active_sessions}
• Total earnings: ${total_earnings:.2f}
• Current rate: ${current_rate:.2f}/kWh
• Premium multiplier: 50x normal charging

V2G allows vehicles to discharge energy back to the grid during high demand, earning premium rates while supporting grid stability. Vehicles need 60%+ SOC to participate."""
            else:
                response_text = self.response_templates["v2g_help"][0]
                
        elif primary_intent == "ml_question":
            ml_data = system_data.get("ml_data", {})
            if ml_data and "metrics" in ml_data:
                metrics = ml_data["metrics"]
                response_text = f"""ML Analytics Status:
• Demand prediction accuracy: {100 - metrics.get('demand_mape', 5):.1f}%
• Patterns found: {metrics.get('patterns_found', 0)}
• Optimization savings: {metrics.get('optimization_savings', 0):.1f}%
• V2G revenue optimization: {metrics.get('v2g_revenue_optimization', 0):.1f}%

Our ML models continuously learn from real-time data to optimize grid operations and V2G trading."""
            else:
                response_text = self.response_templates["ml_insights"][0]
                
        elif primary_intent == "system_status":
            stats = system_data.get("system_stats", {})
            response_text = f"""System Status Overview:
• Substations: {stats.get('substations_operational', 0)}/{stats.get('total_substations', 0)} operational
• Traffic lights: {stats.get('traffic_lights_powered', 0)}/{stats.get('total_traffic_lights', 0)} powered
• EV stations: {stats.get('ev_stations_operational', 0)}/{stats.get('total_ev_stations', 0)} operational
• Current time: {stats.get('current_time', 'Unknown')}

All systems are functioning normally with advanced monitoring and optimization active."""
            
        elif primary_intent == "substation":
            stats = system_data.get("system_stats", {})
            response_text = f"""Power Grid & Substations:
• Operational substations: {stats.get('substations_operational', 0)}/{stats.get('total_substations', 0)}
• Voltage levels: 13.8kV primary, 480V secondary
• Load management: Real-time monitoring and optimization
• Protection systems: Circuit breakers, fuses, and relays
• Capacity: 10MVA to 100MVA depending on location

The power grid uses advanced monitoring and ML-based load forecasting for optimal distribution."""
            
        elif primary_intent == "traffic":
            stats = system_data.get("system_stats", {})
            response_text = f"""Traffic Management System:
• Powered traffic lights: {stats.get('traffic_lights_powered', 0)}/{stats.get('total_traffic_lights', 0)}
• Platform: SUMO (Simulation of Urban Mobility)
• Vehicle types: Gas cars, Electric vehicles, Buses, Trucks
• Control: Adaptive signals with AI-based optimization
• Features: Emergency vehicle priority, network coordination

The system uses real-time traffic flow analysis for optimal signal timing and congestion reduction."""
            
        elif primary_intent == "ev_charging":
            stats = system_data.get("system_stats", {})
            response_text = f"""EV Charging Infrastructure:
• Operational stations: {stats.get('ev_stations_operational', 0)}/{stats.get('total_ev_stations', 0)}
• Charging types: Level 1 (120V), Level 2 (240V), DC Fast (480V)
• Management: Smart charging with load balancing
• Features: SOC tracking, queue management, reservation systems
• V2G capability: Bidirectional energy flow for grid support

The charging network is strategically placed throughout Manhattan with intelligent management systems."""
            
        elif primary_intent == "blackout":
            response_text = """Blackout & Emergency Response:
• Emergency protocols: Automatic V2G activation and load redistribution
• Restoration procedures: Critical infrastructure first, gradual load restoration
• V2G deployment: Vehicle-to-grid emergency power activation
• Elevator rescue: V2G-powered elevator rescue operations
• Monitoring: Real-time restoration progress tracking

The system includes comprehensive emergency response capabilities with V2G-powered backup systems."""
            
        elif primary_intent == "monitoring":
            response_text = """System Monitoring & Alerts:
• Real-time monitoring: Power grid, traffic systems, EV charging, V2G operations
• Alert types: Critical, warning, maintenance, performance alerts
• Coverage: Voltage, current, power flow, traffic flow, charging status
• Response: Automatic notifications and recommended actions
• Integration: SCADA systems with remote monitoring capabilities

Advanced monitoring provides 24/7 system surveillance with proactive alerting."""
            
        elif primary_intent == "power_distribution":
            response_text = """Power Distribution System:
• Primary lines: 13.8kV overhead and underground cables
• Secondary lines: 480V distribution to buildings
• Load balancing: ML-based demand forecasting and distribution optimization
• Demand response: Peak demand management and load shedding
• Protection: Circuit breakers, fuses, and protective relays

The distribution system uses advanced load management and optimization algorithms."""
            
        elif primary_intent == "traffic_management":
            response_text = """Traffic Management & Control:
• Signal types: Fixed-time, Actuated, Adaptive, Connected
• Optimization: AI-based timing optimization for traffic flow
• Coordination: Network-wide signal coordination for optimal flow
• Priority systems: Emergency vehicle and transit priority
• Integration: SCADA integration with remote monitoring

The traffic management system uses advanced algorithms for optimal traffic flow and congestion reduction."""
            
        elif primary_intent == "energy_market":
            v2g_data = system_data.get("v2g_data", {})
            current_rate = v2g_data.get("current_rate", 0)
            response_text = f"""Energy Market & Pricing:
• Current V2G rate: ${current_rate:.2f}/kWh
• Pricing model: Dynamic pricing based on grid demand
• Premium multiplier: 50x normal charging rates during emergencies
• Market factors: Grid demand, V2G availability, time of day
• Revenue optimization: ML-based pricing and vehicle routing

The energy market uses dynamic pricing to optimize V2G participation and grid stability."""
            
        elif primary_intent == "maintenance":
            response_text = """Maintenance & Service:
• Predictive maintenance: ML-based equipment failure prediction
• Scheduled maintenance: Regular inspections and upgrades
• Service types: Equipment repair, replacement, and upgrades
• Monitoring: Real-time equipment health monitoring
• Optimization: Maintenance scheduling for minimal disruption

The system uses predictive analytics to optimize maintenance schedules and prevent failures."""
            
        elif primary_intent == "safety":
            response_text = """Safety & Security:
• Protection systems: Circuit breakers, fuses, and protective relays
• Emergency protocols: Automatic load shedding and V2G activation
• Hazard detection: Real-time monitoring of safety parameters
• Risk management: Proactive identification and mitigation
• Compliance: Industry safety standards and regulations

Comprehensive safety systems ensure reliable and secure grid operations."""
            
        elif primary_intent == "performance":
            ml_data = system_data.get("ml_data", {})
            metrics = ml_data.get("metrics", {})
            response_text = f"""System Performance:
• Demand prediction accuracy: {100 - metrics.get('demand_mape', 5):.1f}%
• Optimization savings: {metrics.get('optimization_savings', 0):.1f}%
• V2G revenue optimization: {metrics.get('v2g_revenue_optimization', 0):.1f}%
• Grid efficiency: Real-time monitoring and optimization
• Throughput: Continuous system performance tracking

Advanced analytics provide comprehensive performance monitoring and optimization."""
            
        elif primary_intent == "anomalies":
            ml_data = system_data.get("ml_data", {})
            anomalies = ml_data.get("anomalies", [])
            
            if anomalies:
                response_text = f"""🚨 System Anomalies Detected ({len(anomalies)} total):

"""
                for i, anomaly in enumerate(anomalies, 1):
                    severity_emoji = "🔴" if anomaly.get("severity") == "HIGH" else "🟡" if anomaly.get("severity") == "MEDIUM" else "🟢"
                    response_text += f"{severity_emoji} **{anomaly.get('type', 'Unknown')}** - {anomaly.get('severity', 'Unknown')} Severity\n"
                    response_text += f"   Description: {anomaly.get('description', 'No description')}\n"
                    response_text += f"   Score: {anomaly.get('score', 0):.3f}\n"
                    response_text += f"   Time: {anomaly.get('timestamp', 'Unknown')}\n\n"
                
                response_text += """**Recommended Actions:**
• Review high-severity anomalies immediately
• Check system logs for additional details
• Consider activating V2G emergency protocols if needed
• Monitor system stability closely"""
            else:
                response_text = """✅ No Anomalies Detected

The system is operating normally with no anomalies or issues detected. All components are functioning within expected parameters."""
            
        elif primary_intent == "data_request":
            # Provide specific data based on request
            if "v2g" in message_lower:
                v2g_data = system_data.get("v2g_data", {})
                response_text = f"V2G Data: {json.dumps(v2g_data, indent=2)}"
            elif "ml" in message_lower:
                ml_data = system_data.get("ml_data", {})
                response_text = f"ML Data: {json.dumps(ml_data, indent=2)}"
            else:
                response_text = f"System Data: {json.dumps(system_data, indent=2)}"
                
        elif primary_intent == "help":
            response_text = """I can help you with all aspects of the Manhattan Power Grid system:

🔌 **Power Grid**: Substations, distribution, load management, voltage levels
⚡ **V2G Systems**: Energy trading, revenue optimization, vehicle recruitment
🤖 **Machine Learning**: Predictions, analytics, anomaly detection, optimization
🚦 **Traffic Management**: Signal control, congestion reduction, vehicle simulation
🔋 **EV Charging**: Charging stations, battery management, SOC tracking
🚨 **Emergency Response**: Blackout scenarios, restoration procedures, V2G activation
📊 **Monitoring**: Real-time monitoring, alerts, performance tracking
💰 **Energy Market**: Pricing, rates, economics, financial optimization
🔧 **Maintenance**: Predictive maintenance, service scheduling, equipment health
🛡️ **Safety**: Protection systems, risk management, compliance

Just ask me about any of these topics!"""
                
        else:
            response_text = "I understand you're asking about the Manhattan Power Grid. I have comprehensive knowledge of all system components including power grid operations, V2G systems, ML analytics, traffic management, EV charging, emergency response, and more. Could you be more specific about what you'd like to know?"
        
        return {
            "text": response_text,
            "type": "response",
            "intent": primary_intent,
            "timestamp": datetime.now().isoformat(),
            "data": system_data
        }
    
    def _generate_openai_response(self, message: str, intent: Dict, system_data: Dict) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            # Build context for OpenAI
            context = self._build_openai_context(system_data)
            
            # Create system prompt
            system_prompt = f"""You are an expert AI assistant for the Manhattan Power Grid system. You have deep knowledge of:

- Power grid operations and substation management
- V2G (Vehicle-to-Grid) energy trading systems
- Machine learning analytics and predictions
- Traffic light management and optimization
- EV charging infrastructure
- Energy market dynamics and pricing

Current system context:
{json.dumps(context, indent=2)}

Provide helpful, accurate, and detailed responses about the power grid system. If asked about specific data, use the provided context. Be conversational but professional."""

            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            return {
                "text": response_text,
                "type": "ai_response",
                "intent": intent["primary"],
                "timestamp": datetime.now().isoformat(),
                "data": system_data
            }
            
        except Exception as e:
            # Fallback to rule-based response
            return self._generate_rule_based_response(message, intent, system_data)
    
    def _build_openai_context(self, system_data: Dict) -> Dict[str, Any]:
        """Build context for OpenAI API"""
        return {
            "system_overview": {
                "name": "Manhattan Power Grid",
                "status": "operational",
                "capabilities": ["V2G trading", "ML analytics", "Grid optimization", "Traffic management"]
            },
            "current_metrics": system_data.get("system_stats", {}),
            "v2g_status": system_data.get("v2g_data", {}),
            "ml_insights": system_data.get("ml_data", {}),
            "knowledge_base": self.knowledge_base
        }
    
    def get_conversation_history(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        """Get conversation history for a user"""
        user_history = [msg for msg in self.conversation_history if msg.get("user_id") == user_id]
        return user_history[-limit:] if limit else user_history
    
    def clear_conversation_history(self, user_id: str = "default"):
        """Clear conversation history for a user"""
        self.conversation_history = [msg for msg in self.conversation_history if msg.get("user_id") != user_id]
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get comprehensive system insights for the chatbot"""
        try:
            system_data = self._get_current_system_data()
            
            # Generate insights
            insights = {
                "grid_health": self._assess_grid_health(system_data),
                "v2g_opportunities": self._assess_v2g_opportunities(system_data),
                "ml_performance": self._assess_ml_performance(system_data),
                "recommendations": self._generate_recommendations(system_data)
            }
            
            return insights
            
        except Exception as e:
            return {"error": str(e)}
    
    def _assess_grid_health(self, system_data: Dict) -> Dict[str, Any]:
        """Assess overall grid health"""
        stats = system_data.get("system_stats", {})
        
        operational_subs = stats.get("substations_operational", 0)
        total_subs = stats.get("total_substations", 1)
        substation_health = operational_subs / total_subs
        
        powered_lights = stats.get("traffic_lights_powered", 0)
        total_lights = stats.get("total_traffic_lights", 1)
        traffic_health = powered_lights / total_lights
        
        overall_health = (substation_health + traffic_health) / 2
        
        return {
            "overall_score": round(overall_health * 100, 1),
            "substation_health": round(substation_health * 100, 1),
            "traffic_health": round(traffic_health * 100, 1),
            "status": "excellent" if overall_health > 0.9 else "good" if overall_health > 0.7 else "needs_attention"
        }
    
    def _assess_v2g_opportunities(self, system_data: Dict) -> Dict[str, Any]:
        """Assess V2G opportunities"""
        v2g_data = system_data.get("v2g_data", {})
        
        active_sessions = v2g_data.get("active_sessions", 0)
        total_earnings = v2g_data.get("total_earnings", 0)
        current_rate = v2g_data.get("current_rate", 0)
        
        return {
            "active_sessions": active_sessions,
            "total_earnings": total_earnings,
            "current_rate": current_rate,
            "opportunity_level": "high" if current_rate > 1.0 else "medium" if current_rate > 0.5 else "low"
        }
    
    def _assess_ml_performance(self, system_data: Dict) -> Dict[str, Any]:
        """Assess ML model performance"""
        ml_data = system_data.get("ml_data", {})
        metrics = ml_data.get("metrics", {})
        
        return {
            "demand_accuracy": 100 - metrics.get("demand_mape", 5),
            "patterns_found": metrics.get("patterns_found", 0),
            "optimization_savings": metrics.get("optimization_savings", 0),
            "performance_level": "excellent" if metrics.get("demand_mape", 5) < 3 else "good" if metrics.get("demand_mape", 5) < 7 else "needs_improvement"
        }
    
    def _generate_recommendations(self, system_data: Dict) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # Grid health recommendations
        grid_health = self._assess_grid_health(system_data)
        if grid_health["overall_score"] < 90:
            recommendations.append("Consider grid maintenance to improve overall health score")
        
        # V2G recommendations
        v2g_opps = self._assess_v2g_opportunities(system_data)
        if v2g_opps["opportunity_level"] == "high":
            recommendations.append("High V2G opportunity detected - consider activating more vehicles")
        
        # ML recommendations
        ml_perf = self._assess_ml_performance(system_data)
        if ml_perf["performance_level"] == "needs_improvement":
            recommendations.append("ML models may need retraining for better accuracy")
        
        return recommendations
    
    def get_v2g_insights(self) -> str:
        """Get V2G-specific insights and recommendations"""
        try:
            v2g_data = self.v2g_manager.get_v2g_dashboard_data() if self.v2g_manager else {}
            
            active_sessions = v2g_data.get("active_sessions", 0)
            total_earnings = v2g_data.get("total_earnings", 0)
            current_rate = v2g_data.get("current_rate", 0)
            
            insights = f"""V2G System Insights:
• Current active sessions: {active_sessions}
• Total revenue generated: ${total_earnings:.2f}
• Current market rate: ${current_rate:.2f}/kWh
• Premium multiplier: 50x normal charging rates

Recommendations:
• Monitor grid demand for optimal V2G activation timing
• Recruit vehicles with 60%+ SOC for maximum participation
• Use ML predictions to optimize pricing and vehicle routing
• Consider emergency scenarios for V2G deployment"""
            
            return insights
        except Exception as e:
            return f"V2G insights unavailable: {str(e)}"
    
    def get_optimization_opportunities(self) -> str:
        """Get system optimization opportunities"""
        try:
            ml_data = self.ml_engine.get_ml_dashboard_data() if self.ml_engine else {}
            optimization = ml_data.get("optimization", {})
            
            recommendations = optimization.get("recommendations", [])
            total_savings = optimization.get("total_savings_mw", 0)
            
            opportunities = f"""Optimization Opportunities:
• Potential savings: {total_savings:.1f} MW
• Active recommendations: {len(recommendations)}

Top recommendations:"""
            
            for i, rec in enumerate(recommendations[:3], 1):
                opportunities += f"\n{i}. {rec.get('action', 'N/A')} - {rec.get('priority', 'N/A')} priority"
            
            return opportunities
        except Exception as e:
            return f"Optimization opportunities unavailable: {str(e)}"
    
    def get_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        try:
            system_data = self._get_current_system_data()
            
            # Generate insights
            grid_health = self._assess_grid_health(system_data)
            v2g_insights = self.get_v2g_insights()
            optimization_opps = self.get_optimization_opportunities()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_overview": {
                    "grid_health": grid_health,
                    "v2g_status": self._assess_v2g_opportunities(system_data),
                    "ml_performance": self._assess_ml_performance(system_data)
                },
                "insights": {
                    "v2g_insights": v2g_insights,
                    "optimization_opportunities": optimization_opps
                },
                "recommendations": self._generate_recommendations(system_data),
                "summary": f"System operating at {grid_health['overall_score']:.1f}% efficiency with {len(self._generate_recommendations(system_data))} active recommendations."
            }
            
            return {
                "text": f"System Report Generated:\n\n{report['summary']}\n\nGrid Health: {grid_health['overall_score']:.1f}%\nV2G Status: {self._assess_v2g_opportunities(system_data)['opportunity_level']}\nML Performance: {self._assess_ml_performance(system_data)['performance_level']}",
                "type": "system_report",
                "timestamp": datetime.now().isoformat(),
                "data": report
            }
        except Exception as e:
            return {
                "text": f"System report generation failed: {str(e)}",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_v2g_optimization(self, optimization_type: str = "general") -> Dict[str, Any]:
        """Get V2G optimization recommendations"""
        try:
            v2g_data = self.v2g_manager.get_v2g_dashboard_data() if self.v2g_manager else {}
            
            if optimization_type == "revenue":
                recommendations = [
                    "Activate V2G during peak demand hours (5-8 PM)",
                    "Recruit vehicles with 80%+ SOC for maximum energy output",
                    "Optimize pricing based on grid demand forecasts",
                    "Coordinate with traffic management for efficient vehicle routing"
                ]
            elif optimization_type == "grid_stability":
                recommendations = [
                    "Deploy V2G vehicles near high-load substations",
                    "Maintain 20% V2G capacity reserve for emergencies",
                    "Coordinate with load balancing systems",
                    "Monitor grid frequency and voltage stability"
                ]
            else:
                recommendations = [
                    "Monitor grid demand patterns for optimal V2G timing",
                    "Balance revenue generation with grid stability",
                    "Use ML predictions for vehicle recruitment",
                    "Implement dynamic pricing based on real-time conditions"
                ]
            
            return {
                "text": f"V2G Optimization Recommendations ({optimization_type}):\n\n" + "\n".join(f"• {rec}" for rec in recommendations),
                "type": "v2g_optimization",
                "recommendations": recommendations,
                "potential_savings": {"revenue_increase": "15-25%", "grid_stability": "Improved", "efficiency": "10-20%"},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "text": f"V2G optimization analysis failed: {str(e)}",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_predictions(self, prediction_type: str = "demand", timeframe: str = "1h") -> Dict[str, Any]:
        """Get system predictions"""
        try:
            if prediction_type == "demand":
                predictions = self.ml_engine.predict_power_demand(next_hours=6) if self.ml_engine else []
                pred_text = "Power Demand Predictions (Next 6 Hours):\n\n"
                for pred in predictions[:3]:
                    pred_text += f"• Hour {pred['hour']}: {pred['predicted_mw']:.1f} MW (±{pred['confidence_upper'] - pred['predicted_mw']:.1f} MW)\n"
            elif prediction_type == "v2g":
                v2g_opps = self.ml_engine.predict_v2g_opportunities(time_horizon_hours=24) if self.ml_engine else []
                pred_text = "V2G Opportunity Predictions:\n\n"
                for opp in v2g_opps[:3]:
                    pred_text += f"• {opp['timestamp']}: {opp['recommendation']}\n"
            else:
                pred_text = "Prediction type not supported. Available types: demand, v2g"
            
            return {
                "text": pred_text,
                "type": "predictions",
                "data": {"prediction_type": prediction_type, "timeframe": timeframe},
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "text": f"Prediction generation failed: {str(e)}",
                "type": "error",
                "timestamp": datetime.now().isoformat()
            }

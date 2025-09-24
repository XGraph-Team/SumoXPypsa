# API Reference

This directory contains complete API documentation for the Manhattan Power Grid simulation system.

## 🔗 Endpoints Overview

### System Monitoring
- `GET /api/status` - Complete system status
- `GET /api/network_state` - Network topology and states
- `GET /api/health` - Health check endpoint

### Vehicle Simulation
- `POST /api/sumo/start` - Start vehicle simulation
- `POST /api/sumo/stop` - Stop vehicle simulation
- `GET /api/sumo/status` - Simulation status
- `GET /api/vehicles` - Live vehicle data

### Power Grid Management
- `POST /api/fail/{substation}` - Trigger substation failure
- `POST /api/restore/{substation}` - Restore failed substation
- `GET /api/power_flow` - Current power flow analysis
- `GET /api/grid_metrics` - Grid performance metrics

### V2G Operations
- `POST /api/v2g/enable/{substation}` - Enable V2G for substation
- `POST /api/v2g/disable/{substation}` - Disable V2G
- `GET /api/v2g/status` - V2G system status
- `GET /api/v2g/transactions` - Energy trading transactions

### ML Analytics & AI
- `POST /api/ai/chat` - AI chatbot interaction
- `GET /api/ml/predictions` - Demand predictions
- `GET /api/ml/insights` - System insights
- `POST /api/ml/retrain` - Retrain ML models

## 📋 Response Formats

All API responses follow this standard format:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "2.0.0"
}
```

For errors:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid parameter value",
    "details": { ... }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## 🔐 Authentication

Currently, the API uses basic authentication for development. Production deployments should implement:

- JWT tokens for stateless authentication
- Rate limiting per user/API key
- HTTPS encryption for all requests
- Input validation and sanitization

## 📊 Rate Limiting

Development environment limits:
- 100 requests per minute per IP
- 1000 requests per hour per IP

Production limits (recommended):
- 300 requests per minute per authenticated user
- 10,000 requests per hour per user

## 🧪 Testing

Test the API using:

```bash
# Health check
curl http://localhost:5000/api/health

# System status
curl http://localhost:5000/api/status

# Start vehicle simulation
curl -X POST http://localhost:5000/api/sumo/start \
  -H "Content-Type: application/json" \
  -d '{"vehicle_count": 10, "ev_percentage": 0.7}'
```

## 📚 Detailed Documentation

- [System API](system.md) - Status and monitoring endpoints
- [Vehicle API](vehicles.md) - SUMO simulation controls
- [Power Grid API](power_grid.md) - Grid management operations
- [V2G API](v2g.md) - Vehicle-to-Grid operations
- [ML & AI API](ml_ai.md) - Analytics and chatbot endpoints
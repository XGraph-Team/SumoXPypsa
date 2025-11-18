"""
Integration module for Realistic Load Model and Scenario Controller
Adds API endpoints to Flask app
"""

from flask import jsonify, request


def integrate_scenario_controller(app, scenario_controller, load_model):
    """
    Add scenario control endpoints to Flask app
    """

    @app.route('/api/scenario/set_time', methods=['POST'])
    def set_time():
        """Set simulation time (hours, minutes, seconds)"""
        try:
            data = request.get_json()
            hour = float(data.get('hour', 12))
            minute = int(data.get('minute', 0))
            second = int(data.get('second', 0))

            result = scenario_controller.set_time(hour, minute, second)

            return jsonify({
                'success': True,
                **result
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/scenario/set_temperature', methods=['POST'])
    def set_temperature():
        """Set temperature"""
        try:
            data = request.get_json()
            temp_f = float(data.get('temperature', 72))

            result = scenario_controller.set_temperature(temp_f)

            return jsonify({
                'success': True,
                **result
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/scenario/add_vehicles', methods=['POST'])
    def add_vehicles():
        """Add vehicles and update EV loads"""
        try:
            data = request.get_json()
            count = int(data.get('count', 50))

            result = scenario_controller.add_vehicles(count)

            return jsonify({
                'success': True,
                **result
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/scenario/run_scenario', methods=['POST'])
    def run_scenario():
        """Run predefined scenario"""
        try:
            data = request.get_json()
            scenario_name = data.get('scenario')

            if not scenario_name:
                return jsonify({'success': False, 'error': 'No scenario specified'}), 400

            result = scenario_controller.run_scenario(scenario_name)

            return jsonify({
                'success': True,
                **result
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/scenario/status', methods=['GET'])
    def get_scenario_status():
        """Get current scenario status"""
        try:
            status = scenario_controller.get_system_status()
            return jsonify({
                'success': True,
                **status
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/forecast', methods=['GET'])
    def get_load_forecast():
        """Get load forecast"""
        try:
            hours = int(request.args.get('hours', 6))
            forecast = scenario_controller.get_load_forecast(hours)

            return jsonify({
                'success': True,
                'forecast': forecast
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/events', methods=['GET'])
    def get_events():
        """Get event log"""
        try:
            limit = int(request.args.get('limit', 50))
            events = scenario_controller.get_event_log(limit)

            return jsonify({
                'success': True,
                'events': events
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/restore_substation', methods=['POST'])
    def scenario_restore_substation():
        """Restore failed substation"""
        try:
            data = request.get_json()
            substation = data.get('substation')

            if not substation:
                return jsonify({'success': False, 'error': 'No substation specified'}), 400

            result = scenario_controller.restore_substation(substation)

            return jsonify({
                'success': True,
                **result
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    @app.route('/api/scenario/load_breakdown', methods=['GET'])
    def get_load_breakdown():
        """Get detailed load breakdown for a substation"""
        try:
            substation = request.args.get('substation')

            if not substation:
                # Return all substations
                breakdowns = {}
                for sub in scenario_controller.substation_monitors.keys():
                    breakdowns[sub] = load_model.get_load_breakdown(sub)

                return jsonify({
                    'success': True,
                    'breakdowns': breakdowns
                })

            breakdown = load_model.get_load_breakdown(substation)

            return jsonify({
                'success': True,
                **breakdown
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/dashboard', methods=['GET'])
    def get_dashboard_data():
        """Get all dashboard data"""
        try:
            data = scenario_controller.get_dashboard_data()

            return jsonify({
                'success': True,
                **data
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/scenarios', methods=['GET'])
    def list_scenarios():
        """List available scenarios"""
        scenarios = [
            {
                'name': 'rush_hour_stress_test',
                'description': '8:00 AM rush hour + 92°F heat + 100 EVs',
                'difficulty': 'HARD',
                'expected_failures': 1-2
            },
            {
                'name': 'evening_peak_v2g',
                'description': '6:00 PM peak + optimal V2G conditions',
                'difficulty': 'MEDIUM',
                'expected_failures': 0
            },
            {
                'name': 'winter_emergency',
                'description': '7:00 AM winter + 15°F extreme cold',
                'difficulty': 'HARD',
                'expected_failures': 1
            },
            {
                'name': 'summer_heatwave',
                'description': '3:00 PM + 98°F heatwave + max AC',
                'difficulty': 'EXTREME',
                'expected_failures': 2-3
            },
            {
                'name': 'late_night_low_load',
                'description': '3:00 AM + minimal load',
                'difficulty': 'EASY',
                'expected_failures': 0
            }
        ]

        return jsonify({
            'success': True,
            'scenarios': scenarios
        })

    @app.route('/api/scenario/monitoring/start', methods=['POST'])
    def start_monitoring():
        """Start automatic monitoring"""
        try:
            scenario_controller.start_auto_monitoring()
            return jsonify({'success': True, 'monitoring': True})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/scenario/monitoring/stop', methods=['POST'])
    def stop_monitoring():
        """Stop automatic monitoring"""
        try:
            scenario_controller.stop_auto_monitoring()
            return jsonify({'success': True, 'monitoring': False})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    print("✓ Scenario controller API endpoints added")

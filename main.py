from flask import Flask, request, jsonify, render_template
import numpy as np
from joblib import load
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Flask app initialization
app = Flask(__name__, template_folder="templates", static_folder="static")

# Load pre-trained prediction model
MODEL_FILE = "delivery_time_model.joblib"
try:
    model = load(MODEL_FILE)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Route for serving the dashboard
@app.route("/")
def dashboard():
    return render_template("index.html")

# Predict delivery time API
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # Extract and validate features
        vehicle_utilization = data.get("vehicle_utilization")
        temperature_celsius = data.get("temperature_celsius")
        weather_impact = data.get("weather_impact")

        if None in [vehicle_utilization, temperature_celsius, weather_impact]:
            return jsonify({"error": "Missing one or more input fields"}), 400

        features = np.array([[vehicle_utilization, temperature_celsius, weather_impact]])
        prediction = model.predict(features)
        return jsonify({"predicted_delivery_time": prediction[0]})

    except Exception as e:
        print(f"Error in /api/predict: {e}")
        return jsonify({"error": str(e)}), 500

# Solve VRP API
@app.route("/api/optimize_routes", methods=["POST"])
def optimize_routes():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']), data['num_vehicles'], data['depot']
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            data['vehicle_capacities'],
            True,
            "Capacity"
        )

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)
        if not solution:
            return jsonify({"error": "No solution found"}), 404

        routes = []
        for vehicle_id in range(manager.GetNumberOfVehicles()):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            routes.append(route)

        return jsonify({"routes": routes})

    except Exception as e:
        print(f"Error in /api/optimize_routes: {e}")
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)

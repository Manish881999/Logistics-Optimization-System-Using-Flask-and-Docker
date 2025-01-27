document.getElementById('predictForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const vehicleUtilization = parseFloat(document.getElementById('vehicle_utilization').value);
    const temperatureCelsius = parseFloat(document.getElementById('temperature_celsius').value);
    const weatherImpact = parseInt(document.getElementById('weather_impact').value);

    try {
        const response = await axios.post('/api/predict', {
            vehicle_utilization: vehicleUtilization,
            temperature_celsius: temperatureCelsius,
            weather_impact: weatherImpact,
        });
        document.getElementById('predictResult').innerText = `Predicted Delivery Time: ${response.data.predicted_delivery_time} mins`;
    } catch (error) {
        document.getElementById('predictResult').innerText = 'Error: Unable to predict delivery time.';
    }
});

document.getElementById('optimizeForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const routeData = JSON.parse(document.getElementById('routeData').value);

    try {
        const response = await axios.post('/api/optimize_routes', routeData);
        const routes = response.data.routes;

        document.getElementById('routeResult').innerText = `Optimized Routes: ${JSON.stringify(routes)}`;

        // Plot routes on map
        const map = L.map('map').setView([51.505, -0.09], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        routes.forEach((route, index) => {
            const polyline = L.polyline(route.map(loc => [loc.lat, loc.lng]), { color: 'blue' }).addTo(map);
            map.fitBounds(polyline.getBounds());
        });
    } catch (error) {
        document.getElementById('routeResult').innerText = 'Error: Unable to optimize routes.';
    }
});

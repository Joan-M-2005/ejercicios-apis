from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# REEMPLAZA ESTO CON LA CLAVE QUE COPIASTE DE OPENWEATHERMAP
WEATHER_API_KEY = '20ebd848f3e52531b97814651ce68843'

@app.route('/')
def index():
    return render_template('clima.html')

@app.route('/api/clima')
def obtener_clima():
    # Coordenadas preconfiguradas
    ciudades = {
        'dolores': {'lat': 21.1561, 'lon': -100.9308, 'nombre': 'Dolores Hidalgo'},
        'celaya': {'lat': 20.5280, 'lon': -100.8115, 'nombre': 'Celaya'},
        'salamanca': {'lat': 20.5732, 'lon': -101.1965, 'nombre': 'Salamanca'}
    }
    
    ciudad = ciudades['dolores']  # Ciudad por defecto para el proyecto
    
    try:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'lat': ciudad['lat'],
            'lon': ciudad['lon'],
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'es'
        }
        
        response = requests.get(url, params=params)
        clima = response.json()
        
        return jsonify({
            'ciudad': ciudad['nombre'],
            'pais': 'México',
            'temperatura': clima['main']['temp'],
            'descripcion': clima['weather'][0]['description'],
            'humedad': clima['main']['humidity'],
            'viento': clima['wind']['speed'],
            'icono': clima['weather'][0]['icon']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('lugares.html')

@app.route('/api/lugares')
def buscar_lugares():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    tipo = request.args.get('tipo', 'restaurant')
    radio = request.args.get('radio', 1000, type=int)
    
    # Mapeo de tipos a queries de OpenStreetMap
    tipos_osm = {
        'restaurant': 'amenity=restaurant',
        'hospital': 'amenity=hospital',
        'cafe': 'amenity=cafe',
        'farmacia': 'amenity=pharmacy',
        'tienda': 'shop=supermarket',
        'gasolinera': 'amenity=fuel',
        'banco': 'amenity=bank',
        'hotel': 'tourism=hotel'
    }
    
    query = tipos_osm.get(tipo, 'amenity=restaurant')
    
    # Consulta a la API de Overpass
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node[{query}](around:{radio},{lat},{lon});
      way[{query}](around:{radio},{lat},{lon});
    );
    out center;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=30)
        data = response.json()
        
        lugares = []
        for elemento in data['elements'][:20]:  # Limitamos a 20 resultados para no saturar
            if 'center' in elemento:
                coords = elemento['center']
            elif 'lat' in elemento:
                coords = {'lat': elemento['lat'], 'lon': elemento['lon']}
            else:
                continue
            
            tags = elemento.get('tags', {})
            lugares.append({
                'nombre': tags.get('name', 'Sin nombre'),
                'direccion': tags.get('addr:street', '') + ' ' + tags.get('addr:housenumber', ''),
                'lat': coords['lat'],
                'lon': coords['lon'],
                'tipo': tags.get('amenity') or tags.get('shop') or tags.get('tourism', ''),
                'telefono': tags.get('phone', ''),
                'horario': tags.get('opening_hours', '')
            })
        
        return jsonify(lugares)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
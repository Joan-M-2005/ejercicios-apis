from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os

app = Flask(__name__)

# Inicializar Firebase
if not firebase_admin._apps:
    if os.path.exists('firebase-credentials.json'):
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred, {
            # REEMPLAZA CON TU ENLACE DE FIREBASE
            'databaseURL': 'https://chatutng-f9908-default-rtdb.firebaseio.com' 
        })
    else:
        print("⚠️ No se encontró firebase-credentials.json")

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/mensajes', methods=['GET'])
def obtener_mensajes():
    """Obtener los últimos mensajes de forma segura"""
    try:
        ref = db.reference('mensajes')
        # Descargamos los datos normales en lugar de usar order_by_child
        # Esto evita errores si hay datos basuras en la base de datos
        mensajes = ref.get()
        
        mensajes_lista = []
        if mensajes:
            # Firebase puede devolver un diccionario o una lista, validamos ambos:
            if isinstance(mensajes, dict):
                for key, value in mensajes.items():
                    if isinstance(value, dict): # Filtramos que sí sea un mensaje válido
                        value['id'] = key
                        mensajes_lista.append(value)
            elif isinstance(mensajes, list):
                for i, value in enumerate(mensajes):
                    if isinstance(value, dict):
                        value['id'] = str(i)
                        mensajes_lista.append(value)
            
            # Ordenamos los mensajes por fecha directamente en Python
            mensajes_lista.sort(key=lambda x: x.get('timestamp', ''))
            
            # Devolvemos solo los últimos 50 mensajes
            return jsonify(mensajes_lista[-50:])
        
        return jsonify([])
        
    except Exception as e:
        print(f"\n❌ ERROR AL LEER MENSAJES: {e}\n")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mensajes', methods=['POST'])
def enviar_mensaje():
    """Enviar un nuevo mensaje"""
    data = request.json
    
    if not data.get('usuario') or not data.get('texto'):
        return jsonify({'error': 'Usuario y texto requeridos'}), 400
    
    try:
        ref = db.reference('mensajes')
        nuevo_mensaje = {
            'usuario': data['usuario'],
            'texto': data['texto'],
            'timestamp': datetime.now().isoformat(),
            'avatar': data.get('avatar', '👤')
        }
        
        # Guardar mensaje
        nueva_ref = ref.push(nuevo_mensaje)
        nuevo_mensaje['id'] = nueva_ref.key
        
        return jsonify(nuevo_mensaje), 201
        
    except Exception as e:
        print(f"\n❌ ERROR AL GUARDAR MENSAJE: {e}\n")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mensajes/<mensaje_id>', methods=['DELETE'])
def eliminar_mensaje(mensaje_id):
    try:
        ref = db.reference(f'mensajes/{mensaje_id}')
        ref.delete()
        return jsonify({'mensaje': 'Mensaje eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/online', methods=['POST'])
def registrar_usuario_online():
    data = request.json
    usuario = data.get('usuario')
    
    if not usuario:
        return jsonify({'error': 'Usuario requerido'}), 400
    
    try:
        ref = db.reference(f'usuarios_online/{usuario}')
        ref.set({
            'ultima_actividad': datetime.now().isoformat(),
            'online': True
        })
        return jsonify({'mensaje': 'Usuario registrado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/online', methods=['GET'])
def obtener_usuarios_online():
    try:
        ref = db.reference('usuarios_online')
        usuarios = ref.get()
        
        if usuarios:
            return jsonify(list(usuarios.keys()))
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔥 Firebase Chat App Iniciado")
    app.run(debug=True)
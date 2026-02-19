from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('reddit.html')

@app.route('/api/reddit/posts')
def obtener_posts_reddit():
    subreddit = request.args.get('subreddit', 'python')
    filtro = request.args.get('filtro', 'hot')  # hot, new, top
    limit = request.args.get('limit', 10, type=int)
    
    # Reddit permite llamadas sin autenticación (limitadas)
    url = f'https://www.reddit.com/r/{subreddit}/{filtro}.json'
    # Es vital enviar un User-Agent personalizado a Reddit para que no bloquee la petición
    headers = {'User-Agent': 'python:flask-educativo-utng:v1.0'}
    
    try:
        response = requests.get(url, headers=headers, params={'limit': limit})
        
        if response.status_code == 404:
            return jsonify({'error': 'Subreddit no encontrado o es privado'}), 404
        if response.status_code == 429:
            return jsonify({'error': 'Demasiadas peticiones a Reddit. Intenta más tarde.'}), 429
            
        data = response.json()
        
        posts = []
        for post in data['data']['children']:
            post_data = post['data']
            
            # Convertir timestamp a fecha legible
            fecha = datetime.fromtimestamp(post_data['created_utc'])
            
            posts.append({
                'titulo': post_data['title'],
                'autor': post_data['author'],
                'puntos': post_data['score'],
                'comentarios': post_data['num_comments'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'url_completa': post_data.get('url', ''),
                'fecha': fecha.strftime('%Y-%m-%d %H:%M'),
                'thumbnail': post_data.get('thumbnail') if post_data.get('thumbnail') not in ['self', 'default', ''] else None,
                'selftext': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else ''
            })
        
        return jsonify({
            'subreddit': subreddit,
            'posts': posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reddit/buscar')
def buscar_reddit():
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Consulta requerida'}), 400
    
    url = f'https://www.reddit.com/search.json'
    headers = {'User-Agent': 'python:flask-educativo-utng:v1.0'}
    params = {'q': query, 'limit': limit}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        resultados = []
        for post in data['data']['children']:
            post_data = post['data']
            fecha = datetime.fromtimestamp(post_data['created_utc'])
            
            resultados.append({
                'titulo': post_data['title'],
                'subreddit': post_data['subreddit'],
                'autor': post_data['author'],
                'puntos': post_data['score'],
                'comentarios': post_data['num_comments'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'fecha': fecha.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify(resultados)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
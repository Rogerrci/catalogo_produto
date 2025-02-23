from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/buscar_preco', methods=['POST'])
def buscar_preco():
    try:
        subprocess.run(['python', 'price_scraper1.py'], check=True)
        return jsonify({'message': 'Preços buscados com sucesso!'})
    except subprocess.CalledProcessError as e:
        return jsonify({'message': f'Erro ao buscar preços: {e}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

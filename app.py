from flask import Flask, render_template, request, redirect, url_for
import csv
from price_scraper1 import main as run_scraper

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('wishlist1.0.html')

@app.route('/run_scraper', methods=['POST'])
def run_scraper_route():
    run_scraper()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

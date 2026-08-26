from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# chemin vers le fichier csv
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'sent.csv')

def read_csv_data():
    """lit les données du csv et retourne une liste de dictionnaires"""
    data = []
    if not os.path.exists(CSV_PATH):
        return data
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def get_stats_by_date(data):
    """calcule les statistiques par date"""
    stats = defaultdict(int)
    for row in data:
        if row.get('status') == 'sent':
            date_str = row.get('ts', '')[:10]  # YYYY-MM-DD
            if date_str:
                stats[date_str] += 1
    return dict(stats)

def get_stats_by_company(data):
    """calcule les statistiques par entreprise"""
    stats = defaultdict(int)
    for row in data:
        if row.get('status') == 'sent':
            company = row.get('company', 'unknown')
            stats[company] += 1
    return dict(stats)

def get_stats_by_status(data):
    """calcule les statistiques par statut"""
    stats = defaultdict(int)
    for row in data:
        status = row.get('status', 'unknown')
        stats[status] += 1
    return dict(stats)

@app.route('/api/stats')
def get_stats():
    """api pour récupérer toutes les statistiques"""
    data = read_csv_data()
    
    stats_by_date = get_stats_by_date(data)
    stats_by_company = get_stats_by_company(data)
    stats_by_status = get_stats_by_status(data)
    
    # trier les entreprises par nombre de candidatures
    sorted_companies = sorted(stats_by_company.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # trier les dates
    sorted_dates = sorted(stats_by_date.items())
    
    # calculer les statistiques des 7 derniers jours
    seven_days_ago = datetime.now() - timedelta(days=7)
    last_7_days = {}
    for date_str, count in sorted_dates:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj >= seven_days_ago:
                last_7_days[date_str] = count
        except:
            pass
    
    # calculer les statistiques des 30 derniers jours
    thirty_days_ago = datetime.now() - timedelta(days=30)
    last_30_days = {}
    for date_str, count in sorted_dates:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj >= thirty_days_ago:
                last_30_days[date_str] = count
        except:
            pass
    
    return jsonify({
        'total_sent': stats_by_status.get('sent', 0),
        'total_errors': stats_by_status.get('error', 0),
        'total': len(data),
        'by_date': sorted_dates,
        'by_company': sorted_companies,
        'by_status': dict(stats_by_status),
        'last_7_days': sorted(last_7_days.items()),
        'last_30_days': sorted(last_30_days.items()),
        'recent_applications': data[:10]  # 10 dernières candidatures
    })

@app.route('/')
def index():
    """servir le frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """servir les fichiers statiques"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("🚀 dashboard lancé sur http://localhost:5001")
    app.run(debug=True, port=5001)

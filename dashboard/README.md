# Dashboard Candidatures

Dashboard web moderne pour visualiser les statistiques de vos candidatures envoyées par le bot.

## 🚀 Installation

1. **Installer les dépendances :**
```bash
cd dashboard
pip install -r requirements.txt
```

2. **Lancer le dashboard :**
```bash
python app.py
```

3. **Ouvrir le navigateur :**
```
http://localhost:5000
```

## 📊 Fonctionnalités

- **KPIs en temps réel :** Total des candidatures, envoyées, erreurs, taux de succès
- **Graphiques interactifs :**
  - Candidatures par date (30 derniers jours)
  - Candidatures par entreprise (Top 10)
  - Répartition par statut
  - Candidatures des 7 derniers jours
- **Tableau des dernières candidatures** avec détails
- **Design moderne** avec TailwindCSS et React

## 🛠 Technologies

- **Backend :** Flask (Python)
- **Frontend :** React + TailwindCSS
- **Graphiques :** Recharts
- **Données :** CSV logs/sent.csv

## 📈 Données

Le dashboard lit automatiquement le fichier `../logs/sent.csv` généré par le bot de candidatures.

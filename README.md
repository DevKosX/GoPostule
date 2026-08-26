# GoPostule

GoPostule est un bot qui vous permet d'envoyer des candidatures par email automatiquement depuis n'importe où avec votre adresse mail. 

Pour utiliser GoPostule, vous avez besoin de :
- Un IDE (éditeur de code)
- Une connexion internet
- Des offres d'emploi (fichier jobs.csv)

Une fois configuré, vous pourrez postuler automatiquement et visualiser vos statistiques sur un dashboard en temps réel.

## Installation

### 1. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Fichier `.env`
Créez un fichier `.env` à la racine du projet avec vos informations SMTP :

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASS=votre_mot_de_passe_application
SENDER_NAME=Votre Nom
REPLY_TO=votre_email@gmail.com
GITHUB_LINK=votre_lien_github
```

**Important pour Gmail :**
- N'utilisez PAS votre mot de passe Gmail normal
- Générez un **mot de passe d'application** : 
  1. Allez dans votre compte Google > Sécurité
  2. Activez la "Vérification en 2 étapes"
  3. Cherchez "Mots de passe d'application"
  4. Créez un nouveau mot de passe pour "Courrier"
  5. Utilisez ce mot de passe dans `SMTP_PASS`

### 2. Personnalisation des emails
Modifiez les fichiers dans `templates/` :
- `email_subject.txt` : Sujet de l'email (utilise `{{ company }}` et `{{ role }}`)
- `email_body.txt` : Corps de l'email (utilise `{{ company }}` et `{{ role }}`)

### 3. CV (optionnel)
Si vous voulez joindre un CV :
- Placez votre fichier `cv.pdf` dans le dossier `assets/`
- Modifiez `apply_bot.py` ligne 138 : `context_attachments = [ATTACH_CV]`

## Démarrage

### 1. Préparer les jobs
Remplissez `data/jobs.csv` avec les colonnes : `company,email,role,source_url`
```
company,email,role,source_url
EntrepriseExemple,contact@example.com,Développeur Python,https://example.com/job
```

### 2. Lancer le dashboard (optionnel, dans un terminal séparé)
Pour visualiser les statistiques en temps réel :
```bash
cd dashboard
python app.py
```
Puis ouvrez http://localhost:5001 dans votre navigateur

### 3. Lancer l'envoi des candidatures
Dans un autre terminal :
```bash
python apply_bot.py
```

## Fonctionnalités

- **Rate limiting** : 10 secondes entre chaque envoi
- **Logs** : Les envois sont tracés dans `logs/sent.csv`
- **Nettoyage automatique** : Les entrées de plus de 30 jours sont supprimées
- **Pas de re-doublons** : Vérifie si une candidature a déjà été envoyée
- **Dashboard** : Visualisation des statistiques en temps réel

## Bonnes pratiques

- Envois ciblés, 1-2 adresses max par entreprise
- Respect des CGU et du RGPD
- Personnalisez les templates pour votre profil

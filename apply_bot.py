# -----------------------------
# bot candidature – envoi automatique de candidatures
# objectif : envoyer automatiquement des candidatures
# avec gestion des délais (14j/30j)
# -----------------------------

import csv, os, smtplib, time, ssl
from email.message import EmailMessage
from jinja2 import Template
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# --- configuration des chemins & variables ---
BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env", override=True)

SMTP_HOST   = os.getenv("SMTP_HOST")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER   = os.getenv("SMTP_USER")
SMTP_PASS   = os.getenv("SMTP_PASS")
SENDER_NAME = os.getenv("SENDER_NAME", "Votre Nom")
REPLY_TO    = os.getenv("REPLY_TO", SMTP_USER)
# github_link retiré

ASSETS_DIR  = BASE / "assets"
TEMPLATES   = BASE / "templates"
DATA_JOBS   = BASE / "data" / "jobs.csv"
LOGS_SENT   = BASE / "logs" / "sent.csv"

# pièces jointes
ATTACH_CV   = ASSETS_DIR / "cv.pdf"

RATE_LIMIT_SECONDS = 10
DELAY_REPOST = 0  # jours d'attente minimum avant de repostuler (désactivé)
DELAY_CLEANUP = 30 # jours avant de supprimer une entrée de log (sans réponse)

# --- fonctions nouvelles / modifiées ---

def load_template(path: Path) -> Template:
    """charge un fichier texte et le transforme en template jinja2."""
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read())

def get_sent_logs(log_path: Path):
    """charge les logs existants, convertit les dates et supprime les anciennes entrées."""
    if not log_path.exists():
        return []
    
    logs = []
    # 1. lecture
    with open(log_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['ts_dt'] = datetime.strptime(row['ts'], "%Y-%m-%d %H:%M:%S")
                logs.append(row)
            except ValueError:
                continue

    # 2. nettoyage (règle 30 jours sans réponse)
    if logs:
        cutoff_date = datetime.now() - timedelta(days=DELAY_CLEANUP)
        
        filtered_logs = [
            log for log in logs 
            if log['ts_dt'] > cutoff_date or (log['status'] != "sent" and log['status'].startswith("r"))
        ]

        if len(filtered_logs) < len(logs):
            print(f"[cleanup] {len(logs) - len(filtered_logs)} anciennes candidatures (> {DELAY_CLEANUP} jours) nettoyées.")
            
            with open(log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows([{k: v for k, v in row.items() if k in reader.fieldnames} for row in filtered_logs])
        
        return filtered_logs
    return []

def can_send(logs: list, company: str, email: str, role: str) -> bool:
    """vérifie si on peut envoyer (règle 14 jours)."""
    
    for row in logs:
        if row.get("company") == company and row.get("email") == email and row.get("role") == role:
            time_since_last_sent = datetime.now() - row['ts_dt']
            
            if time_since_last_sent.days < DELAY_REPOST:
                return False
            
            return True
            
    return True

def append_log(log_path: Path, row: dict):
    """ajoute une entrée dans logs/sent.csv après chaque tentative d'envoi."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["company","email","role","status","ts"]
    write_header = not log_path.exists()
    
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def build_message(to_addr: str, subject_txt: str, body_txt: str, attachments: list):
    """construit un message emailmessage prêt à être envoyé via smtp."""
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = to_addr
    msg["Subject"] = subject_txt
    msg["Reply-To"] = REPLY_TO
    msg.set_content(body_txt)

    for p in attachments:
        if p and p.exists():
            with open(p, "rb") as f:
                data = f.read()
            maintype, subtype = "application", "pdf"
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=p.name)
    return msg

# --- fonction principale ---
def main():
    sent_logs = get_sent_logs(LOGS_SENT)
    
    subj_tpl = load_template(TEMPLATES / "email_subject.txt")
    body_tpl = load_template(TEMPLATES / "email_body.txt")

    # github_link retiré du contexte
    context_common = {
        "sender_name": SENDER_NAME,
        "reply_to": REPLY_TO,
    }

    context_attachments = []  # cv désactivé

    print(f"[info] tente de se connecter au serveur smtp: {SMTP_HOST}:{SMTP_PORT}")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(SMTP_USER, SMTP_PASS)
            print("[ok] connexion smtp réussie.")

            with open(DATA_JOBS, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for i, row in enumerate(reader, start=1):
                    company   = row.get("company","").strip()
                    to_email  = row.get("email","").strip()
                    role      = row.get("role","").strip()
                    source_url= row.get("source_url","").strip()

                    if not company or not to_email or not role:
                        print(f"[skip] ligne {i}: champs manquants.")
                        continue

                    if not can_send(sent_logs, company, to_email, role):
                        print(f"[skip] trop tôt pour relancer: {company} / {role} (< {DELAY_REPOST} jours).")
                        continue

                    ctx = {
                        **context_common,
                        "company": company,
                        "role": role,
                        "source_url": source_url or "(non précisé)",
                    }

                    subject = subj_tpl.render(**ctx)
                    body    = body_tpl.render(**ctx)
                    msg     = build_message(to_email, subject, body, context_attachments)

                    try:
                        server.send_message(msg)
                        print(f"[ok] {company} ({to_email}) – {role}")

                        append_log(LOGS_SENT, {
                            "company": company,
                            "email": to_email,
                            "role": role,
                            "status": "sent",
                            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })

                        time.sleep(RATE_LIMIT_SECONDS)

                    except Exception as e:
                        print(f"[err] {company} – {e}")
                        append_log(LOGS_SENT, {
                            "company": company,
                            "email": to_email,
                            "role": role,
                            "status": f"error: {e}",
                            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
                        
    except smtplib.SMTPAuthenticationError:
        print("\n[erreur fatale] échec de l'authentification smtp. vérifiez votre smtp_user et surtout le mot de passe d'application (smtp_pass) dans .env.")
    except Exception as e:
        print(f"\n[erreur fatale] problème de connexion ou autre: {e}")

if __name__ == "__main__":
    main()
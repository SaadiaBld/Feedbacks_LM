from prometheus_client import Counter, Summary, Gauge, start_http_server
from prometheus_client import CollectorRegistry, REGISTRY, push_to_gateway
import socket
import re

# -------------------------
# MÉTRIQUES PRINCIPALES
# -------------------------

# Total de verbatims analysés
VERBATIMS_ANALYZED = Counter('verbatims_analyzed_total', 'Total des verbatims analysés')

# Durée de traitement d’un verbatim
ANALYSIS_DURATION = Summary('verbatim_analysis_duration_seconds', 'Durée d’analyse d’un verbatim')

# Erreurs de parsing JSON dans la réponse de Claude
ERRORS_JSON = Counter('errors_json_total', "Nombre d'erreurs JSON")

# Nombre de verbatims avec réponse vide (None) de Claude
CLAUDE_EMPTY_RESPONSES = Counter('claude_response_empty_total', "Réponses vides retournées par Claude")

# Taille du dernier verbatim (en nombre de caractères)
CURRENT_VERBATIM_SIZE = Gauge('current_verbatim_size', 'Taille du verbatim actuellement analysé')

# Histogramme des tailles de verbatims (par classe)
VERBATIM_SIZE_BUCKET = Gauge('verbatims_by_length_bucket', 'Nombre de verbatims par taille', ['bucket'])

# Nouveaux thèmes détectés non présents dans la table topics
NEW_TOPICS_DETECTED = Counter('new_topics_detected_total', 'Nouveaux thèmes non reconnus par le modèle')

# Erreurs à l’insertion dans BigQuery
BQ_INSERT_ERRORS = Counter('bq_insert_errors_total', "Erreurs survenues lors de l'insertion dans BigQuery")

# Verbatims ignorés (trop courts, déjà traités, etc.)
VERBATIMS_SKIPPED = Counter('verbatims_skipped_total', "Verbatims ignorés dans le pipeline")

# Ratio de réponses Claude valides vs total appelés (à afficher en dashboard)
CLAUDE_SUCCESS_RATIO = Gauge('claude_call_success_ratio', "Ratio de succès des appels Claude (%)")

# -------------------------
# FONCTION D’EXPORT SERVER
# -------------------------

def monitor_start(port=8000):
    try:
        # on teste si le port est déjà utilisé
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                start_http_server(port)
                print(f"✅ Exporter Prometheus lancé sur http://localhost:{port}/metrics")
            else:
                print(f"ℹ️ Exporter Prometheus déjà en cours sur le port {port}")
    except Exception as e:
        print(f"⚠️ Impossible de démarrer Prometheus : {e}")


# -------------------------
# LOGIQUE DE MISE À JOUR DES MÉTRIQUES
# -------------------------

def log_analysis_metrics(verbatim_text: str, duration: float, error=False, empty=False, new_topics=None, bq_error=False):
    """
    Met à jour les métriques Prometheus après le traitement d’un verbatim.
    
    - verbatim_text : texte du verbatim
    - duration : durée d’analyse
    - error : True si erreur JSON
    - empty : True si réponse vide de Claude
    - new_topics : liste de thèmes non reconnus
    - bq_error : True si insertion BQ échouée
    """
    #VERBATIMS_ANALYZED.inc()
    ANALYSIS_DURATION.observe(duration)

    # Taille du verbatim (en brut)
    size = len(verbatim_text)
    CURRENT_VERBATIM_SIZE.set(size)

    # Classification par taille
    if size < 100:
        VERBATIM_SIZE_BUCKET.labels(bucket="court").inc()
    elif size < 300:
        VERBATIM_SIZE_BUCKET.labels(bucket="moyen").inc()
    else:
        VERBATIM_SIZE_BUCKET.labels(bucket="long").inc()

    if error:
        ERRORS_JSON.inc()

    if empty:
        CLAUDE_EMPTY_RESPONSES.inc()

    if new_topics:
        NEW_TOPICS_DETECTED.inc(len(new_topics))

    if bq_error:
        BQ_INSERT_ERRORS.inc()

    print(f"➡️ VERBATIMS_ANALYZED avant: {VERBATIMS_ANALYZED._value.get()}")
    VERBATIMS_ANALYZED.inc()
    print(f"➡️ VERBATIMS_ANALYZED après: {VERBATIMS_ANALYZED._value.get()}")


def update_claude_success_ratio(total_calls: int, total_valid: int):
    """
    Met à jour la métrique de ratio succès Claude.
    """
    if total_calls > 0:
        ratio = (total_valid / total_calls) * 100
        CLAUDE_SUCCESS_RATIO.set(ratio)


def push_metrics_to_gateway(job_name="verbatim_pipeline"):
    """
    Push toutes les métriques enregistrées vers le PushGateway.
    """
    try:
        push_to_gateway("http://pushgateway:9091", job=job_name, registry=REGISTRY)
        print(f"📡 Métriques poussées vers le PushGateway pour le job : {job_name}")
    except Exception as e:
        print(f"❌ Erreur lors du push Prometheus : {e}")


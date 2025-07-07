import pytest
from unittest.mock import patch, MagicMock
from project.api.analyze_and_insert import process_and_insert_all
from project.api.claude_interface import validate_claude_response

#proteger les imports airflow 
try:
    from airflow.models import DagBag
    from airflow.operators.python import PythonOperator
    airflow_installed = True
except ImportError:
    DagBag = None
    PythonOperator = None
    airflow_installed = False


@pytest.fixture(scope="module")
@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def dagbag():
    with patch("os.path.isfile", return_value=True), \
         patch("os.getenv", side_effect=lambda k, d=None: "dummy" if k in {"GOOGLE_APPLICATION_CREDENTIALS", "PROJECT_ID"} else d), \
         patch("api.analyze_and_insert.load_dotenv", return_value=True), \
         patch("api.analyze_and_insert.process_and_insert_all"):
        
        import dags.trustpilot_dag  # charger le dag pour s'assurer qu'il est importé
        return DagBag(dag_folder="/opt/airflow/dags", include_examples=False)


@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def test_dag_import(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    assert dag is not None, "Le DAG 'trustpilot_pipeline' n'a pas été trouvé."


# verifier que le dag a les taches attendues
@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def test_task_ids(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    expected_tasks = {"scrape_trustpilot_reviews", "analyze_and_insert"}
    for task_id in expected_tasks:
        assert task_id in dag.task_ids, f"Le task_id '{task_id}' est manquant"

# tester l'ordre des taches
@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def test_dependencies(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    assert dag is not None
    # Exemple concret : scrape → clean → analyze
    assert dag.get_task("clean_reviews").upstream_task_ids == {"scrape_trustpilot_reviews"}
    assert dag.get_task("analyze_and_insert").upstream_task_ids == {"clean_reviews"}

# tester que le dag est acyclique
@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def test_dag_is_acyclic():
    from airflow.models.dagbag import DagBag

    dagbag = DagBag(dag_folder="/opt/airflow/dags", include_examples=False)
    dag = dagbag.get_dag("trustpilot_pipeline")

    # Cette méthode interne recharge tous les DAGs et détecte les cycles
    assert dagbag.import_errors == {}, f"Import errors: {dagbag.import_errors}"
    assert dag is not None, "DAG trustpilot_pipeline introuvable"


# tester que la tache 'analyze_and_insert' est bien un python operator
@pytest.mark.skipif(not airflow_installed, reason="Airflow not installed")
def test_operator_type(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    task = dag.get_task("analyze_and_insert")
    assert isinstance(task, PythonOperator)

#tester la fonction process_and_instert_all pour valider que tout s'enchaîne correctement
def test_process_and_insert_all(mock_get_verbatims, mock_classify, mock_insert):
    # 1. Simuler les verbatims récupérés
    mock_get_verbatims.return_value = [
        {"review_id": "R1", "text": "Livraison lente", "date": "2024-01-01"}
    ]
    
    # 2. Simuler la réponse de Claude
    mock_classify.return_value = [
        {"topic": "Livraison", "score": 1, "label": "Insatisfaction"}
    ]
    
    # 3. Simuler l'insertion BigQuery
    mock_insert.return_value = None  # On vérifie juste que c'est bien appelé

    # 4. Appel réel
    process_and_insert_all()

    # 5. Vérifications
    mock_get_verbatims.assert_called_once()
    mock_classify.assert_called_once()
    mock_insert.assert_called_once()

# tester que les reponses de claude sont des json valides
# project/tests/test_claude_validation.py


def test_validate_claude_response_valid():
    data = [
        {"topic": "Produit", "score": 2, "label": "Neutre"},
        {"topic": "Prix", "score": 0, "label": "Insatisfaction"}
    ]
    assert validate_claude_response(data) == True

def test_validate_claude_response_invalid_missing_field():
    data = [
        {"topic": "Produit", "label": "Neutre"}  # score manquant
    ]
    assert validate_claude_response(data) == False

def test_validate_claude_response_invalid_type():
    data = "not a list"
    assert validate_claude_response(data) == False

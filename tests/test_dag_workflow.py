import pytest
from unittest.mock import patch
from airflow.models import DagBag


@pytest.fixture(scope="module")
def dagbag():
    with patch("os.path.isfile", return_value=True), \
         patch("os.getenv", side_effect=lambda k, d=None: "dummy" if k in {"GOOGLE_APPLICATION_CREDENTIALS", "PROJECT_ID"} else d), \
         patch("api.analyze_and_insert.load_dotenv", return_value=True), \
         patch("api.analyze_and_insert.process_and_insert_all"):
        
        import dags.trustpilot_dag  # Force import pour charger le DAG
        return DagBag(dag_folder="/opt/airflow/dags", include_examples=False)


# verifier que le dag existe et peut être importé
def test_dag_import(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    assert dag is not None, "Le DAG 'trustpilot_pipeline' n'a pas été trouvé."


# verifier que le dag a les taches attendues
def test_task_ids(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    expected_tasks = {"scrape_trustpilot_reviews", "analyze_and_insert"}
    for task_id in expected_tasks:
        assert task_id in dag.task_ids, f"Le task_id '{task_id}' est manquant"

# tester l'ordre des taches
def test_dependencies(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    assert dag is not None

    # Exemple concret : scrape → clean → analyze
    assert dag.get_task("clean_reviews").upstream_task_ids == {"scrape_trustpilot_reviews"}
    assert dag.get_task("analyze_and_insert").upstream_task_ids == {"clean_reviews"}

# tester que le dag est acyclique
def test_dag_is_acyclic():
    from airflow.models.dagbag import DagBag

    dagbag = DagBag(dag_folder="/opt/airflow/dags", include_examples=False)
    dag = dagbag.get_dag("trustpilot_pipeline")

    # Cette méthode interne recharge tous les DAGs et détecte les cycles
    assert dagbag.import_errors == {}, f"Import errors: {dagbag.import_errors}"
    assert dag is not None, "DAG trustpilot_pipeline introuvable"


# tester que la tache 'analyze_and_insert' est bien un python operator
def test_operator_type(dagbag):
    dag = dagbag.get_dag("trustpilot_pipeline")
    task = dag.get_task("analyze_and_insert")
    from airflow.operators.python import PythonOperator
    assert isinstance(task, PythonOperator)


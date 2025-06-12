from airflow.models import DagBag

#lancer le daemon Airflow pour que le DAG soit chargé + lancer docker compose up -d à la racine du projet où se trouve le fichier docker-compose.yaml
#pour tester, executer pytest dans le container airflow-scheduler depuis le terminal: docker compose exec airflow-scheduler pytest /opt/airflow/tests/test_dag_workflow.py -v


# Vérifie que le DAG est bien chargé
def test_dag_loaded():
    dag_bag = DagBag()
    assert dag_bag.import_errors == {}, f"Erreur(s) lors du chargement des DAGs : {dag_bag.import_errors}"
    assert "trustpilot_analyze_pipeline" in dag_bag.dags, "Le DAG 'trustpilot_analyze_pipeline' est introuvable."

# Vérifie que les tâches attendues existent
def test_dag_has_expected_tasks():
    dag = DagBag().dags["trustpilot_analyze_pipeline"]
    expected_tasks = {"extract_raw_reviews", "analyze_and_insert"}
    dag_task_ids = set(dag.task_ids)
    assert expected_tasks.issubset(dag_task_ids), f"Tâches manquantes : {expected_tasks - dag_task_ids}"

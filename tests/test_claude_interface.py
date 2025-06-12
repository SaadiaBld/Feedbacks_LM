import pytest
from unittest.mock import patch
from api.claude_interface import classify_with_claude

@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_valid_response(mock_create):
    # Simulation d'une réponse JSON valide
    mock_create.return_value = type("Obj", (object,), {
        "content": '{"themes": [{"theme": "Livraison et retrait", "note": 1},{"theme": "Expérience d'achat en ligne", "note": 1}, {"theme": "Retour et remboursement", "note": 2}]}'
    })()

    verbatim = "Produit trop cher et livraison lente, c'est inacceptable. Je n'ai pas pu retourner le produit facilement."
    result = classify_with_claude(verbatim)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["theme"] == "Prix"
    assert result[0]["note"] == 1

@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_invalid_json(mock_create):
    # Simulation d'un JSON cassé
    mock_create.return_value = type("Obj", (object,), {
        "content": 'invalid json string'
    })()

    with pytest.raises(ValueError):
        classify_with_claude("Avis incompréhensible")

@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_empty_response(mock_create):
    # Simulation d'une réponse vide
    mock_create.return_value = type("Obj", (object,), {
        "content": ''
    })()

    with pytest.raises(ValueError):
        classify_with_claude("Très bon service")

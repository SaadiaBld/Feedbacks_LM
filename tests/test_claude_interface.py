import pytest
from unittest.mock import patch
from api.claude_interface import classify_with_claude

# Tester la classification avec Claude en utilisant des réponses simulées
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_valid_response(mock_create):
    # Simulation d'une réponse JSON valide avec bon format
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": ['
                    '{"theme": "Livraison et retrait", "note": 1}, '
                    '{"theme": "Retour et remboursement", "note": 2}]}'
        })()]
    })()

    verbatim = "Livraison lente et retour compliqué"
    result = classify_with_claude(verbatim)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["theme"] == "Livraison et retrait"
    assert result[0]["note"] == 1

@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_invalid_json(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": "not valid JSON"
        })()]
    })()

    with pytest.raises(ValueError):
        classify_with_claude("Texte cassé")

# tester la classification avec un thème vide
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_empty_response(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": ""
        })()]
    })()
    with pytest.raises(ValueError):
        classify_with_claude("Texte vide")

#theme detecté qui n'est pas dans la liste 
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_unknown_theme(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": ['
                    '{"theme": "Organisation magasin", "note": 3}, '
                    '{"theme": "Livraison et retrait", "note": 2}]}'
        })()]
    })()

    result = classify_with_claude("Livraison correcte, mais je prefere acheter en magasin")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["theme"] == "Livraison et retrait"

#note invalide 
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_invalid_note(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": ['
                    '{"theme": "Livraison et retrait", "note": 10}]}'
        })()]
    })()

    result = classify_with_claude("Livraison absurde")
    assert result is None

#tester le cas avec une note manquante
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_missing_note(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": [{"theme": "Livraison et retrait"}]}'
        })()]
    })()
    result = classify_with_claude("Livraison correcte")
    assert result is None

# tester le cas où les thèmes ne sont pas une liste (un dictionnaire par exemple)
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_themes_not_a_list(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": {"theme": "Livraison et retrait", "note": 2}}'
        })()]
    })()
    result = classify_with_claude("Mauvaise livraison")
    assert result is None

# tester le cas où les thèmes sont un item qui n'est pas un dictionnaire
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_item_not_dict(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": ["not_a_dict"]}'
        })()]
    })()
    result = classify_with_claude("Texte bidon")
    assert result is None

# tester le cas où la note est une chaîne de caractères et non un entier
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_note_as_string(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": [{"theme": "Livraison et retrait", "note": "3"}]}'
        })()]
    })()
    result = classify_with_claude("Livraison correcte")
    assert result is None


# tester le cas où la réponse de Claude est vide
@patch('api.claude_interface.client.messages.create')
def test_classify_with_claude_empty_verbatim(mock_create):
    mock_create.return_value = type("Obj", (object,), {
        "content": [type("SubObj", (object,), {
            "text": '{"themes": []}'
        })()]
    })()
    result = classify_with_claude("")
    assert result is None

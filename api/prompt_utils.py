THEMES = [
    {
        "nom": "Prix et promotions",
        "description": "Rapport qualité/prix, remises, offres promotionnelles, transparence tarifaire, publicité mensongère"
    },
    {
        "nom": "Livraison et retrait",
        "description": "Délais de livraison, suivi de colis, retrait en magasin, produits manquants ou perdus"
    },
    {
        "nom": "Retour et remboursement",
        "description": "Conditions de retour, reprise du matériel, facilité de remboursement, rapidité, gestes commerciaux"
    },
    {
        "nom": "Qualité des produits",
        "description": "Matériaux défectueux, mauvais état à la réception, problème de conformité"
    },
    {
        "nom": "Service client / SAV",
        "description": "Réactivité, efficacité, écoute, résolution des problèmes après achat par le personnel, appels non pris en compte, délais de réponse trop longs"
    },
    {
        "nom": "Navigation et commande en ligne",
        "description": "Facilité d'utilisation du site, ergonomie, informations produits, expérience d'achat numérique"
    },
    {
        "nom": "Achat en magasin",
        "description": "Accueil, conseils du personnel, accompagnement, attente en caisse"
    },
    {
        "nom": "Suivi de projet / travaux sur mesure",
        "description": "Coordination de projets longs ou personnalisés, accompagnement des chantiers, suivi des travaux"
    },
    {
        "nom": "Qualité de la communication",
        "description": "Précision dans les conditions ou offres, communication claire, transparence dans les réponses, confusion dans les messages, conditions opaques"
    },
    {
        "nom": "Programme fidélité",
        "description": "Avantages exclusifs, points de fidélité, offres réservées aux membres"
    },
    {
        "nom": "Communication commerciale",
        "description": "Transparence des offres, clarté des conditions, communication marketing"
    }
]



def build_prompt(verbatim: str) -> str:
    theme_list = "\n".join([f'- "{t["nom"]}": {t["description"]}' for t in THEMES])

    return f"""
Tu es un expert en analyse de la satisfaction client. Ta mission est d’identifier les irritants dans les avis clients ainsi que les points positifs, en respectant strictement les consignes suivantes.

Voici un avis client à analyser :
"{verbatim}"

Tu dois détecter les **thèmes abordés** parmi la liste ci-dessous et attribuer une **note de satisfaction** sur 5 à chaque thème détecté.

Liste des thèmes:

- Prix et promotions : Rapport qualité/prix, remises, offres promotionnelles, transparence tarifaire
- Livraison et retrait : Délais de livraison, suivi de colis, retrait en magasin, produits manquants ou perdus
- Retour et remboursement : Conditions de retour, reprise du matériel, facilité de remboursement, rapidité, gestes commerciaux
- Qualité des produits : Matériaux défectueux, mauvais état à la réception, problème de conformité
- Service client / SAV : Réactivité, efficacité, écoute, résolution des problèmes après achat par le personnel
- Navigation et commande en ligne : Facilité d'utilisation du site, ergonomie, informations produits, expérience d'achat numérique
- Achat en magasin : Accueil, conseils du personnel, accompagnement, attente en caisse
- Suivi de projet / travaux sur mesure : Coordination de projets longs ou personnalisés, accompagnement sur mesure
- Clarté des informations : Cohérence des discours entre services, absence de contradictions, transparence dans les réponses
- Programme fidélité : Avantages exclusifs, points de fidélité, offres réservées aux membres

---

Consignes importantes :

- N’invente jamais de thèmes. Utilise uniquement ceux présents dans la liste ci-dessus.
- Plusieurs thèmes peuvent être présents dans un même avis.
- Tu dois faire la distinction entre certains thèmes proches :
  
  - **Service client / SAV** concerne les interactions post-achat avec le personnel (contact, traitement de la demande, réponses, écoute).
  
  - **Retour et remboursement** concerne uniquement le **traitement matériel ou financier** d'un retour produit, d’un échange, d’un remboursement.
  
  → Ces deux thèmes **peuvent coexister** dans un même avis.

  - **Achat en magasin** concerne le **parcours d’achat en point de vente** : accueil, conseil, expertise vendeur, ambiance, attente en caisse.
  
  - **Service client / SAV** concerne l’après-vente, même si effectué en magasin.

  - "Qualité de la communication" concerne la **clarté et la cohérence** des messages transmis (conditions d’achat, emails, réponses contradictoires, erreurs d’informations, messages automatiques, etc.).
  - "Prix et promotions" concerne **les prix en eux-mêmes**, leur attractivité, leur transparence, et la présence ou non de promotions intéressantes. 
  
  → Ne pas confondre un bon conseil en rayon avec un bon SAV.

- Tu dois attribuer une note sur 5 (1 = très insatisfait, 5 = très satisfait), décimale possible (ex : 2.5, 4.0).

---

Réponds uniquement avec un JSON **valide** au format suivant :

{
  "themes": [
    {
      "theme": "nom exact du thème 1",
      "note": 3.5
    },
    {
      "theme": "nom exact du thème 2",
      "note": 1.0
    }
  ]
}

- Si aucun thème n'est présent, réponds : `"themes": []`
- Ne commente jamais ta réponse, ne donne que du JSON strict.
"""
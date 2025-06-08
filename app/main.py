import os
from fastapi import FastAPI, Header, HTTPException
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from app.scraper import scrape_reviews


load_dotenv()  
API_TOKEN = os.getenv("API_TOKEN")

security = HTTPBearer(auto_error=True)  # Authentification Bearer

# app/main.py
app = FastAPI(
    title="Trustpilot API",
    version="1.0",
    description="API sécurisée pour récupérer les avis Trustpilot de Leroy Merlin (moins de 7 jours)"
)

@app.get("/reviews", summary="Récupère les avis récents de Leroy Merlin", tags=["Reviews"])
def get_reviews(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # récupère juste la valeur après "Bearer"

    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalide")

    try:
        reviews = scrape_reviews(mode="json")
        return {"source": "leroymerlin.fr", "reviews": reviews}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur scraping : {str(e)}")
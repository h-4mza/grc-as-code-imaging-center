from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessValue(BaseModel):
    id: str = Field(..., description="Identifiant unique de la valeur métier")
    nom: str = Field(..., description="Nom de la valeur métier")
    processus: str = Field(..., description="Description du processus")
    evenement_redoute: str = Field(..., description="Événement redouté associé")
    gravite: int = Field(..., ge=1, le=5, description="Niveau de gravité (1 à 5)")

class BusinessValueList(BaseModel):
    business_values: List[BusinessValue]

class Asset(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'actif")
    nom: str = Field(..., description="Nom de l'actif")
    type: str = Field(..., description="Type de l'actif (e.g. Logiciel applicatif)")
    criticite: int = Field(..., ge=1, le=5, description="Criticité de l'actif (1 à 5)")
    valeurs_metier_liees: List[str] = Field(default_factory=list, description="Liste des IDs des valeurs métier liées")

class AssetList(BaseModel):
    assets: List[Asset]

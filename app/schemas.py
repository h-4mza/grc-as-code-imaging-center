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

class SourceRisque(BaseModel):
    id: str = Field(..., description="Identifiant unique de la SR")
    nom: str = Field(..., description="Nom de la source de risque")
    type: str = Field(..., description="Type (Malveillance externe, interne, etc.)")
    motivation: str = Field(..., description="Motivation principale")
    ressources: str = Field(..., description="Niveau de ressources")

class ObjectifVise(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'OV")
    nom: str = Field(..., description="Nom de l'objectif visé")
    description: str = Field(..., description="Description détaillée")

class CoupleSROV(BaseModel):
    id: str = Field(..., description="Identifiant unique du couple SR/OV")
    sr_id: str = Field(..., description="ID de la Source de Risque")
    ov_id: str = Field(..., description="ID de l'Objectif Visé")
    pertinence: int = Field(..., ge=1, le=5, description="Pertinence évaluée (1 à 5)")
    description: str = Field(..., description="Description du scénario stratégique de haut niveau")

class Atelier2(BaseModel):
    sources_risques: List[SourceRisque]
    objectifs_vises: List[ObjectifVise]
    couples_sr_ov: List[CoupleSROV]

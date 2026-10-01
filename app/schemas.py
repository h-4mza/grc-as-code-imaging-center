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

class PartiePrenante(BaseModel):
    id: str = Field(..., description="Identifiant unique de la partie prenante")
    nom: str = Field(..., description="Nom de la partie prenante")
    type: str = Field(..., description="Type (Partenaire, fournisseur, etc.)")
    niveau_menace: int = Field(..., ge=1, le=5, description="Niveau de menace perçu (1 à 5)")
    dependance: str = Field(..., description="Niveau et nature de la dépendance")

class ScenarioStrategique(BaseModel):
    id: str = Field(..., description="Identifiant du scénario stratégique")
    nom: str = Field(..., description="Nom du scénario")
    srov_id: str = Field(..., description="ID du couple SR/OV associé")
    partie_prenante_id: str = Field(..., description="ID de la partie prenante (vecteur)")
    vraisemblance: int = Field(..., ge=1, le=5, description="Vraisemblance (1 à 5)")
    description: str = Field(..., description="Description de l'attaque via l'écosystème")

class Atelier3(BaseModel):
    parties_prenantes: List[PartiePrenante]
    scenarios_strategiques: List[ScenarioStrategique]

class ScenarioOperationnel(BaseModel):
    id: str = Field(..., description="Identifiant du scénario opérationnel")
    nom: str = Field(..., description="Nom du scénario")
    sc_strat_id: str = Field(..., description="ID du scénario stratégique parent (ou N/A)")
    techniques_attack: List[str] = Field(..., description="Liste des techniques MITRE ATT&CK")
    vraisemblance: int = Field(..., ge=1, le=5, description="Vraisemblance évaluée (1 à 5)")
    gravite: int = Field(..., ge=1, le=5, description="Gravité évaluée (1 à 5)")
    description: str = Field(..., description="Description technique du mode opératoire")

class Atelier4(BaseModel):
    scenarios_operationnels: List[ScenarioOperationnel]

class Control(BaseModel):
    id: str = Field(..., description="ID du contrôle ISO 27001 (ex: 5.1)")
    nom: str = Field(..., description="Nom du contrôle")
    theme: str = Field(..., description="Thème (Organisationnel, Personnes, Physique, Technologique)")
    applicable: bool = Field(..., description="Applicabilité du contrôle")
    justification: str = Field(..., description="Justification d'applicabilité ou d'exclusion")
    etat: str = Field(..., description="État de mise en œuvre (En place, Partiel, Non initié, N/A)")
    maturite: int = Field(..., ge=0, le=5, description="Niveau de maturité (0 à 5)")
    preuve: str = Field(..., description="Élément de preuve ou commentaire")

class AnnexA(BaseModel):
    controls: List[Control]

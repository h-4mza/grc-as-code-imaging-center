from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base

# Association table for Asset <-> BusinessValue
asset_bv_table = Table(
    'asset_business_value',
    Base.metadata,
    Column('asset_id', String, ForeignKey('assets.id'), primary_key=True),
    Column('bv_id', String, ForeignKey('business_values.id'), primary_key=True)
)

class BusinessValue(Base):
    __tablename__ = "business_values"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    processus = Column(String)
    evenement_redoute = Column(String)
    gravite = Column(Integer)
    assets = relationship("Asset", secondary=asset_bv_table, back_populates="valeurs_metier")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    type = Column(String)
    criticite = Column(Integer)
    valeurs_metier = relationship("BusinessValue", secondary=asset_bv_table, back_populates="assets")

class SourceRisque(Base):
    __tablename__ = "sources_risques"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    type = Column(String)
    motivation = Column(String)
    ressources = Column(String)

class ObjectifVise(Base):
    __tablename__ = "objectifs_vises"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    description = Column(String)

class CoupleSROV(Base):
    __tablename__ = "couples_sr_ov"
    id = Column(String, primary_key=True)
    sr_id = Column(String, ForeignKey("sources_risques.id"))
    ov_id = Column(String, ForeignKey("objectifs_vises.id"))
    pertinence = Column(Integer)
    description = Column(String)
    sr = relationship("SourceRisque")
    ov = relationship("ObjectifVise")

class PartiePrenante(Base):
    __tablename__ = "parties_prenantes"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    type = Column(String)
    niveau_menace = Column(Integer)
    dependance = Column(String)

class ScenarioStrategique(Base):
    __tablename__ = "scenarios_strategiques"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    srov_id = Column(String, ForeignKey("couples_sr_ov.id"))
    partie_prenante_id = Column(String, ForeignKey("parties_prenantes.id"))
    vraisemblance = Column(Integer)
    description = Column(String)
    srov = relationship("CoupleSROV")
    partie_prenante = relationship("PartiePrenante")

class ScenarioOperationnel(Base):
    __tablename__ = "scenarios_operationnels"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    sc_strat_id = Column(String, nullable=True) # Pas de ForeignKey stricte pour les N/A
    techniques_attack = Column(String) # Stored as comma separated or JSON string
    vraisemblance = Column(Integer)
    gravite = Column(Integer)
    description = Column(String)

class Control(Base):
    __tablename__ = "controls"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    theme = Column(String)
    applicable = Column(Boolean)
    justification = Column(String)
    etat = Column(String)
    maturite = Column(Integer)
    preuve = Column(String)

# Association tables for Finding
finding_control_table = Table(
    'finding_control',
    Base.metadata,
    Column('finding_id', Integer, ForeignKey('findings.id'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id'), primary_key=True)
)

finding_risk_table = Table(
    'finding_risk',
    Base.metadata,
    Column('finding_id', Integer, ForeignKey('findings.id'), primary_key=True),
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True) # sc_op = risk
)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)
    severite = Column(String)
    actif_id = Column(String, ForeignKey("assets.id"))
    cve = Column(String, nullable=True)
    technique_attack = Column(String, nullable=True)
    date = Column(String)
    
    actif = relationship("Asset")
    controls = relationship("Control", secondary=finding_control_table)
    risks = relationship("ScenarioOperationnel", secondary=finding_risk_table)

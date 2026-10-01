from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base

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


risk_asset_table = Table(
    'risk_asset',
    Base.metadata,
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True),
    Column('asset_id', String, ForeignKey('assets.id'), primary_key=True)
)

risk_control_table = Table(
    'risk_control',
    Base.metadata,
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id'), primary_key=True)
)

class ScenarioOperationnel(Base):
    __tablename__ = "scenarios_operationnels"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    sc_strat_id = Column(String, nullable=True)
    techniques_attack = Column(String)
    vraisemblance = Column(Integer)
    gravite = Column(Integer)
    description = Column(String)
    nist_csf = Column(String, nullable=True)
    assets = relationship("Asset", secondary=risk_asset_table)
    controls_list = relationship("Control", secondary=risk_control_table)

class Control(Base):
    __tablename__ = "controls"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    theme = Column(String)
    is_applicable = Column(Boolean)
    justification = Column(String)
    status = Column(String)
    maturity = Column(Integer)
    evidence = Column(String)
    
    mappings = relationship("ControlMapping", back_populates="control")

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
    Column('risk_id', String, ForeignKey('scenarios_operationnels.id'), primary_key=True)
)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)
    severite = Column(String)
    actif_id = Column(String, ForeignKey("assets.id"))
    cve = Column(String, nullable=True)
    technique_attack = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date = Column(String)
    
    actif = relationship("Asset")
    controls = relationship("Control", secondary=finding_control_table)
    risks = relationship("ScenarioOperationnel", secondary=finding_risk_table)

class ControlMapping(Base):
    __tablename__ = "control_mappings"
    id = Column(String, primary_key=True)
    control_id = Column(String, ForeignKey("controls.id"))
    framework = Column(String)
    reference = Column(String)
    
    control = relationship("Control", back_populates="mappings")

class Treatment(Base):
    __tablename__ = "treatments"
    id = Column(String, primary_key=True)
    nom = Column(String, nullable=False)
    risk_id = Column(String, ForeignKey("scenarios_operationnels.id"))
    option = Column(String)
    echeance = Column(String)
    responsable = Column(String)
    jira_key = Column(String, nullable=True)
    status = Column(String, default="todo")
    
    risk = relationship("ScenarioOperationnel")

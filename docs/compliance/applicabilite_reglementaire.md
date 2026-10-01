# Note d'Applicabilité Réglementaire : Centre d'Imagerie Médicale

**Référence Document** : CIM-SEC-REG-001  
**Version** : 1.0  
**Statut** : Approuvé (Direction Générale / DSI)  
**Date** : Juin 2026  

---

## 1. Contexte de l'organisation
Le Centre d'Imagerie Médicale (CIM) est une structure de santé spécialisée dans le radiodiagnostic (IRM, Scanner, Mammographie, Échographie). Le CIM produit, manipule, stocke et transmet des données médicales hautement sensibles. En outre, le centre assure une continuité de soins via un service de téléradiologie 24/7 en partenariat avec des cliniques locales et les urgences.

En raison de la nature de ses données (données de santé à caractère personnel - DSCP) et de son rôle critique dans la chaîne de soins régionale, le CIM est soumis à un cadre réglementaire strict. 

La présente note argumente l'applicabilité des trois principaux référentiels de conformité : **NIS2**, **RGPD**, et **HDS**.

---

## 2. Applicabilité de la Directive NIS2 (UE 2022/2555)

### 2.1. Critère sectoriel
La directive NIS2 (Network and Information Security) élargit considérablement le périmètre des entités régulées. Le secteur de la **Santé** est classé comme un **Secteur Hautement Critique** (Annexe I).
Le CIM, en tant que prestataire de soins de santé (au sens de la directive 2011/24/UE), rentre de plein droit dans ce champ sectoriel.

### 2.2. Critère de taille et d'importance
Bien que le CIM puisse être classé comme une moyenne entreprise (selon les effectifs), il est qualifié d'**Entité Essentielle (EE)** ou d'**Entité Importante (EI)** selon la transposition nationale en cours, car :
- Une perturbation de ses services de téléradiologie aurait un impact immédiat sur les urgences hospitalières (danger pour la santé publique).
- Le centre dépend fortement des réseaux et systèmes d'information (PACS, RIS) pour la production de soins.

### 2.3. Conséquences et Exigences (Article 21)
En conséquence, le CIM s'engage formellement à mettre en œuvre les mesures de gestion des risques de cybersécurité exigées par l'Article 21 :
- **Analyse des risques** : Réalisée via la méthode EBIOS RM.
- **Gestion des incidents** : Mise en place d'un processus de notification sous 24h/72h à l'ANSSI.
- **Sécurité de la chaîne d'approvisionnement** : Audit de l'éditeur du PACS (Scénario stratégique R-03).
- **Hygiène informatique & Cryptographie** : Chiffrement des flux DICOM (VPN IPSec) et déploiement du MFA pour la téléradiologie.

---

## 3. Applicabilité du RGPD (Règlement Général sur la Protection des Données)

### 3.1. Traitement de Catégories Particulières de Données (Article 9)
Le cœur de métier du CIM repose sur la production et l'interprétation d'images médicales (radiographies, IRM). Ces images, associées au nom du patient et à son dossier clinique (DPI), constituent des **Données Concernant la Santé** (Article 9 du RGPD).
Leur traitement est interdit par défaut, sauf exception (Art. 9.2.h : diagnostic médical, prise en charge sanitaire).

### 3.2. Rôle du Centre d'Imagerie
Le CIM agit en tant que **Responsable de Traitement** pour les données générées en son sein.

### 3.3. Exigences applicables
- **DPIA (Analyse d'Impact sur la Protection des Données - Art. 35)** : Obligatoire pour le traitement à grande échelle de données de santé (PACS/RIS). Le volet cybersécurité du DPIA est couvert par notre analyse EBIOS RM.
- **Sécurité des traitements (Art. 32)** : Obligation de garantir la confidentialité et l'intégrité des données. Couvert par l'implémentation de la norme **ISO 27001**.
- **Registre des traitements (Art. 30)** : Maintenu par le DPO (Délégué à la Protection des Données).
- **Notification des violations de données (Art. 33)** : À la CNIL dans un délai de 72h. Ce risque est traité dans le scénario opérationnel R-02 (Exfiltration via faille VPN).

---

## 4. Applicabilité du Référentiel HDS (Hébergement de Données de Santé)

### 4.1. Le Principe d'Externalisation
L'article L. 1111-8 du Code de la santé publique (CSP) impose que tout hébergement de données de santé à caractère personnel sur support numérique, réalisé par un prestataire pour le compte d'un professionnel de santé, soit confié à un prestataire certifié **HDS**.

### 4.2. Architecture du CIM et périmètre HDS
Le CIM héberge une partie de ses données sur site (Modalités, PACS local tampon), mais **externalise ses sauvegardes et son archivage long terme (VNA)** vers le cloud pour des raisons de résilience.
Par conséquent :
- Le fournisseur Cloud (AWS/Azure/OVH) ou l'infogéreur **DOIT être certifié HDS** (niveaux 1 à 6 selon la prestation).
- Le CIM doit inclure dans ses contrats des clauses spécifiques HDS.

### 4.3. Conséquences pour le CIM
Bien que le CIM ne soit pas lui-même hébergeur, il doit exiger et contrôler la conformité de son fournisseur. Ce point est directement audité par le contrôle ISO 27001 **5.23 (Sécurité de l'information pour l'utilisation de services cloud)**, dont la maturité a été évaluée à 4/5 grâce à la contractualisation stricte HDS et à l'immutabilité des sauvegardes (WORM).

---

## 5. Synthèse de Couverture (Mapping GRC)

Afin de démontrer cette conformité, l'approche **GRC As-Code** du centre mappe chaque exigence de ces réglementations aux contrôles ISO 27001 mis en œuvre :

| Référentiel | Moteur d'Applicabilité | Contrôles ISO 27001 Clés Mappés (Exemples) |
|-------------|------------------------|------------------------------------------|
| **NIS2**    | Protection SI Essentiel| 5.24 (Incidents), 5.21 (Supply chain), 8.7 (Malware) |
| **RGPD**    | Données de Santé (DPI) | 5.34 (Confidentialité), 8.12 (DLP), 8.24 (Cryptographie) |
| **HDS**     | Archivage Cloud PACS   | 5.23 (Cloud), 8.13 (Sauvegardes) |

*(Voir les tableaux de bord Streamlit de l'application pour le taux de couverture en temps réel).*

# Note d'Applicabilité Réglementaire : Centre d'Imagerie Médicale (CIM)

**Référence Document** : CIM-SEC-REG-001
**Version** : 1.1 (Mise à jour GRC-as-Code)
**Statut** : Approuvé (Direction Générale / DPO / RSSI)
**Date** : Juin 2026

---

## 1. Contexte de l'organisation et Périmètre d'Application
Le Centre d'Imagerie Médicale (CIM) est une structure de santé spécialisée dans le radiodiagnostic (IRM, Scanner, Mammographie, Échographie). Le CIM produit, manipule, stocke et transmet des données médicales hautement sensibles. Il assure une continuité de soins via un service de téléradiologie 24/7 en partenariat avec des cliniques locales et les urgences.

**Enjeu de conformité croisée (UE / Maroc) :** 
Bien que le centre soit situé géographiquement au Maroc, ses partenariats de téléradiologie avec des cliniques européennes et le traitement de données de ressortissants de l'UE rendent le cadre réglementaire européen (RGPD, NIS2) **extraterritorialement applicable**. Ces exigences s'additionnent au cadre local (Loi 09-08 relative à la protection des données à caractère personnel et Loi 05-20 relative à la cybersécurité).

---

## 2. Applicabilité de la Directive NIS2 (UE 2022/2555)

### 2.1. Critère sectoriel et qualification
La directive NIS2 élargit le périmètre des entités régulées par rapport à NIS1. Le secteur de la **Santé** est classé comme un **Secteur Hautement Critique** (Annexe I). En tant que prestataire de soins et nœud d'interconnexion pour la téléradiologie, le CIM rentre de plein droit dans ce champ sectoriel.

Il est qualifié d'**Entité Essentielle (EE)** ou d'**Entité Importante (EI)** car une perturbation de ses services de téléradiologie aurait un impact immédiat sur les urgences (danger pour la santé publique). Le centre dépend fortement des réseaux et systèmes d'information (PACS, RIS) pour la production de soins.

### 2.2. Réponse aux Exigences (Article 21)
Le CIM a transposé les exigences de gestion des risques de cybersécurité (Article 21) dans son modèle GRC-as-Code :
* **Analyse des risques** : Réalisée via la méthode EBIOS RM (5 ateliers, 10 scénarios).
* **Gestion des incidents (Art. 21.2.b)** : Mise en place d'un processus de notification précoce sous 24h et d'un rapport sous 72h aux autorités de contrôle (ANSSI/DGSSI).
* **Sécurité de la chaîne d'approvisionnement (Art. 21.2.d)** : Audit de l'éditeur du PACS et des mainteneurs biomédicaux (Scénarios stratégiques R-03 et R-04).
* **Cryptographie et MFA (Art. 21.2.j)** : Chiffrement des flux DICOM via VPN IPSec et déploiement du MFA pour la téléradiologie.

---

## 3. Applicabilité du RGPD (UE 2016/679)

### 3.1. Traitement de Catégories Particulières de Données (Article 9)
Le cœur de métier du CIM repose sur la production et l'interprétation d'images médicales. Ces images, associées au dossier clinique du patient (DPI), constituent des **Données Concernant la Santé** (Article 9 du RGPD). Leur traitement est licite sous l'exception de la prise en charge sanitaire (Art. 9.2.h). Le CIM agit en tant que **Responsable de Traitement** pour ces données.

### 3.2. Exigences opérationnelles appliquées
* **Registre des traitements (Art. 30)** : Maintenu par le DPO, il inclut les processus de "Prise en charge patient" et "Téléradiologie" identifiés dans les valeurs métier EBIOS RM.
* **DPIA (Analyse d'Impact - Art. 35)** : Obligatoire pour le traitement à grande échelle de données de santé (PACS/RIS). Le volet cyber du DPIA s'appuie nativement sur l'analyse EBIOS RM.
* **Sécurité des traitements (Art. 32)** : Obligation de garantir la confidentialité et l'intégrité des données, couverte par l'évaluation continue des 93 contrôles ISO 27001.
* **Notification des violations (Art. 33)** : Délai strict de 72h auprès de l'autorité de contrôle (CNIL/CNDP). Ce risque est directement modélisé dans les scénarios R-02 (Exfiltration VPN) et R-05 (Insider threat).

---

## 4. Applicabilité du Référentiel HDS (Hébergement de Données de Santé)

### 4.1. Principe d'Externalisation
L'article L. 1111-8 du Code de la santé publique (CSP) français impose que tout hébergement de données de santé sur support numérique soit confié à un prestataire certifié **HDS**.

### 4.2. Architecture du CIM et périmètre HDS
Le CIM héberge une partie de ses données sur site (Modalités, PACS local tampon), mais **externalise ses sauvegardes et son archivage long terme (VNA)** vers le cloud pour des raisons de résilience.
Le fournisseur Cloud ou l'infogéreur **DOIT être certifié HDS** (niveaux 1 à 6 selon la prestation). Le CIM doit inclure dans ses contrats des clauses spécifiques HDS.

### 4.3. Conséquences pour le CIM
Bien que le CIM ne soit pas lui-même hébergeur, il doit exiger et contrôler la conformité de son fournisseur. Ce point est audité informatiquement par notre registre de risques via le contrôle ISO 27001 **5.23 (Sécurité de l'information pour l'utilisation de services cloud)**. La maturité est évaluée à 4/5 grâce à la contractualisation stricte HDS et à l'immutabilité des sauvegardes (WORM).

---

## 5. Matrice de Conformité Dynamique (GRC-as-Code)

Afin de démontrer cette conformité en temps réel, l'API FastAPI du CIM mappe dynamiquement chaque exigence réglementaire aux contrôles ISO 27001 correspondants :

| Référentiel | Moteur d'Applicabilité | Contrôles ISO 27001 Clés Mappés (Exemples) |
|-------------|------------------------|------------------------------------------|
| **NIS2** | Protection SI Essentiel | 5.24 (Incidents), 5.21 (Supply chain), 8.7 (Malware) |
| **RGPD** | Données de Santé (DPI) | 5.34 (Confidentialité), 8.12 (DLP), 8.24 (Cryptographie) |
| **HDS** | Archivage Cloud PACS | 5.23 (Cloud), 8.13 (Sauvegardes) |

*(Le calcul exact de couverture et l'état d'implémentation de ces mesures sont disponibles sur les tableaux de bord Streamlit de la plateforme).*

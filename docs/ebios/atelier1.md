# Atelier 1 : Cadrage et Socle de Sécurité (Périmètre & Valeurs Métier)

L'Atelier 1 de la méthode EBIOS RM définit le périmètre de l'étude, recense les missions et processus de l'organisation, et identifie les valeurs métier ainsi que les actifs supports indispensables à leur fonctionnement.

## 1. Description du Centre d'Imagerie Médicale (CIM)

Le centre d'imagerie médicale étudié est un établissement de radiodiagnostic doté d'un plateau technique moderne :
- **2 Scanners TDM**
- **1 IRM 3 Tesla**
- **3 Tables de radiologie numérique directe (DR)**
- **1 Salle d'échographie**
- **1 Équipement de mammographie numérique**

L'équipe médicale et technique compte 4 médecins radiologues, 8 manipulateurs d'électroradiologie, 3 secrétaires médicales et 1 technicien informatique.
Le centre traite environ 150 examens par jour, générant un volume quotidien d'environ 80 Go de données d'imagerie au standard DICOM. Il assure également une astreinte de téléradiologie 24/7 en liaison avec les services d'urgences de cliniques partenaires.

## 2. Échelle de Cotation EBIOS RM (1 à 4)

Conformément au guide EBIOS RM de l'ANSSI, l'évaluation des impacts et de la criticité repose sur une échelle standardisée à 4 niveaux :

| Niveau | Qualification | Définition opérationnelle pour le CIM |
|:---:|---|---|
| **1** | **Mineure** | Conséquences minimes, contournables immédiatement sans impact sur les patients ni sur la continuité de service. |
| **2** | **Significative** | Perturbation temporaire d'un processus support, surcoût modéré, sans danger pour la santé des patients. |
| **3** | **Grave** | Retard diagnostique significatif, interruption prolongée de téléradiologie, préjudice financier ou atteinte réglementaire notable. |
| **4** | **Critique** | Arrêt immédiat de la production de soins, urgence vitale compromise, destruction irrémédiable de données médicales ou fuite massive de données de santé (RGPD art. 9). |

## 3. Cartographie des Valeurs Métier & Événements Redoutés

Les valeurs métier correspondent aux processus fondamentaux du centre dont l'atteinte porterait préjudice à son activité ou à ses obligations réglementaires :

| ID | Valeur Métier | Processus associé | Critères (DIC) | Événement Redouté | Gravité (1-4) |
|---|---|---|:---:|---|:---:|
| **bv_prise_en_charge** | Prise en charge patient | Accueil administratif, vérification prescriptions, enregistrement DPI/RIS, consentement | D | Impossibilité d'accueillir et d'enregistrer les patients, entraînant des retards de prise en charge. | **3** (Grave) |
| **bv_acquisition** | Acquisition des images | Réalisation de l'examen par le manipulateur, acquisition et transfert DICOM vers le PACS | D, I | Arrêt des équipements d'imagerie ou impossibilité de transférer les images, arrêt de la production de soins. | **4** (Critique) |
| **bv_interpretation** | Interprétation et compte rendu | Visualisation PACS, rédaction CR dans le RIS, signature électronique, envoi MSSanté | D, I | Indisponibilité des images ou du RIS retardant le diagnostic, ou erreur de compte rendu affectant la santé du patient. | **4** (Critique) |
| **bv_teleradiologie** | Téléradiologie | Transfert chiffré VPN, interprétation à distance, retour CR signé | D, C | Interception ou indisponibilité du flux de téléradiologie compromettant les gardes et urgences. | **3** (Grave) |
| **bv_archivage** | Archivage légal | Stockage long terme, réplication sur site distant | D, I | Perte définitive des historiques médicaux. | **3** (Grave) |
| **bv_facturation** | Administration et facturation | Gestion des rendez-vous, facturation des actes, télétransmission des feuilles de soins | D | Blocage de la facturation ou rejet des télétransmissions entraînant des pertes financières. | **2** (Significative) |
| **bv_confidentialite** | Confidentialité des données de santé | Protection des dossiers médicaux, images DICOM et données identifiantes contre la divulgation non autorisée | C | Divulgation de dossiers patients, violation RGPD art. 9, notification CNIL/CNDP. | **4** (Critique) |

*(Données source : `grc/si/business_values.yaml`)*

## 4. Cartographie des Actifs Supports

Les actifs supports sont les composantes du système d'information (applications, matériels, réseaux, données, personnels) sur lesquelles reposent les valeurs métier :

| ID | Nom de l'Actif | Type | Criticité (1-4) | Valeurs Métier Supportées |
|---|---|---|:---:|---|
| **ast_pacs** | PACS (Picture Archiving and Communication System) | Application | **4** (Critique) | `bv_acquisition`, `bv_interpretation`, `bv_teleradiologie`, `bv_archivage`, `bv_confidentialite` |
| **ast_dpi** | DPI (Dossier Patient Informatisé) | Application | **4** (Critique) | `bv_prise_en_charge`, `bv_interpretation`, `bv_confidentialite` |
| **ast_modalites** | Modalités d'imagerie (Scanner IRM / CT / Mammographe) | Équipement | **4** (Critique) | `bv_acquisition` |
| **ast_ris** | RIS (Radiological Information System) | Application | **4** (Critique) | `bv_prise_en_charge`, `bv_interpretation`, `bv_teleradiologie`, `bv_facturation`, `bv_confidentialite` |
| **ast_telemaintenance** | Accès de télémaintenance biomédicale | Réseau | **3** (Grave) | `bv_acquisition` |
| **ast_vpn** | Connexion Internet / VPN téléradiologie | Réseau | **3** (Grave) | `bv_teleradiologie`, `bv_archivage` |
| **ast_donnees_identite** | Données administratives et identité patient | Données | **3** (Grave) | `bv_prise_en_charge`, `bv_facturation`, `bv_confidentialite` |
| **ast_personnel** | Personnel du centre (Administratif, Manipulateurs, Médecins) | Humain | **3** (Grave) | `bv_prise_en_charge`, `bv_acquisition`, `bv_interpretation` |
| **ast_postes_travail** | Postes de travail (Secrétariat, Médecins) | Équipement | **2** (Significative) | `bv_prise_en_charge`, `bv_interpretation`, `bv_facturation` |

*(Données source : `grc/si/assets.yaml`)*

## 5. Synthèse des Enjeux du Socle de Sécurité

Les objectifs prioritaires dégagés par l'Atelier 1 sont les suivants :
- **Disponibilité (D)** : Garantir la continuité de service des modalités d'imagerie et du flux de téléradiologie 24/7.
- **Intégrité (I)** : Assurer la stricte fidélité des images DICOM et des comptes rendus médicaux pour prévenir les erreurs de diagnostic.
- **Confidentialité (C)** : Préserver le secret médical et répondre aux obligations du RGPD (données de santé au sens de l'article 9) et de la certification HDS.
- **Maîtrise des tiers** : Encadrer rigoureusement les accès distants via l'actif `ast_telemaintenance` et les flux partenaires `ast_vpn`.

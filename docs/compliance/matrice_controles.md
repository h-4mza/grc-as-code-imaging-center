# Matrice de Conformité et Couverture des Contrôles

Ce document présente la cartographie croisée des mesures de sécurité du **Centre d'Imagerie Médicale (CIM)**. Il consolide l'alignement entre les contrôles de l'**ISO/IEC 27001:2022 (Annexe A)**, les exigences de la directive européenne **NIS 2 (Article 21(2))**, le référentiel **NIST Cybersecurity Framework (CSF 2.0)** et les techniques d'attaque **MITRE ATT&CK Enterprise v14** identifiées dans l'analyse de risques EBIOS RM.

---

## 1. Matrice des Contrôles ISO 27001:2022 et Mappings Multi-Référentiels

Le tableau suivant détaille chaque contrôle ISO 27001:2022 de la Déclaration d'Applicabilité (SoA), son statut opérationnel, son niveau de maturité (0-5), ainsi que ses correspondances NIS2, NIST CSF 2.0 et ATT&CK.

| Contrôle ISO | Statut | Maturité | NIS2 (Art. 21(2)) | NIST CSF 2.0 | Techniques ATT&CK |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **5.1** - Politiques de sécurité de l'information | Implémenté | 4/5 | Art. 21(2)a | GV.PO-01 : Cybersecurity policies are established, communicated, and enforced | - |
| **5.2** - Rôles et responsabilités | Implémenté | 3/5 | - | - | - |
| **5.3** - Séparation des tâches | Implémenté | 3/5 | - | - | - |
| **5.4** - Responsabilités de la direction | Implémenté | 3/5 | Art. 21(2)a | - | - |
| **5.5** - Contacts avec les autorités | Implémenté | 4/5 | - | - | - |
| **5.6** - Contacts avec des groupes d'intérêts | Partiel | 1/5 | - | - | - |
| **5.7** - Renseignements sur les menaces | Implémenté | 3/5 | - | - | - |
| **5.8** - Sécurité dans la gestion de projet | Implémenté | 3/5 | - | - | - |
| **5.9** - Inventaire des actifs | Partiel | 2/5 | Art. 21(2)i | ID.AM-01 : Physical devices and systems inventory is maintained | - |
| **5.10** - Utilisation acceptable des actifs | Partiel | 1/5 | - | - | - |
| **5.11** - Restitution des actifs | Partiel | 2/5 | - | - | - |
| **5.12** - Classification des informations | Partiel | 1/5 | - | - | - |
| **5.13** - Marquage des informations | Partiel | 1/5 | - | - | - |
| **5.14** - Transfert d'information | Implémenté | 4/5 | Art. 21(2)h | PR.DS-02 : Data-in-transit is protected | - |
| **5.15** - Contrôle d'accès | Partiel | 1/5 | Art. 21(2)i | PR.AA-05 : Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed (incorporating least privilege and separation of duties) | T1005, T1078, T1213, T1485, T1531, T1565 |
| **5.16** - Gestion des identités | Partiel | 1/5 | - | - | - |
| **5.17** - Informations d'authentification | Implémenté | 3/5 | Art. 21(2)j | PR.AA-01 : Identities and credentials for authorized users, services, and hardware are managed | T1110 |
| **5.18** - Droits d'accès | Implémenté | 3/5 | - | - | - |
| **5.19** - Sécurité fournisseurs | Partiel | 2/5 | Art. 21(2)d | GV.SC-05 : Requirements to address cybersecurity risks in supply chains are established, prioritized, and integrated into contracts and other types of agreements with suppliers and other relevant third parties | T1195 |
| **5.20** - Sécurité dans les contrats fournisseurs | Implémenté | 3/5 | Art. 21(2)d | - | - |
| **5.21** - Sécurité chaîne d'approvisionnement TIC | Partiel | 2/5 | Art. 21(2)d | GV.SC-09 : Supply chain security practices are integrated into cybersecurity and enterprise risk management programs, and their performance is monitored throughout the technology product and service life cycle | T1195 |
| **5.22** - Surveillance des fournisseurs | Partiel | 1/5 | Art. 21(2)d | - | - |
| **5.23** - Sécurité des services cloud | Implémenté | 4/5 | Art. 21(2)d | GV.SC-07 : The risks posed by a supplier, their products and services, and other third parties are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship | - |
| **5.24** - Préparation gestion incidents | Partiel | 2/5 | Art. 21(2)b | - | - |
| **5.25** - Évaluation des événements | Implémenté | 3/5 | Art. 21(2)b | - | - |
| **5.26** - Réponse aux incidents | Implémenté | 3/5 | Art. 21(2)b | RS.MA-01 : The incident response plan is executed in coordination with relevant third parties once an incident is declared | - |
| **5.27** - Apprentissage des incidents | Implémenté | 3/5 | Art. 21(2)b | - | - |
| **5.28** - Collecte de preuves | Implémenté | 3/5 | Art. 21(2)b | - | - |
| **5.29** - Sécurité lors de perturbations | Implémenté | 3/5 | Art. 21(2)c | - | - |
| **5.30** - Préparation TIC pour continuité | Partiel | 2/5 | Art. 21(2)c | RC.RP-01 : The recovery portion of the incident response plan is executed once initiated from the incident response process | - |
| **5.31** - Exigences légales | Implémenté | 3/5 | - | - | - |
| **5.32** - Propriété intellectuelle | Partiel | 2/5 | - | - | - |
| **5.33** - Protection des enregistrements | Partiel | 2/5 | - | - | - |
| **5.34** - Données personnelles | Implémenté | 4/5 | - | - | - |
| **5.35** - Révision indépendante | Partiel | 2/5 | Art. 21(2)f | - | - |
| **5.36** - Conformité aux politiques | Implémenté | 3/5 | Art. 21(2)f | - | - |
| **5.37** - Procédures d'exploitation | Partiel | 1/5 | Art. 21(2)a | PR.PS-01 : Configuration management practices are established and applied | - |
| **6.1** - Sélection du personnel | Implémenté | 3/5 | Art. 21(2)i | PR.AA-01 : Identities and credentials for authorized users, services, and hardware are managed | - |
| **6.2** - Conditions d'emploi | Implémenté | 3/5 | Art. 21(2)i | - | - |
| **6.3** - Sensibilisation | Partiel | 2/5 | Art. 21(2)g | PR.AT-01 : Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind | T1566 |
| **6.4** - Processus disciplinaire | Partiel | 1/5 | - | - | - |
| **6.5** - Fin d'emploi | Partiel | 1/5 | Art. 21(2)i | - | - |
| **6.6** - Accords de confidentialité | Implémenté | 4/5 | - | - | - |
| **6.7** - Travail à distance | Implémenté | 4/5 | - | - | - |
| **6.8** - Signalement | Implémenté | 3/5 | - | - | - |
| **7.1** - Périmètres de sécurité | Implémenté | 3/5 | - | - | - |
| **7.2** - Entrée physique | Implémenté | 3/5 | - | - | - |
| **7.3** - Sécurisation bureaux/salles | Implémenté | 4/5 | - | - | - |
| **7.4** - Surveillance physique | Partiel | 1/5 | - | - | - |
| **7.5** - Protection contre menaces externes | Implémenté | 3/5 | - | - | - |
| **7.6** - Travail dans zones sécurisées | Implémenté | 3/5 | - | - | - |
| **7.7** - Bureaux et écrans dégagés | Implémenté | 3/5 | Art. 21(2)g | - | - |
| **7.8** - Emplacement des équipements | Implémenté | 3/5 | - | - | - |
| **7.9** - Sécurité des actifs hors site | Implémenté | 3/5 | - | - | - |
| **7.10** - Supports de stockage | Partiel | 2/5 | - | PR.DS-01 : Data-at-rest is protected | T1052 |
| **7.11** - Services généraux | Implémenté | 3/5 | - | - | - |
| **7.12** - Sécurité câblage | Partiel | 1/5 | - | - | - |
| **7.13** - Maintenance des équipements | Implémenté | 4/5 | - | - | - |
| **7.14** - Élimination sécurisée | Partiel | 2/5 | - | - | - |
| **8.1** - Appareils terminaux | Partiel | 2/5 | - | - | - |
| **8.2** - Privilèges d'accès | Partiel | 2/5 | - | - | - |
| **8.3** - Restriction d'accès | Partiel | 1/5 | - | - | - |
| **8.4** - Code source | Non applicable | N/A | - | - | - |
| **8.5** - Authentification sécurisée | Non implémenté | 1/5 | Art. 21(2)j | PR.AA-02 : Users, services, and hardware are authenticated | T1021, T1078, T1110 |
| **8.6** - Gestion de capacité | Partiel | 1/5 | - | PR.IR-04 : Adequate resource capacity to ensure availability is maintained | T1499 |
| **8.7** - Protection malwares | Partiel | 2/5 | Art. 21(2)g | PR.PS-05 : Installation and execution of unauthorized software are prevented | T1059, T1486, T1566 |
| **8.8** - Vulnérabilités techniques | Partiel | 2/5 | Art. 21(2)e, Art. 21(2)f | ID.RA-01 : Vulnerabilities in assets are identified, validated, and recorded | T1190 |
| **8.9** - Configurations | Implémenté | 3/5 | Art. 21(2)a, Art. 21(2)g | PR.PS-01 : Configuration management practices are established and applied | T1547, T1566 |
| **8.10** - Suppression de l'information | Implémenté | 3/5 | - | - | - |
| **8.11** - Masquage des données | Implémenté | 3/5 | - | - | - |
| **8.12** - Prévention des fuites (DLP) | Non implémenté | 0/5 | - | PR.DS-11 : Unauthorized data disclosures are prevented | T1005, T1052, T1213, T1567 |
| **8.13** - Sauvegarde | Implémenté | 3/5 | Art. 21(2)c | PR.DS-10 : Data is backed up, protected, and tested | T1485, T1486, T1531, T1565 |
| **8.14** - Redondance | Implémenté | 3/5 | Art. 21(2)c | PR.IR-03 : Mechanisms are implemented to achieve resilience requirements in normal and adverse situations | T1498 |
| **8.15** - Journalisation | Implémenté | 3/5 | - | - | - |
| **8.16** - Surveillance | Partiel | 1/5 | - | DE.CM-01 : Networks and network services are monitored to find potentially adverse events | T1005, T1021, T1040, T1052, T1059, T1078, T1110, T1190, T1195, T1213, T1485, T1486, T1498, T1499, T1531, T1547, T1557, T1565, T1566, T1567 |
| **8.17** - Synchronisation horloges | Partiel | 1/5 | - | - | - |
| **8.18** - Utilisation de programmes | Partiel | 1/5 | - | - | - |
| **8.19** - Installation logiciels | Partiel | 1/5 | Art. 21(2)e | PR.PS-05 : Installation and execution of unauthorized software are prevented | T1059, T1547 |
| **8.20** - Sécurité réseaux | Partiel | 2/5 | Art. 21(2)j | PR.IR-01 : Networks and environments are protected from unauthorized logical access and usage | T1021, T1190, T1498, T1499, T1567 |
| **8.21** - Services réseau | Implémenté | 3/5 | - | - | - |
| **8.22** - Ségrégation réseaux | Implémenté | 3/5 | Art. 21(2)j | PR.IR-01 : Networks and environments are protected from unauthorized logical access and usage | T1040, T1557 |
| **8.23** - Filtrage Web | Partiel | 1/5 | - | - | - |
| **8.24** - Cryptographie | Partiel | 2/5 | Art. 21(2)h | PR.DS-01 : Data-at-rest is protected | T1040, T1557 |
| **8.25** - Cycle de vie développement | Non applicable | N/A | Art. 21(2)e | - | - |
| **8.26** - Exigences sécurité | Non applicable | N/A | - | - | - |
| **8.27** - Architecture sécurité | Non applicable | N/A | - | - | - |
| **8.28** - Sécurité du codage | Non applicable | N/A | Art. 21(2)e | - | - |
| **8.29** - Tests de sécurité | Non applicable | N/A | - | - | - |
| **8.30** - Développement externalisé | Non applicable | N/A | - | - | - |
| **8.31** - Séparation environnements | Non applicable | N/A | - | - | - |
| **8.32** - Gestion des changements | Implémenté | 3/5 | - | - | - |
| **8.33** - Informations de test | Non applicable | N/A | - | - | - |
| **8.34** - Protection systèmes d'audit | Partiel | 2/5 | - | - | - |

---

## 2. Matrice Inversée : Directive NIS 2 -> Contrôles ISO 27001:2022

Cette vue synthétise la conformité aux **10 mesures obligatoires de gestion des risques** prescrites par l'Article 21 paragraphe 2 de la directive NIS 2 (UE 2022/2555). Chaque mesure est couverte par un ensemble de contrôles ISO 27001 applicables.

| Mesure NIS 2 | Intitulé de l'obligation | Contrôles ISO 27001 associés | Ventilation Statut | Couverture |
| :--- | :--- | :--- | :--- | :---: |
| **Article 21(2)a** | Politiques relatives à l'analyse des risques et à la sécurité des SI | `5.1` (Politiques de sécurité de l'information)<br>`5.4` (Responsabilités de la direction)<br>`5.37` (Procédures d'exploitation)<br>`8.9` (Configurations) | 3 implémenté(s), 1 partiel(s) | ✅ Conforme |
| **Article 21(2)b** | Gestion des incidents (détection, notification, réponse) | `5.24` (Préparation gestion incidents)<br>`5.25` (Évaluation des événements)<br>`5.26` (Réponse aux incidents)<br>`5.27` (Apprentissage des incidents)<br>`5.28` (Collecte de preuves) | 4 implémenté(s), 1 partiel(s) | ✅ Conforme |
| **Article 21(2)c** | Continuité des activités (sauvegardes, PCA/PRA, gestion de crise) | `5.29` (Sécurité lors de perturbations)<br>`5.30` (Préparation TIC pour continuité)<br>`8.13` (Sauvegarde)<br>`8.14` (Redondance) | 3 implémenté(s), 1 partiel(s) | ✅ Conforme |
| **Article 21(2)d** | Sécurité de la chaîne d'approvisionnement et relations tiers | `5.19` (Sécurité fournisseurs)<br>`5.20` (Sécurité dans les contrats fournisseurs)<br>`5.21` (Sécurité chaîne d'approvisionnement TIC)<br>`5.22` (Surveillance des fournisseurs)<br>`5.23` (Sécurité des services cloud) | 2 implémenté(s), 3 partiel(s) | ✅ Conforme |
| **Article 21(2)e** | Sécurité de l'acquisition, dev, maintenance et vulnérabilités | `8.8` (Vulnérabilités techniques)<br>`8.19` (Installation logiciels)<br>`8.25` (Cycle de vie développement)<br>`8.28` (Sécurité du codage) | 2 partiel(s), 2 non applicable(s) | ✅ Conforme |
| **Article 21(2)f** | Évaluation de l'efficacité des mesures de sécurité (audits, tests) | `5.35` (Révision indépendante)<br>`5.36` (Conformité aux politiques)<br>`8.8` (Vulnérabilités techniques) | 1 implémenté(s), 2 partiel(s) | ✅ Conforme |
| **Article 21(2)g** | Pratiques de base en hygiène informatique et formation | `6.3` (Sensibilisation)<br>`7.7` (Bureaux et écrans dégagés)<br>`8.7` (Protection malwares)<br>`8.9` (Configurations) | 2 implémenté(s), 2 partiel(s) | ✅ Conforme |
| **Article 21(2)h** | Politiques d'utilisation de la cryptographie et du chiffrement | `5.14` (Transfert d'information)<br>`8.24` (Cryptographie) | 1 implémenté(s), 1 partiel(s) | ✅ Conforme |
| **Article 21(2)i** | Sécurité des ressources humaines, contrôle d'accès et actifs | `5.9` (Inventaire des actifs)<br>`5.15` (Contrôle d'accès)<br>`6.1` (Sélection du personnel)<br>`6.2` (Conditions d'emploi)<br>`6.5` (Fin d'emploi) | 2 implémenté(s), 3 partiel(s) | ✅ Conforme |
| **Article 21(2)j** | Authentification multifacteur (MFA) et communications sécurisées | `5.17` (Informations d'authentification)<br>`8.5` (Authentification sécurisée)<br>`8.20` (Sécurité réseaux)<br>`8.22` (Ségrégation réseaux) | 2 implémenté(s), 1 partiel(s), 1 non implémenté(s) | ✅ Conforme |

---

## 3. Matrice Inversée : MITRE ATT&CK -> Contrôles ISO 27001:2022

Cette vue associe chaque **technique d'attaque MITRE ATT&CK** rencontrée dans les scénarios opérationnels EBIOS RM (Atelier 4) aux mesures préventives et détectives de l'ISO 27001:2022. Elle met en évidence les mitigations officielles et garantit une défense en profondeur équilibrée.

| Technique ATT&CK | Nom | Mitigations ATT&CK | Contrôles ISO 27001 Associés | Statuts | Défense |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **T1005** | Data from Local System | M1057, M1022 | `8.12` (Prévention des fuites (DLP)) *(Préventif)*<br>`5.15` (Contrôle d'accès) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1021** | Remote Services | M1032, M1035, M1047 | `8.5` (Authentification sécurisée) *(Préventif)*<br>`8.20` (Sécurité réseaux) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1040** | Network Sniffing | M1041, M1030 | `8.24` (Cryptographie) *(Préventif)*<br>`8.22` (Ségrégation réseaux) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1052** | Exfiltration Over Physical Medium | M1042, M1034, M1057 | `7.10` (Supports de stockage) *(Préventif)*<br>`8.12` (Prévention des fuites (DLP)) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1059** | Command and Scripting Interpreter | M1038, M1049, M1047 | `8.19` (Installation logiciels) *(Préventif)*<br>`8.7` (Protection malwares) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 3 partiel(s) | 🛡️ Prévention & Détection |
| **T1078** | Valid Accounts | M1032, M1026 | `8.5` (Authentification sécurisée) *(Préventif)*<br>`5.15` (Contrôle d'accès) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1110** | Brute Force | M1032, M1036 | `8.5` (Authentification sécurisée) *(Préventif)*<br>`5.17` (Informations d'authentification) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 1 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1190** | Exploit Public-Facing Application | M1051, M1037 | `8.8` (Vulnérabilités techniques) *(Préventif)*<br>`8.20` (Sécurité réseaux) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 3 partiel(s) | 🛡️ Prévention & Détection |
| **T1195** | Supply Chain Compromise | M1013 | `5.19` (Sécurité fournisseurs) *(Détection)*<br>`5.21` (Sécurité chaîne d'approvisionnement TIC) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 3 partiel(s) | 🛡️ Prévention & Détection |
| **T1213** | Data from Information Repositories | M1018, M1047 | `5.15` (Contrôle d'accès) *(Préventif)*<br>`8.12` (Prévention des fuites (DLP)) *(Détection)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |
| **T1485** | Data Destruction | M1053, M1018, M1032 | `8.13` (Sauvegarde) *(Préventif)*<br>`5.15` (Contrôle d'accès) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1486** | Data Encrypted for Impact | M1040, M1053 | `8.7` (Protection malwares) *(Détection)*<br>`8.13` (Sauvegarde) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1498** | Network Denial of Service | M1037 | `8.20` (Sécurité réseaux) *(Préventif)*<br>`8.14` (Redondance) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1499** | Endpoint Denial of Service | M1037 | `8.20` (Sécurité réseaux) *(Préventif)*<br>`8.6` (Gestion de capacité) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 3 partiel(s) | 🛡️ Prévention & Détection |
| **T1531** | Account Access Removal | Audit / Monitoring | `5.15` (Contrôle d'accès) *(Préventif)*<br>`8.13` (Sauvegarde) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1547** | Boot or Logon Autostart Execution | M1028, M1038 | `8.9` (Configurations) *(Préventif)*<br>`8.19` (Installation logiciels) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1557** | Adversary-in-the-Middle | M1041, M1030, M1031 | `8.24` (Cryptographie) *(Préventif)*<br>`8.22` (Ségrégation réseaux) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1565** | Data Manipulation | M1022, M1029 | `5.15` (Contrôle d'accès) *(Préventif)*<br>`8.13` (Sauvegarde) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 2 partiel(s) | 🛡️ Prévention & Détection |
| **T1566** | Phishing | M1017, M1054, M1049, M1047 | `6.3` (Sensibilisation) *(Préventif)*<br>`8.9` (Configurations) *(Préventif)*<br>`8.7` (Protection malwares) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 1 implémenté(s), 3 partiel(s) | 🛡️ Prévention & Détection |
| **T1567** | Exfiltration Over Web Service | M1057, M1021 | `8.12` (Prévention des fuites (DLP)) *(Préventif)*<br>`8.20` (Sécurité réseaux) *(Préventif)*<br>`8.16` (Surveillance) *(Détection)* | 2 partiel(s), 1 non implémenté(s) | 🛡️ Prévention & Détection |

# Atelier 4 : Scénarios Opérationnels (MITRE ATT&CK)

L'Atelier 4 détaille les modes opératoires techniques que les attaquants pourraient utiliser pour accomplir les scénarios vus précédemment. Chaque scénario opérationnel est lié à des techniques standardisées du référentiel **MITRE ATT&CK**.

## Cartographie des 10 scénarios opérationnels

| ID | Nom de l'attaque | Techniques ATT&CK principales | Vraisemblance (1-5) | Gravité (1-5) |
|---|---|---|---|---|
| **SC_OP_1** | Phishing et déploiement de Ransomware | T1566 (Phishing), T1486 (Data Encrypted) | 4 | 5 |
| **SC_OP_2** | Exfiltration de données via faille VPN | T1190 (Exploit Public-Facing App), T1567 (Exfiltration) | 4 | 5 |
| **SC_OP_3** | Compromission de la chaîne logistique PACS | T1195 (Supply Chain), T1021 (Remote Services) | 3 | 5 |
| **SC_OP_4** | Attaque d'un équipement IRM via télémaintenance | T1078 (Valid Accounts), T1499 (Endpoint DoS) | 3 | 5 |
| **SC_OP_5** | Vol de données internes (Insider Threat) | T1213 (Data from Info Repository), T1052 (USB) | 3 | 4 |
| **SC_OP_6** | Attaque DDoS sur la ligne Internet | T1498 (Network Denial of Service) | 4 | 4 |
| **SC_OP_7** | Rebond via une clinique partenaire | T1190 (Exploit), T1565 (Data Manipulation) | 3 | 4 |
| **SC_OP_8** | Destruction des sauvegardes HDS | T1531 (Account Access Removal), T1485 (Destruction) | 2 | 5 |
| **SC_OP_9** | Interception de trafic DICOM non chiffré | T1557 (AiTM), T1040 (Network Sniffing) | 3 | 4 |
| **SC_OP_10**| Compromission Admin par Brute Force (RDP) | T1110 (Brute Force), T1078 (Valid Accounts) | 4 | 5 |

## Analyse et Hiérarchisation

L'évaluation de la vraisemblance (Probabilité) et de la gravité (Impact) permet d'obtenir un score de risque.
Les scénarios **SC_OP_1**, **SC_OP_2**, et **SC_OP_10** obtiennent la note maximale de **20/25**, ce qui les place en criticité absolue. Ces scénarios impliquent systématiquement :
1. Une exposition externe (Email, VPN, RDP).
2. Un impact sur les données vitales (PACS, DPI).

*(Données source : `grc/ebios/w4_operationnels.yaml`)*

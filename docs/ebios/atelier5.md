# Atelier 5 : Traitement du Risque (Plan d'Action GRC)

L'Atelier 5 de la méthode **EBIOS RM** formalise la stratégie de traitement de l'ensemble des risques opérationnels identifiés lors de l'Atelier 4. Pour chaque scénario (R-01 à R-12), une décision stratégique d'arbitrage est arrêtée parmi les quatre options normatives :
- **Réduction (`reduce`)** : Déploiement de mesures techniques ou organisationnelles (contrôles ISO 27001) diminuant la vraisemblance et/ou l'impact.
- **Transfert (`transfer`)** : Partage financier ou opérationnel du risque (assurance cyber, garanties contractuelles).
- **Acceptation (`accept`)** : Décision formelle de maintien du risque résiduel sous conditions strictes de gouvernance (niveau résiduel $\le$ Moyen, motivation argumentée et validation par la direction).
- **Évitement (`avoid`)** : Abandon ou reconception d'une activité ou d'un flux jugé intolérable.

---

## 1. Tableau Général des Traitements de Risque

Le référentiel compte **13 traitements opérationnels** couvrant l'intégralité des 12 scénarios opérationnels (R-01 à R-12) :

| ID | Nom du Traitement | Risque Visé | Option | Contrôles ISO 27001 | Échéance | Revue | Responsable | Statut | Résiduel Cible |
|---|---|---|:---:|---|:---:|:---:|:---:|:---:|:---:|
| **tr_pacs_ransomware_defense** | Segmentation réseau, EDR managé, sauvegardes hors ligne testées et sensibilisation | **R-01** | `reduce` | 8.7, 8.13, 5.14, 8.22 | 2026-12-15 | 2027-06-30 | IT | `in_progress` | **Moyen** |
| **tr_vpn_hardening_mfa** | Mise à jour d'urgence firmware VPN, MFA obligatoire et segmentation réseau | **R-02** | `reduce` | 8.20, 8.22, 8.8, 8.5 | 2026-11-30 | 2027-06-30 | Réseau | `in_progress` | **Moyen** |
| **tr_audit_clauses_fournisseur** | Audit sécurité fournisseur PACS et renforcement des clauses contractuelles | **R-03** | `reduce` | 5.19, 5.21, 8.19 | 2027-02-28 | 2027-06-30 | DSSI | `todo` | **Moyen** |
| **tr_cyber_assurance** | Souscription d'une assurance cyber dédiée couvrant la chaîne logistique logicielle | **R-03** | `transfer` | 5.19 | 2027-01-15 | 2027-06-30 | Direction | `todo` | **Faible** |
| **tr_bastion_telemaintenance** | Déploiement d'un bastion télémaintenance IRM avec MFA et validation à la demande | **R-04** | `reduce` | 8.20, 5.15, 8.5 | 2027-04-30 | 2027-06-30 | Biomédical | `todo` | **Moyen** |
| **tr_dlp_usb_blocking** | Blocage physique/logiciel des ports USB et surveillance DLP sur dossiers DPI | **R-05** | `reduce` | 8.12, 7.10, 6.1 | 2027-01-31 | 2027-06-30 | IT | `in_progress` | **Faible** |
| **tr_anti_ddos_accept** | Acceptation du risque DDoS avec protection de base de l'opérateur FAI | **R-06** | `accept` | 8.16, 8.20 | 2026-10-31 | 2027-06-30 | Réseau | `done` | **Moyen** |
| **tr_ipsec_filter_signature** | Filtrage applicatif strict flux HL7/DICOM et signature électronique des comptes rendus | **R-07** | `reduce` | 8.22, 5.14, 8.24 | 2027-03-15 | 2027-06-30 | Réseau | `todo` | **Moyen** |
| **tr_backup_immutability_worm** | Activation de l'immutabilité des sauvegardes (WORM / Object Lock) sur le cloud HDS | **R-08** | `reduce` | 8.13, 8.14, 5.23 | 2027-02-15 | 2027-06-30 | IT | `todo` | **Faible** |
| **tr_dicom_tls_encryption** | Chiffrement TLS des flux DICOM en transit sur le LAN et durcissement réseau | **R-09** | `reduce` | 8.24, 8.20 | 2027-05-31 | 2027-06-30 | Biomédical | `todo` | **Faible** |
| **tr_rdp_closure_mfa** | Fermeture de l'exposition Internet des ports RDP et MFA pour les administrateurs | **R-10** | `reduce` | 5.17, 8.5, 5.15 | 2026-11-15 | 2027-06-30 | DSSI | `in_progress` | **Moyen** |
| **tr_raid6_backup_321** | Migration baie stockage en RAID 6 avec redondance matérielle et sauvegarde 3-2-1 | **R-11** | `reduce` | 8.14, 8.6, 8.13 | 2027-06-30 | 2027-06-30 | IT | `todo` | **Faible** |
| **tr_procedures_versioning_formation** | Procédures d'exploitation documentées, versionnage configurations et formation | **R-12** | `reduce` | 8.9, 8.13, 5.37 | 2027-03-31 | 2027-06-30 | IT | `todo` | **Faible** |

> [!NOTE]
> **Décision d'acceptation formalisée pour R-06 (`tr_anti_ddos_accept`) :**
> - **Justification** : Le coût financier d'une infrastructure anti-DDoS dédiée haute capacité sur site excède l'impact d'une coupure temporaire de la téléradiologie externe. Le plateau technique d'imagerie reste pleinement opérationnel en local et l'opérateur FAI assure un nettoyage volumétrique amont.
> - **Autorité d'acceptation** : Validé formellement par le **Comité de Direction / DSSI**.
> - **Niveau résiduel conforme** : **Moyen** ($\le$ Moyen requis par la gouvernance).

*(Données source : `grc/ebios/w5_traitements.yaml`)*

---

## 2. Plan d'Action par Horizon Temporel

Les 13 traitements sont échelonnés sur trois horizons temporels selon l'urgence opérationnelle et la complexité technique :

### 🚀 Court terme : Clôture Q4 2026 ($\le 3$ mois)
*Focalisation sur l'extinction des vecteurs d'exposition externe immédiate et la défense périmétrique.*

1. **`tr_anti_ddos_accept`** (R-06, Réseau, 2026-10-31) : **Terminé (`done`)** – Activation du service de filtrage FAI et arbitrage d'acceptation formalisé.
2. **`tr_rdp_closure_mfa`** (R-10, DSSI, 2026-11-15) : **En cours (`in_progress`)** – Révocation des accès RDP directs sur Internet, migration vers bastion d'administration MFA.
3. **`tr_vpn_hardening_mfa`** (R-02, Réseau, 2026-11-30) : **En cours (`in_progress`)** – Application des correctifs de firmware et généralisation du MFA pour les téléradiologues.
4. **`tr_pacs_ransomware_defense`** (R-01, IT, 2026-12-15) : **En cours (`in_progress`)** – Déploiement de l'EDR managé, segmentation PACS/RIS et tests de restauration hors ligne.

### ⚙️ Moyen terme : Horizon Q1 2027 (3 à 6 mois)
*Renforcement de la gouvernance fournisseur, protection des données et intégrité applicative.*

5. **`tr_cyber_assurance`** (R-03, Direction, 2027-01-15) : **Planifié (`todo`)** – Souscription du contrat d'assurance cyber-risques couvrant la supply chain.
6. **`tr_dlp_usb_blocking`** (R-05, IT, 2027-01-31) : **En cours (`in_progress`)** – Verrouillage matériel des ports USB et règles DLP sur les exports DPI.
7. **`tr_backup_immutability_worm`** (R-08, IT, 2027-02-15) : **Planifié (`todo`)** – Verrouillage WORM / Object Lock des sauvegardes externalisées HDS.
8. **`tr_audit_clauses_fournisseur`** (R-03, DSSI, 2027-02-28) : **Planifié (`todo`)** – Revue d'audit tiers et avenants contractuels avec l'éditeur PACS.
9. **`tr_ipsec_filter_signature`** (R-07, Réseau, 2027-03-15) : **Planifié (`todo`)** – Signature électronique des comptes rendus et filtrage des trames HL7 inter-cliniques.
10. **`tr_procedures_versioning_formation`** (R-12, IT, 2027-03-31) : **Planifié (`todo`)** – Formalisation des SOPs, contrôle de version Git des configs et sensibilisation technique.

### 🛡️ Long terme : Horizon Q2 2027 ($> 6$ mois)
*Projets d'infrastructure lourde, refonte d'architecture et chiffrement en profondeur.*

11. **`tr_bastion_telemaintenance`** (R-04, Biomédical, 2027-04-30) : **Planifié (`todo`)** – Mise en place de la passerelle bastion sécurisée pour les mainteneurs IRM.
12. **`tr_dicom_tls_encryption`** (R-09, Biomédical, 2027-05-31) : **Planifié (`todo`)** – Activation systématique du protocole DICOM-TLS sur l'ensemble du parc d'imagerie.
13. **`tr_raid6_backup_321`** (R-11, IT, 2027-06-30) : **Planifié (`todo`)** – Remplacement et migration vers une baie SAN en RAID 6 double contrôleur avec sauvegarde 3-2-1.

---

## 3. Matrice de Réduction du Risque : Risque Inhérent $\rightarrow$ Résiduel Cible

Le tableau suivant mesure l'abaissement d'exposition projeté entre l'évaluation inhérente initiale ($G \times V$) et le niveau résiduel cible (`expected_residual`) :

| ID Risque | Nom du Scénario | Niveau Inhérent ($G \times V$) | Traitement(s) Associé(s) | Option(s) | Résiduel Cible | Évolution de Criticité |
|:---:|---|:---:|---|:---:|:---:|:---:|
| **R-01** | Phishing & Ransomware PACS/RIS | **Critique** (16) | `tr_pacs_ransomware_defense` | `reduce` | **Moyen** | 🔴 $\rightarrow$ 🟡 *(Gain de 2 niveaux)* |
| **R-02** | Exfiltration via VPN téléradiologie | **Critique** (12) | `tr_vpn_hardening_mfa` | `reduce` | **Moyen** | 🔴 $\rightarrow$ 🟡 *(Gain de 2 niveaux)* |
| **R-03** | Supply chain PACS | **Élevé** (8) | `tr_audit_clauses_fournisseur`<br/>`tr_cyber_assurance` | `reduce`<br/>`transfer` | **Moyen** / **Faible** | 🟠 $\rightarrow$ 🟢 *(Gain de 2 niveaux)* |
| **R-04** | Télémaintenance IRM | **Élevé** (9) | `tr_bastion_telemaintenance` | `reduce` | **Moyen** | 🟠 $\rightarrow$ 🟡 *(Gain de 1 niveau)* |
| **R-05** | Vol de données internes (USB) | **Élevé** (8) | `tr_dlp_usb_blocking` | `reduce` | **Faible** | 🟠 $\rightarrow$ 🟢 *(Gain de 2 niveaux)* |
| **R-06** | DDoS ligne Internet | **Moyen** (6) | `tr_anti_ddos_accept` | `accept` | **Moyen** | 🟡 $\rightarrow$ 🟡 *(Maintien accepté $\le$ Moyen)* |
| **R-07** | Rebond via clinique partenaire | **Élevé** (8) | `tr_ipsec_filter_signature` | `reduce` | **Moyen** | 🟠 $\rightarrow$ 🟡 *(Gain de 1 niveau)* |
| **R-08** | Destruction sauvegardes HDS | **Élevé** (8) | `tr_backup_immutability_worm` | `reduce` | **Faible** | 🟠 $\rightarrow$ 🟢 *(Gain de 2 niveaux)* |
| **R-09** | Interception DICOM sur LAN | **Moyen** (6) | `tr_dicom_tls_encryption` | `reduce` | **Faible** | 🟡 $\rightarrow$ 🟢 *(Gain de 1 niveau)* |
| **R-10** | Brute force RDP et compte admin | **Critique** (12) | `tr_rdp_closure_mfa` | `reduce` | **Moyen** | 🔴 $\rightarrow$ 🟡 *(Gain de 2 niveaux)* |
| **R-11** | Panne matérielle NAS/SAN | **Élevé** (9) | `tr_raid6_backup_321` | `reduce` | **Faible** | 🟠 $\rightarrow$ 🟢 *(Gain de 2 niveaux)* |
| **R-12** | Erreur humaine d'exploitation | **Moyen** (6) | `tr_procedures_versioning_formation` | `reduce` | **Faible** | 🟡 $\rightarrow$ 🟢 *(Gain de 1 niveau)* |

### Synthèse de la Maîtrise des Risques :
- **Éradication des risques Critiques résiduels** : Aucun risque ne demeure à l'état Critique après déploiement du plan d'action ($0\%$ de risque Critique résiduel).
- **Abaissement généralisé** : $100\%$ des scénarios inhérents Critiques (R-01, R-02, R-10) sont ramenés au niveau **Moyen**.
- **Prédominance des niveaux résiduels Faibles et Moyens** : $50\%$ des scénarios atteignent la cible **Faible** et $50\%$ la cible **Moyen**, garantissant l'homologation de sécurité et la conformité NIS 2 / HDS du centre d'imagerie.

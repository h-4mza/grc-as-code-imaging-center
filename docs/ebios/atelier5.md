# Atelier 5 : Traitement du Risque (Plan d'Action GRC)

L'Atelier 5 de la méthode EBIOS RM formalise la stratégie globale de traitement des risques identifiés lors des ateliers précédents. Pour chaque scénario de risque opérationnel, une stratégie est arrêtée (réduction, transfert, acceptation ou évitement), assortie d'un plan d'action précis, d'un responsable désigné et d'un calendrier de mise en œuvre.

## Tableau des Traitements de Risque

| ID | Nom du traitement | Risque visé | Option | Échéance | Responsable | Statut |
|---|---|---|---|---|---|---|
| **tr_mfa** | Déploiement MFA pour accès critiques | R-10 | reduce | 2026-12-31 | DSSI | todo |
| **tr_segmentation** | Segmentation réseau et sauvegardes hors ligne testées | R-01 | reduce | 2026-11-30 | IT | in_progress |
| **tr_patch_vpn** | Mise à jour d'urgence firmware VPN | R-02 | reduce | 2026-10-15 | Réseau | todo |
| **tr_dicom_tls** | Chiffrement TLS flux DICOM | R-09 | reduce | 2027-01-31 | Biomédical | todo |
| **tr_assurance_cyber** | Souscription assurance cyber et audit fournisseur | R-03 | transfer | 2026-12-15 | Direction | todo |
| **tr_bastion** | Mise en place d'un bastion pour la télémaintenance IRM | R-04 | reduce | 2027-02-28 | Biomédical | todo |
| **tr_dlp_usb** | Désactivation des ports USB et monitoring DLP | R-05 | reduce | 2026-11-15 | IT | in_progress |
| **tr_anti_ddos** | Acceptation du risque avec solution Anti-DDoS FAI de base | R-06 | accept | 2026-10-30 | Réseau | done |
| **tr_ipsec_filter** | Filtrage strict des flux IPSec inter-cliniques | R-07 | reduce | 2026-12-01 | Réseau | todo |
| **tr_backup_immutability** | Activation de l'immutabilité des sauvegardes (WORM) sur le cloud | R-08 | reduce | 2027-01-15 | IT | todo |

## Analyse et Synthèse du Plan de Traitement

Le plan de traitement regroupe 10 mesures couvrant l'ensemble des scénarios de risque :

1. **Orientation stratégique majeure (Réduction du risque) :**
   - **80% (8/10)** des mesures relèvent de la **réduction** (`reduce`), ciblant en priorité le durcissement technique (MFA, bastion, segmentation, filtrage IPSec, chiffrement TLS, sauvegardes WORM et DLP).
   - Les scénarios prioritaires (R-01 Ransomware, R-02 Exposition VPN, R-10 Accès distants/MFA) concentrent les efforts de sécurisation immédiate avec des échéances à court terme (Q4 2026).

2. **Mesures complémentaires (Transfert et Acceptation) :**
   - **1 mesure de transfert** (`transfer`) : la souscription d'une cyber-assurance et les clauses contractuelles fournisseurs (`tr_assurance_cyber`) pour couvrir l'écosystème PACS / tiers.
   - **1 mesure d'acceptation** (`accept`) : l'arbitrage rendu pour le risque DDoS (`tr_anti_ddos`), estimé résiduel au regard des protections de base fournies par l'opérateur réseau (statut `done`).

3. **Gouvernance et état d'avancement :**
   - La gouvernance implique l'ensemble des parties prenantes clés : **DSSI, IT, Réseau, Biomédical et Direction**.
   - À date, **1 traitement est finalisé** (`done`), **2 sont en cours de déploiement** (`in_progress`), et **7 sont planifiés** (`todo`) pour un aboutissement complet au premier trimestre 2027.

*(Données source : `grc/ebios/w5_traitements.yaml`)*

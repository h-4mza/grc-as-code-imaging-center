# Atelier 4 : Scénarios Opérationnels (MITRE ATT&CK & NIST CSF 2.0)

L'Atelier 4 de la méthode **EBIOS RM** formalise les modes opératoires techniques précis par lesquels les scénarios stratégiques se matérialisent sur le système d'information. Chaque scénario opérationnel est rattaché à un scénario stratégique parent, caractérise les actifs menacés, détaille la séquence ordonnée des techniques **MITRE ATT&CK** employées (ou la cause d'origine pour les défaillances), s'adosse aux contrôles **ISO 27001:2022** et s'aligne sur les sous-catégories officielles du cadre **NIST CSF 2.0**.

---

## 1. Méthode de Cotation du Risque Inhérent (Matrice $4 \times 4$)

Conformément à l'échelle unifiée EBIOS RM ($1$ à $4$), chaque scénario est qualifié en **Gravité ($G$)** et en **Vraisemblance ($V$)** avec une justification explicite (*rationale*). Le score de risque inhérent est calculé selon la logique de `app/services/scoring.py` :

$$\text{Score Inhérent} = G \times V \quad (G \in [1, 4], \; V \in [1, 4])$$

Les seuils de criticité sont définis comme suit :
- **Faible** : Score de $1$ à $3$
- **Moyen** : Score de $4$ à $6$
- **Élevé** : Score de $7$ à $9$
- **Critique** : Score de $10$ à $16$

---

## 2. Cartographie des 12 Scénarios Opérationnels

Le tableau ci-dessous récapitule l'évaluation des 12 scénarios opérationnels (R-01 à R-12) :

| ID | Nom du Scénario | Scénario Stratégique Parent | Techniques ATT&CK (séquence) | Contrôles ISO 27001 | NIST CSF 2.0 | $G$ | $V$ | Score ($G \times V$) | Niveau Inhérent |
|---|---|---|---|---|---|:---:|:---:|:---:|:---:|
| **R-01** | Phishing et déploiement de Ransomware sur PACS/RIS | `sc_strat_6` (Attaque directe) | T1566 $\rightarrow$ T1078 $\rightarrow$ T1021 $\rightarrow$ T1486 | 8.7, 8.13, 5.14 | PR.AT-01, PR.DS-11, RC.RP-03 | 4 | 4 | **16** | **Critique** |
| **R-02** | Exfiltration de données via faille VPN téléradiologie | `sc_strat_2` (VPN téléradiologie) | T1190 $\rightarrow$ T1005 $\rightarrow$ T1567 | 8.20, 8.22, 8.8 | ID.RA-01, PR.PS-01, PR.DS-10 | 4 | 3 | **12** | **Critique** |
| **R-03** | Compromission de la chaîne logistique (Supply chain PACS) | `sc_strat_1` (Éditeur PACS) | T1195 $\rightarrow$ T1059 $\rightarrow$ T1486 | 5.19, 5.21, 8.19 | GV.SC-04, GV.SC-06, PR.PS-06 | 4 | 2 | **8** | **Élevé** |
| **R-04** | Attaque d'un équipement IRM via télémaintenance biomédicale | `sc_strat_3` (Mainteneur biomédical) | T1078 $\rightarrow$ T1190 $\rightarrow$ T1499 | 8.20, 5.15, 8.5 | PR.AA-01, PR.AA-05, PR.IR-01 | 3 | 3 | **9** | **Élevé** |
| **R-05** | Vol de données internes par un employé (USB) | `sc_strat_7` (Abus interne) | T1078 $\rightarrow$ T1213 $\rightarrow$ T1052 | 8.12, 6.1, 7.10 | PR.AA-02, PR.DS-10, DE.CM-03 | 4 | 2 | **8** | **Élevé** |
| **R-06** | Attaque DDoS sur la ligne Internet | `sc_strat_8` (DDoS Internet) | T1498 $\rightarrow$ T1499 | 8.16, 8.20 | PR.IR-01, DE.AE-04 | 2 | 3 | **6** | **Moyen** |
| **R-07** | Rebond et altération de comptes rendus via clinique partenaire | `sc_strat_4` (Clinique partenaire) | T1190 $\rightarrow$ T1021 $\rightarrow$ T1565 | 8.22, 5.14, 8.24 | PR.AA-05, PR.DS-01, DE.CM-01 | 4 | 2 | **8** | **Élevé** |
| **R-08** | Destruction des sauvegardes hébergées chez l'hébergeur HDS | `sc_strat_5` (Hébergeur HDS) | T1078 $\rightarrow$ T1531 $\rightarrow$ T1485 | 8.13, 8.14, 5.23 | PR.DS-11, PR.AA-03, RC.RP-01 | 4 | 2 | **8** | **Élevé** |
| **R-09** | Interception de trafic DICOM en clair sur le LAN | `sc_strat_7` (Abus interne) | T1040 $\rightarrow$ T1557 $\rightarrow$ T1005 | 8.24, 8.20 | PR.DS-02, PR.PS-05 | 3 | 2 | **6** | **Moyen** |
| **R-10** | Brute force RDP et compromission de compte Administrateur | `sc_strat_6` (Attaque directe) | T1110 $\rightarrow$ T1078 $\rightarrow$ T1547 | 5.17, 8.5, 5.15 | PR.AA-01, PR.AA-03, DE.AE-02 | 4 | 3 | **12** | **Critique** |
| **R-11** | Panne matérielle majeure du stockage NAS/SAN | `sc_strat_9` (Défaillance technique) | *(Défaillance matérielle / N/A)* | 8.14, 8.6 | PR.IR-02, RC.RP-02 | 3 | 3 | **9** | **Élevé** |
| **R-12** | Erreur humaine d'exploitation (suppression / mauvaise config) | `sc_strat_9` (Défaillance technique) | *(Erreur humaine / N/A)* | 8.9, 8.13, 5.37 | PR.PS-02, PR.AT-02, ID.IM-01 | 2 | 3 | **6** | **Moyen** |

*(Données source : `grc/ebios/w4_operationnels.yaml`)*

---

## 3. Justification des Cotations (Rationales)

Chaque cotation de sévérité ($G$) et de vraisemblance ($V$) repose sur l'analyse contextuelle du plateau technique d'imagerie :

- **R-01 (4/4)** : Paralysie complète du centre en cas de chiffrement combiné du PACS et du RIS ; le phishing reste le vecteur d'attaque le plus fréquent et probant en milieu hospitalier.
- **R-02 (4/3)** : Fuite massive de données de santé (violation majeure RGPD/HDS) ; forte exposition des passerelles VPN et des postes nomades des téléradiologues.
- **R-03 (4/2)** : Impact maximal par compromission du socle applicatif ; complexité opératoire importante pour corrompre la chaîne de build d'un éditeur de santé.
- **R-04 (3/3)** : Arrêt direct d'un équipement IRM lourd sans atteinte aux bases de données ; les accès de télémaintenance recourent encore à des pratiques de sécurité inégales.
- **R-05 (4/2)** : Divulgation ciblée d'informations médicales hautement confidentielles ; l'intention malveillante interne reste un événement rare mais redouté.
- **R-06 (2/3)** : Rupture des flux distants (téléradiologie nocturne) sans impact sur la production locale ; facilité d'orchestration d'attaques DDoS volumétriques.
- **R-07 (4/2)** : Corruption potentielle de diagnostics mettant en jeu la prise en charge clinique ; nécessite une double compromission (partenaire puis rebond).
- **R-08 (4/2)** : Perte de la capacité de reprise après sinistre ; accès aux consoles cloud sous contrôle strict de l'hébergeur certifié HDS.
- **R-09 (3/2)** : Violation de confidentialité des examens radiologiques non chiffrés ; nécessite un positionnement physique préalable sur le réseau local du centre.
- **R-10 (4/3)** : Prise de contrôle totale du domaine Active Directory ; scans de vulnérabilités et attaques automatisées permanentes contre les accès distants.
- **R-11 (3/3)** : Indisponibilité immédiate des archives et clichés diagnostiques ; usure mécanique et sollicitation continue des volumes disques.
- **R-12 (2/3)** : Dysfonctionnements applicatifs résorbables par restauration ; fréquence statistique élevée des erreurs de manipulation humaine lors de l'exploitation quotidienne.

---

## 4. Répartition des Risques par Niveau Inhérent

La répartition statistique des 12 scénarios sur la matrice $4 \times 4$ s'établit ainsi :

| Niveau Inhérent | Score ($G \times V$) | Nombre de Scénarios | Pourcentage | Scénarios |
|---|:---:|:---:|:---:|---|
| 🔴 **Critique** | 10 à 16 | **3** | 25 % | R-01, R-02, R-10 |
| 🟠 **Élevé** | 7 à 9 | **6** | 50 % | R-03, R-04, R-05, R-07, R-08, R-11 |
| 🟡 **Moyen** | 4 à 6 | **3** | 25 % | R-06, R-09, R-12 |
| 🟢 **Faible** | 1 à 3 | **0** | 0 % | Aucun |
| **Total** | | **12** | **100 %** | |

### Synthèse d'analyse :
1. **Priorité absolue (Niveau Critique)** : Les 3 scénarios critiques (R-01, R-02, R-10) combinent une exposition directe vers l'extérieur (phishing, passerelle VPN, services RDP) avec des privilèges permettant de paralyser le cœur de métier (chiffrement PACS/RIS ou prise de contrôle AD).
2. **Vulnérabilités de l'écosystème et défaillances (Niveau Élevé)** : 50 % des risques relèvent du niveau élevé, illustrant la dépendance du centre envers ses partenaires tiers (éditeur, mainteneurs, hébergeur HDS) et la criticité de l'infrastructure de stockage.
3. **Risques résiduels circonscrits (Niveau Moyen)** : Les risques R-06, R-09 et R-12 sont modérés par la résilience de l'exploitation locale et la facilité de restauration des configurations.

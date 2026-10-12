# Atelier 2 : Sources de Risque et Objectifs Visés (EBIOS RM)

L'Atelier 2 de la méthode EBIOS RM consiste à identifier qui pourrait attaquer le centre d'imagerie médicale (les **Sources de Risque - SR**) et ce que ces acteurs cherchent à accomplir (les **Objectifs Visés - OV**). Ces éléments sont ensuite croisés pour constituer les couples **SR/OV**, évalués selon leur niveau de pertinence sur une échelle de 1 à 4.

## 1. Sources de Risques (SR) retenues

Quatre sources de risques couvrant les menaces externes, internes et accidentelles ont été identifiées :

| ID | Nom de la Source | Type | Motivation | Ressources | Justification (Rationale EBIOS RM) |
|---|---|---|---|---|---|
| **sr_cybercriminels** | Groupe de cybercriminels | Malveillance externe | Gain financier (extorsion et revente de données de santé) | Importantes (outils offensifs avancés, botnets, RaaS) | **Retenue** : Principale menace pesant sur le secteur de la santé, motivée par la rentabilité de la double extorsion (chiffrement du PACS et chantage à la fuite de données). |
| **sr_interne_malveillant** | Employé malveillant ou compte usurpé | Malveillance interne | Vengeance, appât du gain ou contrainte suite à compromission | Modérées (accès légitimes internes et connaissances du SI) | **Retenue** : Les personnels et prestataires disposent d'accès réguliers aux consoles PACS/RIS et aux dossiers cliniques sensibles (DPI). |
| **sr_hacktivistes** | Hacktivistes | Malveillance externe | Atteinte à l'image, revendication idéologique et déstabilisation | Moyennes (attaques par déni de service distribué, défaçage) | **Retenue** : Le centre constitue une cible potentielle d'opportunité pour des actions d'indisponibilité médiatisées. |
| **sr_defaillance** | Défaillance technique ou accident | Non-malveillant / Accidentel | N/A | N/A | **Retenue** : L'infrastructure d'imagerie repose sur des équipements matériels et de stockage critiques soumis aux pannes et aléas d'exploitation. |

*(Données source : `grc/ebios/w2_sources.yaml`)*

## 2. Objectifs Visés (OV)

Quatre objectifs majeurs susceptibles d'être poursuivis par ces sources ont été retenus :

| ID | Nom de l'Objectif | Description détaillée |
|---|---|---|
| **ov_extorsion** | Extorsion par paralysie du SI et chantage | Chiffrement des données sensibles (PACS, DPI) et menace de publication pour contraindre au paiement d'une rançon financière. |
| **ov_vol_donnees** | Vol et exfiltration de données de santé | Exfiltration massive d'images médicales DICOM et d'identités de patients pour revente sur des forums illicites. |
| **ov_indisponibilite** | Indisponibilité des services et paralysie des soins | Interruption du fonctionnement du plateau technique ou du lien de téléradiologie empêchant la prise en charge des patients. |
| **ov_alteration** | Altération des données et comptes rendus médicaux | Modification malveillante ou corruption de comptes rendus et diagnostics radiologiques pouvant induire des erreurs médicales graves. |

*(Données source : `grc/ebios/w2_sources.yaml`)*

## 3. Matrice des Couples SR/OV Évalués et Retenus

L'analyse de pertinence des croisements SR $\times$ OV est évaluée sur une échelle de **1 à 4** (1: Négligeable, 2: Significative, 3: Forte, 4: Maximale). Conformément aux préconisations EBIOS RM, seuls les couples dont la pertinence est **supérieure ou égale à 2** sont retenus pour l'élaboration des scénarios stratégiques :

| ID | Source de Risque (SR) | Objectif Visé (OV) | Pertinence (1-4) | Description opérationnelle & Rationale |
|---|---|---|:---:|---|
| **srov_1** | Groupe de cybercriminels | Extorsion par paralysie du SI | **4** (Maximale) | Un groupe de cybercriminels cible le centre pour chiffrer le PACS et réclamer une rançon financière. |
| **srov_2** | Groupe de cybercriminels | Vol et exfiltration de données | **4** (Maximale) | Des cybercriminels s'infiltrent pour dérober des examens DICOM et données personnelles à des fins de revente. |
| **srov_3** | Employé malveillant ou compte usurpé | Vol et exfiltration de données | **3** (Forte) | Un employé malveillant ou un compte interne usurpé exfiltre des dossiers médicaux ciblés. |
| **srov_4** | Hacktivistes | Indisponibilité des services | **2** (Significative) | Des hacktivistes mènent une attaque DDoS saturant la connexion Internet et bloquant la téléradiologie pour nuire à l'image du centre. |
| **srov_5** | Défaillance technique ou accident | Indisponibilité des services | **3** (Forte) | Une panne majeure sur le stockage PACS ou le réseau local entraîne une interruption prolongée de l'activité. |
| **srov_6** | Groupe de cybercriminels | Altération des données médicales | **2** (Significative) | Attaquant externe (cybercriminels) infiltrant le réseau via un poste compromis d'une clinique partenaire pour altérer des comptes rendus radiologiques. Source externe retenue car plus plausible : l'attaquant exploite un rebond tiers pour contourner le périmètre du centre et modifier des diagnostics. |

*(Données source : `grc/ebios/w2_sources.yaml`)*

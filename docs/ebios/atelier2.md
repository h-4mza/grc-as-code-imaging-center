# Atelier 2 : Événements Redoutés (Sources de Risques et Objectifs Visés)

L'Atelier 2 de la méthode EBIOS RM consiste à identifier qui pourrait nous attaquer (les Sources de Risques - SR) et ce qu'ils cherchent à accomplir (les Objectifs Visés - OV). 

## 1. Sources de Risques (SR) retenues

En nous basant sur le rapport d'analyse de risques (NIST CSF 2.0), nous avons identifié les profils d'attaquants suivants :

1. **SR1 - Groupe de cybercriminels** (Malveillance externe) : Motivés par l'extorsion financière, disposant de ressources importantes (outils sophistiqués, RaaS).
2. **SR2 - Employé malveillant ou compromis** (Malveillance interne) : Motivé par la revente, la vengeance ou suite à la compromission de son compte.
3. **SR3 - Hacktivistes** (Malveillance externe) : Motivés par l'envie de nuire à l'image, ressources moyennes.
4. **SR4 - Défaillance technique / Accident** : Cas de panne matérielle majeure ou erreur humaine non intentionnelle.

## 2. Objectifs Visés (OV) par ces sources

1. **OV1 - Extorsion par paralysie du SI** : Chiffrement des données critiques (PACS, DPI) pour paralyser l'activité.
2. **OV2 - Vol de données de santé** : Exfiltration de données patients pour revente.
3. **OV3 - Atteinte à la continuité des soins** : Interruption des services, rendant la prise en charge ou la téléradiologie impossible.
4. **OV4 - Altération des données médicales** : Modification de comptes rendus ou images conduisant à une erreur de diagnostic.

## 3. Couples SR/OV évalués (Scénarios de haut niveau)

Les 6 couples SR/OV suivants ont été jugés pertinents pour le centre d'imagerie (voir `grc/ebios/w2_sources.yaml`) :

- **SROV_1 (Pertinence: 5/5)** : Un groupe de cybercriminels cible le centre pour chiffrer le PACS et demander une rançon (Extorsion).
- **SROV_2 (Pertinence: 4/5)** : Un groupe de cybercriminels s'infiltre pour voler massivement les données d'identification et de santé pour revente.
- **SROV_3 (Pertinence: 3/5)** : Un employé malveillant exfiltre des dossiers médicaux de patients spécifiques.
- **SROV_4 (Pertinence: 2/5)** : Des hacktivistes lancent une attaque DDoS bloquant la connexion Internet et la téléradiologie.
- **SROV_5 (Pertinence: 4/5)** : Une défaillance technique majeure des serveurs de stockage entraîne un arrêt prolongé de l'activité.
- **SROV_6 (Pertinence: 2/5)** : Un acteur compromettant un compte interne modifie un compte rendu radiologique.

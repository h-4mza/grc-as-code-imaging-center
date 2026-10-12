# Note d'Applicabilité Réglementaire : Centre d'Imagerie Médicale (CIM)

> [!WARNING]
> **Avertissement méthodologique et juridique :**  
> Cette note d'applicabilité constitue une analyse indicative fournie exclusivement à titre d'exercice dans le cadre d'un système d'information pédagogique et fictif. Elle n'est en aucun cas assimilable à un avis juridique formel, à une consultation d'avocat ou à une prise de position réglementaire opposable. Pour toute transposition à une situation réelle, cette analyse doit impérativement être validée par un juriste ou un avocat spécialisé en droit des technologies de l'information, de la santé et de la protection des données.

**Référence Document** : CIM-SEC-REG-001  
**Version** : 1.2 (Mise à jour GRC-as-Code — Contexte Transfrontalier)  
**Statut** : Brouillon pédagogique, SI fictif, aucune approbation réelle  
**Date** : Octobre 2026  

---

## 1. Contexte de l'organisation et Périmètre d'Application

Le Centre d'Imagerie Médicale (CIM) est modélisé comme une structure de santé privée de 16 collaborateurs spécialisée dans le radiodiagnostic (IRM, Scanner, Mammographie, Échographie). Le plateau technique exploite un système d'information articulé autour d'un PACS, d'un RIS, d'un dossier patient informatisé (DPI) et d'interfaces de télémaintenance biomédicale. Le centre prévoit d'assurer une continuité de service pour l'interprétation d'examens en téléradiologie en lien avec des cliniques partenaires locales et européennes.

**Enjeu de conformité croisée (Maroc / Union Européenne) :**  
Le centre est physiquement établi au Maroc. Dès lors, le cadre légal de référence obligatoire relève du droit marocain :
* **Loi n° 09-08** relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel, sous le contrôle de la **CNDP** (Commission Nationale de contrôle de la protection des Données à caractère Personnel) ;
* **Loi n° 05-20** relative à la cybersécurité (promulguée par le Dahir n° 1-20-69), fixant les règles de gouvernance et de sécurité des systèmes d'information sous l'égide de la **DGSSI** (Direction Générale de la Sécurité des Systèmes d'Information) et du **maCERT**.

Parallèlement, en raison de ses flux de téléradiologie avec des partenaires hospitaliers établis dans l'Union européenne et du traitement potentiel de données de ressortissants européens, le centre doit articuler son organisation avec les réglementations de l'UE (RGPD, NIS2). Cette articulation ne s'opère pas de manière indistincte ou automatique, mais selon des critères juridiques spécifiques d'extraterritorialité et de stipulations contractuelles détaillés ci-après.

---

## 2. Applicabilité de la Directive NIS2 (Directive (UE) 2022/2555)

L'évaluation de l'assujettissement du centre à la directive (UE) 2022/2555 (NIS2) fait l'objet d'une analyse méthodique en trois critères :

### 2.1. Analyse en trois temps : Secteur, Taille et Qualification

#### a) Critère sectoriel
La santé est classée parmi les **Secteurs hautement critiques** à l'Annexe I, point 5 de la directive NIS2. Cette annexe vise expressément les *"prestataires de soins de santé au sens de l'article 3, point g), de la directive 2011/24/UE"*. L'activité de radiodiagnostic relève par nature des prestations de soins de santé au sens fonctionnel de ce texte.

#### b) Règle du seuil de taille (Article 2 et Recommandation 2003/361/CE)
L'article 2, paragraphe 1 de NIS2 subordonne l'assujettissement direct à la règle du seuil de taille issue de l'annexe de la recommandation 2003/361/CE de la Commission européenne :
* Le périmètre obligatoire couvre en principe uniquement les entités qualifiées au minimum de **moyennes entreprises** (effectif $\ge 50$ personnes ou chiffre d'affaires / bilan annuel $> 10$ millions d'euros).
* Le CIM compte **16 personnes**, ce qui en fait une **petite entreprise** au sens de l'article 2, paragraphe 2 de ladite recommandation.
* En conséquence, le centre se situe **hors du périmètre direct** de NIS2 en vertu de la règle générale des seuils.

*Examen des exceptions de l'article 2, paragraphe 2 :*  
L'article 2(2) de NIS2 prévoit des dérogations permettant d'assujettir de petites entités indépendamment de leur taille dans des situations strictement circonscrites :
1. *Fournisseur exclusif* dans un État membre d'un service essentiel pour des activités économiques ou sociétales critiques ;
2. *Perturbation ayant un impact significatif* sur la sécurité publique, la sûreté publique ou la santé publique à l'échelle d'un État membre ;
3. *Risque systémique critique* pour des secteurs particuliers ;
4. *Entité identifiée comme critique* au sens de la directive (UE) 2022/2557 (résilience des entités critiques) ;
5. *Fournisseurs de réseaux de communications électroniques publics* ou de services de confiance / DNS.

*Motif de non-application :* Le CIM constitue un cabinet libéral de radiologie parmi d'autres, dépourvu de monopole territorial ou de délégation de service public exclusif au sein de l'UE. Aucune autorité nationale d'un État membre de l'UE n'a désigné le centre sous l'une de ces exceptions dérogatoires.

#### c) Qualification réglementaire (Article 3)
La distinction formelle entre **Entité Essentielle (EE)** et **Entité Importante (EI)** définie à l'article 3 de NIS2 repose sur le croisement du secteur et de la taille de l'entité. Étant donné que le centre n'entre pas dans le champ d'application direct de la directive, **cette qualification n'a pas lieu d'être prononcée pour cette structure**.

### 2.2. Critère de territorialité (Article 26)
L'article 26 de la directive NIS2 régit la compétence et la juridiction territoriale : la directive s'applique aux entités établies sur le territoire de l'Union européenne. Les règles spécifiques d'extraterritorialité (représentant légal dans l'UE) ne visent que des catégories très ciblées de fournisseurs de services numériques tiers (DNS, cloud, places de marché, moteurs de recherche) et non les prestataires physiques de soins de santé.

En tant qu'établissement de santé situé et immatriculé au **Maroc**, le CIM **n'est pas couvert directement** par la directive NIS2.

### 2.3. Posture retenue : Alignement volontaire et chaîne d'approvisionnement

Bien que non assujetti directement, le CIM retient une posture proactive d'alignement pour deux motifs opérationnels majeurs :
1. **Référentiel de bonnes pratiques :** L'article 21 de NIS2 constitue l'état de l'art européen en matière de mesures de gouvernance et de gestion des risques cyber (hygiène informatique, gestion des vulnérabilités, sauvegardes, MFA, segmentation réseau). Le CIM s'en inspire directement pour bâtir son référentiel de sécurité.
2. **Exigence contractuelle via la chaîne d'approvisionnement (Article 21(2)d) :** Les cliniques et établissements hospitaliers européens partenaires du centre relèvent potentiellement de NIS2 en tant qu'entités essentielles ou importantes. En vertu de l'article 21, paragraphe 2, point d), ces entités ont l'obligation légale de sécuriser leur chaîne d'approvisionnement et de répercuter contractuellement des exigences de cybersécurité strictes sur leurs tiers, sous-traitants et partenaires de téléradiologie.

### 2.4. Synthèse hypothétique : Si le centre entrait dans le périmètre

À titre d'exercice d'anticipation, le tableau suivant illustre les exigences qui s'imposeraient au centre dans l'hypothèse d'une extension de périmètre (croissance d'effectif ou implantation dans l'UE), sans affirmer qu'elles constituent des obligations légales actuelles pour le centre :

| Article NIS2 | Objet de l'exigence | Dispositif simulé / Cible opérationnelle |
|:---|:---|:---|
| **Article 21(1) & (2)** | Mesures de gestion des risques de cybersécurité (politiques de sécurité, gestion des incidents, continuité d'activité, supply chain, hygiène informatique, chiffrement, MFA) | Transposition visée via les 93 contrôles ISO 27001:2022 et le traitement des 12 risques opérationnels (R-01 à R-12). |
| **Article 23(4)a** | **Alerte précoce sous 24 heures** auprès du CSIRT ou de l'autorité compétente | Procédure d'escalade d'urgence à formaliser en cas d'incident majeur suspecté d'origine malveillante ou à impact transfrontalier. |
| **Article 23(4)b** | **Notification d'incident sous 72 heures** | Mise à jour de l'évaluation initiale (gravité, impact, indicateurs de compromission) prévue dans le plan de réponse à incident. |
| **Article 23(4)c** | **Rapport intermédiaire** (sur demande) | Production d'un point de situation technique prévu à la demande des autorités. |
| **Article 23(4)e** | **Rapport final sous 1 mois** | Rapport de clôture à formaliser intégrant la description de l'incident, la cause racine, les mesures d'atténuation et l'impact réel. |

---

## 3. Applicabilité du RGPD (Règlement (UE) 2016/679) et Droit Local Marocain

### 3.1. Analyse d'application territoriale du RGPD (Article 3)

Le RGPD ne s'applique pas au CIM sur le fondement de l'article 3(1) (absence d'établissement sur le territoire de l'Union). Son applicabilité doit être appréciée à la lumière de l'article 3, paragraphe 2 :

* **Critère de l'article 3(2) du RGPD :** Le règlement s'applique au traitement de données de personnes se trouvant dans l'UE par un responsable ou sous-traitant non établi dans l'UE si les activités sont liées :
  * à l'offre de biens ou de services à ces personnes dans l'UE (art. 3(2)a) ;
  * au suivi de leur comportement dans l'UE (art. 3(2)b).
* **Qualification des rôles (Responsable de traitement vs Sous-traitant) :**
  * Dans le cadre de la téléradiologie transfrontalière, les cliniques partenaires européennes agissent en tant que **Responsables de traitement** (elles collectent les données des patients et prescrivent les examens).
  * Le CIM intervient en qualité de **Sous-traitant** (Article 4, point 8 et Article 28 du RGPD) pour exécuter la prestation d'interprétation radiologique au nom et pour le compte de ces cliniques.
  * Si le centre venait à proposer directement ses services de téléradiologie à des patients résidant dans l'UE (sans intermédiaire hospitalier européen), il agirait en tant que responsable de traitement sous l'article 3(2)a.
* **Encadrement contractuel obligatoire (Article 28 du RGPD) :**
  En qualité de sous-traitant, les obligations RGPD s'imposent au CIM **par contrat** (convention d'externalisation / *Data Processing Agreement* - DPA). Le centre s'engage contractuellement à :
  * ne traiter les données que sur instruction documentée du responsable de traitement ;
  * mettre en œuvre les mesures techniques et organisationnelles appropriées (Article 32) ;
  * notifier au responsable de traitement toute violation de données dans les meilleurs délais après en avoir pris connaissance (Article 33, paragraphe 2) ;
  * assister le responsable pour la réalisation des analyses d'impact (AIPD).
* **Transferts internationaux de données vers un pays tiers (Chapitre V, Articles 44 à 49) :**
  La transmission d'examens radiologiques depuis l'UE vers le Maroc constitue un transfert de données à caractère personnel vers un pays tiers. Le Maroc ne faisant pas l'objet d'une décision d'adéquation de la Commission européenne (Art. 45), le transfert doit obligatoirement être sécurisé par des garanties appropriées au sens de l'**Article 46 du RGPD**. L'instrument juridique retenu consiste en la signature des **Clauses Contractuelles Types (CCT / SCC)** adoptées par la Commission européenne (Décision d'exécution (UE) 2021/914), complétées d'une évaluation d'impact du transfert (*Transfer Impact Assessment* - TIA).

**Conclusion d'applicabilité RGPD :** Le cadre européen est **applicable par contrat et, selon les cas, article 3(2)**.

### 3.2. Catégories particulières de données (Article 9)
Les clichés DICOM, comptes rendus diagnostiques et historiques cliniques constituent des **Données concernant la santé** au sens de l'article 4(15) et de l'article 9 du RGPD. Le traitement de ces données est ciblé sous l'exception de l'article 9, paragraphe 2, point h) (fourniture de soins de santé, diagnostics médicaux et gestion des systèmes de soins) sous la responsabilité de professionnels soumis au secret médical.

### 3.3. Droit local marocain de référence (Loi 09-08 et Loi 05-20)

En tant qu'entité opérant sur le territoire marocain, le centre est soumis prioritairement à la législation nationale :
* **Loi n° 09-08 (CNDP) :**
  * Le traitement de données sensibles (données de santé) requiert l'autorisation préalable de la **CNDP** (Articles 12 et suivants).
  * Les transferts transfrontaliers de données de santé (vers les cliniques européennes ou vers des prestataires d'archivage distants) sont subordonnés à une déclaration ou demande d'autorisation de transfert auprès de la CNDP conformément aux articles 43 et 44 de la loi 09-08.
  * Les droits des personnes (information, accès, rectification, opposition) doivent être garantis conformément aux articles 5 et suivants.
* **Loi n° 05-20 (Cybersécurité) :**
  * Fixe le cadre national de gouvernance de la sécurité des systèmes d'information pour les entités exploitant des infrastructures critiques ou sensibles.
  * Définit les obligations d'audit régulier des SI, d'homologation de sécurité et de déclaration des cyberincidents majeurs auprès de la **DGSSI** / **maCERT**.

---

## 4. Applicabilité du Référentiel HDS (Hébergement de Données de Santé)

### 4.1. Principe juridique et périmètre de la certification HDS
L'obligation de certification **HDS** (*Hébergement de Données de Santé*) découle de l'article **L. 1111-8 du Code de la santé publique (CSP) français**.

*Portée juridique pour le centre :*  
* La certification HDS est une exigence de droit national français. Elle **ne s'applique pas directement au CIM marocain en tant que centre médical**, celui-ci n'étant ni établi sur le territoire français, ni lui-même fournisseur de services d'hébergement pour compte de tiers.
* En revanche, l'obligation HDS **concerne les hébergeurs de clients et partenaires français** du centre : lorsque des cliniques françaises confient des examens d'imagerie nécessitant un archivage externe ou une sauvegarde dans le cloud, elles doivent veiller à ce que l'hébergeur physique ou infogérant retenu soit titulaire d'un certificat HDS valide (activités 1 à 6).

### 4.2. Traduction opérationnelle pour le CIM (en cible)
* **Sauvegardes et archivage externalisés :** Pour répondre aux obligations contractuelles de ses clients français et garantir la résilience de son propre archivage PACS (VNA), le CIM a pour objectif de confier ses sauvegardes externalisées à un fournisseur cloud certifié HDS et ISO 27001 (couvrant le risque **R-08** : *Destruction des sauvegardes hébergées HDS*).
* **Contrôle ISO 27001 associé :** Cette exigence est suivie via le contrôle **5.23 (Sécurité des services cloud)**. La maturité actuelle est évaluée à **3/5** (traitement *TR-08* planifié pour formaliser l'immutabilité WORM et le cloisonnement des accès cloud).

---

## 5. Matrice de Conformité et Alignement EBIOS RM (12 Scénarios)

Le tableau ci-dessous synthétise l'articulation entre les exigences de conformité, les 12 scénarios de risques opérationnels modélisés dans `w4_operationnels.yaml` (R-01 à R-12) et les contrôles ISO 27001:2022 correspondants :

| Référentiel / Cadre | Portée pour le CIM | Scénarios de Risque Liés (w4_operationnels.yaml) | Contrôles ISO 27001 Clés (Exemples) |
|:---|:---|:---|:---|
| **Loi 09-08 (Maroc / CNDP)** | Droit national obligatoire (données de santé, déclarations et autorisations de transfert CNDP) | **R-02** (Exfiltration VPN téléradiologie), **R-05** (Vol de données internes / USB) | **5.34** (Données personnelles), **8.12** (DLP / Fuite de données), **8.24** (Cryptographie) |
| **Loi 05-20 (Maroc / DGSSI)** | Droit national de cybersécurité (résilience des SI, déclaration d'incidents maCERT) | **R-01** (Ransomware PACS), **R-06** (DDoS ligne Internet), **R-10** (Brute force RDP) | **5.24** (Gestion incidents), **8.7** (Protection malwares), **8.20** (Sécurité réseaux) |
| **RGPD (UE 2016/679)** | Applicable par contrat (Art. 28) et selon les cas (Art. 3(2)a, Transferts Chapitre V / SCC) | **R-02** (Exfiltration téléradiologie), **R-05** (Vol données USB), **R-07** (Rebond clinique partenaire) | **5.14** (Transfert d'information), **5.19** (Sécurité fournisseurs), **8.24** (Chiffrement TLS) |
| **NIS2 (UE 2022/2555)** | Hors périmètre direct (règle seuil PME & territorialité) ; alignement volontaire et exigences supply chain (Art. 21(2)d) | **R-01** (Ransomware), **R-03** (Supply chain PACS), **R-04** (Télémaintenance IRM), **R-10** (RDP) | **5.21** (Chaîne d'approvisionnement), **8.5** (MFA), **8.8** (Gestion des vulnérabilités), **8.22** (Segmentation) |
| **HDS (CSP France)** | Concerne les hébergeurs des partenaires français ; exigence contractuelle répercutée sur le cloud de sauvegarde | **R-08** (Destruction des sauvegardes hébergées HDS), **R-11** (Panne stockage primaire) | **5.23** (Sécurité services cloud), **8.13** (Sauvegardes), **8.14** (Redondance et résilience) |

*Note de traçabilité :* L'ensemble des 12 risques opérationnels (R-01 à R-12) font l'objet d'un suivi dynamique et de plans de traitement formalisés dans le référentiel GRC-as-Code de la structure.

# Méthode de Cotation et Scoring des Risques (EBIOS RM & ISO 27001)

Ce document décrit la méthode mathématique standardisée de calcul des niveaux de risque au sein de la plateforme **GRC-as-Code**, unifiée dans la fonction `compute_risk_view()` du module `app/services/scoring.py`.

---

## 1. Matrice de Risque EBIOS RM (Échelle 1–4)

L'évaluation s'appuie sur la matrice $4 \times 4$ préconisée par la méthode ANSSI EBIOS RM :

$$\text{Score} = \text{Gravité } (G) \times \text{Vraisemblance } (V)$$

Les deux dimensions sont strictement bornées sur l'intervalle entier $[1, 4]$ :

| Niveau | Gravité ($G$) | Vraisemblance ($V$) |
| :--- | :--- | :--- |
| **1** | Mineure | Minime / Très peu probable |
| **2** | Significative | Significative / Plausible |
| **3** | Grave | Forte / Très probable |
| **4** | Critique | Maximale / Quasi-certain |

### Seuils de Cotation

| Plage de Score ($G \times V$) | Niveau Qualitatif | Description Opérationnelle |
| :---: | :---: | :--- |
| **1 à 3** | **Faible** | Risque mineur, surveillance normale sans mesures contraignantes immédiates. |
| **4 à 6** | **Moyen** | Risque significatif, arbitrages de sécurité et suivi requis. |
| **7 à 9** | **Élevé** | Risque majeur, plan de réduction impératif à court/moyen terme. |
| **10 à 16** | **Critique** | Risque intolérable, action prioritaire immédiate et revue en comité de direction. |

---

## 2. Règle des Constats Opérationnels (SecOps / Télémétrie)

La vraisemblance inhérente $V$ est ajustée dynamiquement en fonction des constats de sécurité ouverts (CVE, failles AD, audits) rattachés au scénario de risque :

- **Règle :** Si au moins un constat ouvert de sévérité `error` est lié au scénario (via correspondance de technique MITRE ATT&CK ou actif), la vraisemblance est relevée d'un cran :
  $$V_{\text{ajustée}} = \min(4, V + 1)$$
- **Plafonnement :** La vraisemblance ajustée est strictement plafonnée à 4.
- **Constats de sévérité inférieure (`warning`, `info`) :** Ne provoquent pas d'escalade immédiate de la vraisemblance.

---

## 3. Règle de Maturité ISO 27001 (Déclaration d'Applicabilité)

Le niveau de risque résiduel actuel (*Current Residual*) est calculé à partir du niveau d'efficacité réel des mesures de sécurité déployées :

### 3.1 Calcul de la Maturité Moyenne ($M$)

Pour chaque risque, la maturité moyenne $M$ est calculée à partir des contrôles ISO 27001 associés (table `risk_control`) :

$$M = \frac{1}{N} \sum_{i=1}^{N} \text{maturité}_i \quad (0 \le \text{maturité}_i \le 5)$$

- **Contrôles non applicables :** Les contrôles dont `is_applicable = false` sont **strictement ignorés** du calcul de la moyenne.
- **Absence de contrôle lié :** Si aucun contrôle applicable n'est lié au risque, la maturité est fixée à $M = 0.0$.

### 3.2 Atténuation de la Vraisemblance Résiduelle ($V_{\text{résiduelle}}$)

La maturité moyenne des contrôles agit par atténuation de la vraisemblance :

| Maturité Moyenne ($M$) | Atténuation | Formule de la Vraisemblance Résiduelle |
| :---: | :---: | :--- |
| **$M \ge 4.0$** (Haute maturité) | **-2 crans** | $V_{\text{res}} = \max(1, V_{\text{ajustée}} - 2)$ |
| **$2.5 \le M < 4.0$** (Maturité intermédiaire) | **-1 cran** | $V_{\text{res}} = \max(1, V_{\text{ajustée}} - 1)$ |
| **$M < 2.5$** (Faible maturité / Aucun contrôle) | **0 cran** | $V_{\text{res}} = V_{\text{ajustée}}$ |

### 3.3 Score et Niveau Résiduel Actuel

Le score résiduel actuel et son niveau qualitatif sont déduits :

$$\text{Score Résiduel} = G \times V_{\text{res}}$$
$$\text{Niveau Résiduel} = \text{calculate\_level}(G, V_{\text{res}})$$

---

## 4. Niveau Cible (*Target Residual*) et Détection des Écarts

Le niveau résiduel cible (*Target Residual*) est lu directement dans le champ `expected_residual` du plan de traitement associé au risque dans l'atelier 5 (`w5_traitements.yaml`) :

- **Trajectoire complète d'un risque :**
  $$\text{Inhérent} \longrightarrow \text{Résiduel Actuel} \longrightarrow \text{Cible}$$
- **Détection des écarts dans le Dashboard :** Un risque dont le résiduel actuel dépasse le niveau cible sans plan de traitement actif (`status: in_progress`) est automatiquement signalé en alerte prioritaire.
- **Règle de conformité de l'option "accept" :** L'acceptation formelle d'un risque n'est recevable que si le niveau résiduel cible calculé est inférieur ou égal à **Moyen** ($\le 6$).

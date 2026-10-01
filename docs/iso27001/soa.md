# Déclaration d'Applicabilité (SoA) - ISO 27001:2022

La Déclaration d'Applicabilité (Statement of Applicability - SoA) justifie les choix d'implémentation des 93 contrôles de l'Annexe A de la norme ISO 27001:2022.

*État d'avancement (Passe 1) : Thèmes Organisationnel (5) et Technologique (8) complétés.*

## 1. Thème Organisationnel (Contrôles 5.x)

Les contrôles organisationnels définissent le cadre de gouvernance et les processus.

| ID | Nom | Applicable | Maturité (0-5) | État | Preuve |
|---|---|---|---|---|---|
| **5.1** | Politiques en matière de SSI | Oui | 3 | En place | P-SSI-01 signée |
| **5.2** | Rôles et responsabilités | Oui | 2 | Partiel | Charte IT |
| **5.3** | Séparation des tâches | Oui | 3 | En place | Matrice_RBAC |
| **5.9** | Inventaire des actifs | Oui | 3 | En place | assets.yaml |
| **5.24**| Gestion des incidents | Oui | 2 | En place | Procédure P-INC-01 |

*(Extrait représentatif. Données complètes dans `grc/iso27001/annex_a.yaml`)*

## 2. Thème Technologique (Contrôles 8.x)

Les contrôles technologiques protègent directement l'infrastructure (réseau, serveurs, postes de travail, cloud).

| ID | Nom | Applicable | Maturité (0-5) | État | Preuve |
|---|---|---|---|---|---|
| **8.1** | Appareils terminaux | Oui | 2 | Partiel | Antivirus sans EDR |
| **8.3** | Restriction d'accès (DPI) | Oui | 3 | En place | Droits RBAC DPI |
| **8.4** | Accès au code source | **Non** | 0 | N/A | Pas de développement |
| **8.5** | Authentification sécurisée | Oui | 1 | Non initié | MFA non déployé |
| **8.13**| Sauvegarde de l'information | Oui | 3 | En place | Sauvegardes HDS |

*(Extrait représentatif. Données complètes dans `grc/iso27001/annex_a.yaml`)*

## Prochaines étapes
- Passe 2 : Évaluation des thèmes 6 (Personnes) et 7 (Physique).

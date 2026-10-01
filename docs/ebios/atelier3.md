# Atelier 3 : Scénarios Stratégiques (Écosystème)

L'Atelier 3 de la méthode EBIOS RM cartographie l'écosystème du centre d'imagerie médicale. L'objectif est de comprendre comment un attaquant pourrait utiliser les fournisseurs, partenaires ou sous-traitants pour atteindre ses objectifs (vulnérabilités de la chaîne d'approvisionnement).

## 1. Cartographie de l'Écosystème

Nous avons identifié 5 parties prenantes principales interagissant directement avec le SI du centre :

1. **Cliniques partenaires** (Menace: 3/5) : Interconnexion continue pour l'échange de dossiers médicaux.
2. **Service de téléradiologie** (Menace: 3/5) : Connexion VPN critique pour les gardes et les urgences nocturnes.
3. **Éditeur du PACS** (Menace: 4/5) : Fournisseur du cœur du système, disposant d'un accès à privilèges pour la télémaintenance.
4. **Hébergeur HDS** (Menace: 2/5) : Stocke les sauvegardes externalisées. Un acteur généralement bien sécurisé mais critique.
5. **Mainteneurs biomédicaux** (Menace: 4/5) : Techniciens intervenant sur les Scanners et IRM, souvent avec des clés USB ou des accès distants non monitorés.

## 2. Scénarios Stratégiques

En croisant les couples SR/OV (Atelier 2) avec ces parties prenantes, nous avons défini 5 scénarios stratégiques :

| ID | Vecteur (Partie prenante) | Menace & Objectif (SR/OV) | Vraisemblance | Description |
|---|---|---|---|---|
| **SC_STRAT_1** | Éditeur du PACS | Ransomware (Cybercriminels) | 3/5 | Attaque par la chaîne d'approvisionnement (Supply Chain) : déploiement d'une mise à jour malveillante. |
| **SC_STRAT_2** | Service de téléradiologie | Vol de données (Cybercriminels) | 4/5 | Rebond depuis l'infrastructure du téléradiologue via le tunnel VPN existant. |
| **SC_STRAT_3** | Mainteneurs biomédicaux | Ransomware (Cybercriminels) | 4/5 | Utilisation des identifiants volés d'un mainteneur pour entrer via le portail de télémaintenance d'un scanner. |
| **SC_STRAT_4** | Cliniques partenaires | Altération (Hacktiviste/Interne) | 3/5 | Usurpation de session depuis un poste infecté de la clinique pour falsifier un diagnostic. |
| **SC_STRAT_5** | Hébergeur HDS | Continuité (Défaillance/Cyber) | 2/5 | Panne ou compromission de l'hébergeur entraînant l'impossibilité de restaurer en cas de sinistre local. |

*(Données source : `grc/ebios/w3_strategiques.yaml`)*

# Politique de Sécurité (Security Policy)

## 🏥 Déclaration sur la nature des données (Cadre fictif)

Ce projet est un projet de recherche et une démonstration pédagogique de démarche **GRC-as-code** appliquée au secteur de la santé :

- **Système d'Information Fictif** : L'ensemble des architectures, actifs, scénarios de risque, contrôles et processus décrits dans ce dépôt modélise un centre d'imagerie médicale fictif de 16 personnes.
- **Absence de Données Réelles de Santé** : Ce dépôt ne contient aucune donnée à caractère personnel (DCP), aucune donnée médicale réelle, ni aucun identifiant patient réel. Tous les identifiants, journaux et exemples sont synthétiques et à visée d'illustration.
- **Identifiants de Démonstration** : Les mots de passe et clés d'API présents dans `docker-compose.yml`, `.env.example` et les jeux de tests (`grc_password`, `fake_token`, etc.) sont exclusivement destinés à l'exécution locale de la démo et aux tests automatisés. Ils ne doivent sous aucun prétexte être déployés en environnement de production.

---

## 🔒 Signalement d'une vulnérabilité

Si vous identifiez une vulnérabilité de sécurité dans le code source ou la configuration de ce dépôt :

1. **Rapport privé GitHub (Recommandé)** :  
   Utilisez la fonctionnalité [GitHub Private Vulnerability Reporting](https://github.com/h-4mza/grc-as-code-imaging-center/security/advisories/new) sous l'onglet **Security** du dépôt pour soumettre un rapport confidentiel.
2. **Contact direct** :  
   À défaut, vous pouvez contacter directement le propriétaire et mainteneur du projet ([@h-4mza](https://github.com/h-4mza)) via son profil GitHub ou par e-mail direct.

Merci de **ne pas ouvrir d'issue publique** pour signaler une vulnérabilité de sécurité non corrigée.

### Processus de traitement
- **Accusé de réception** : Sous 48 à 72 heures ouvrées.
- **Analyse et remédiation** : Évaluation de l'impact, développement d'un correctif et publication d'une version corrective accompagnée de notes de version (advisory).

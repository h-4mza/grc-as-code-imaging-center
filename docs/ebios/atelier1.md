# Atelier 1 : Contexte et Périmètre (Imagerie Médicale)

## 1. Description du centre

Le centre d'imagerie médicale étudié est un établissement privé disposant de :
- 2 Scanners TDM
- 1 IRM 3 Tesla
- 3 Tables de radiologie numérique directe (DR)
- 1 Salle d'échographie
- 1 Équipement de mammographie numérique

L'équipe est composée de 4 médecins radiologues, 8 manipulateurs, 3 secrétaires et 1 technicien informatique.
Le centre traite environ 150 examens par jour (générant 80 Go de données DICOM).

## 2. Processus métiers critiques

L'analyse des processus métiers a permis d'identifier 6 flux d'informations critiques :

1. **Prise en charge patient** : Accueil, vérification, enregistrement DPI/RIS, consentement.
2. **Acquisition des images** : Réalisation de l'examen et transfert DICOM.
3. **Interprétation et compte rendu** : Visualisation, rédaction CR, signature, envoi MSSanté.
4. **Téléradiologie** : Transfert chiffré VPN, interprétation à distance.
5. **Archivage et traçabilité** : Conservation 10 ans des images dans le PACS.
6. **Administration et facturation** : Gestion rendez-vous et feuilles de soins.

Ces processus sont définis dans le fichier source `grc/si/business_values.yaml`.

## 3. Enjeux de sécurité

- **Réglementaires** : RGPD, certification HDS, notification CNIL.
- **Disponibilité** : Critique pour les urgences.
- **Intégrité** : Un enjeu vital pour les images diagnostiques.
- **Équipements connectés** : OS souvent obsolètes difficiles à mettre à jour.

## 4. Actifs critiques

Les actifs identifiés (voir `grc/si/assets.yaml`) ont été cartographiés. Les 4 actifs les plus critiques (score 5/5) sont :
- Le PACS (Picture Archiving and Communication System)
- Les équipements d'imagerie lourds (Scanner / IRM)
- Le Dossier Patient Informatisé (DPI)
- Le RIS (Radiology Information System)

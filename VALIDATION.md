# État de validation — 9 novembre 2026

## Observé sur le déploiement original

- Deployment Flask : 3/3 réplicas disponibles.
- Deployment PostgreSQL : 1/1 disponible.
- Trois Pods Flask et un Pod PostgreSQL : Running, sans redémarrage lors de la lecture.
- PVC PostgreSQL : Bound, capacité 1 Gio.
- Docker Compose : application démarrée, PostgreSQL healthy.
- Résilience : l’échange précédent conserve la suppression du Pod se terminant par `47pt9`, puis l’apparition du Pod `6mhwf`. Ce dernier est toujours présent lors de cette vérification. Le test de suppression n’a pas été rejoué.

## Copie pour remise

Les fichiers de configuration ont été nettoyés pour remplacer les valeurs secrètes codées en dur. L’application originale, ses volumes et son cluster n’ont pas été modifiés. Le README distingue les résultats de l’original du nouveau déploiement à reproduire.

Tests de la copie nettoyée : syntaxe Python, ajout/lecture/modification/suppression en base mémoire, doublon e-mail, champs obligatoires et identifiant absent : réussis. Validation de la configuration Docker Compose : réussie. Le nouveau déploiement Kubernetes n’a pas été exécuté.

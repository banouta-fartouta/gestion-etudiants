# Gestion des étudiants — Docker & Kubernetes

Mini-projet pédagogique : application web CRUD Flask, base PostgreSQL, conteneurisation Docker et orchestration Kubernetes avec Minikube.

## Fonctionnalités

- Ajouter, consulter, modifier et supprimer un étudiant.
- Champs obligatoires et unicité de l’adresse e-mail.
- PostgreSQL partagé entre les réplicas Flask et stockage persistant.
- Mise à l’échelle à trois réplicas et remplacement automatique d’un Pod.

## Architecture

Navigateur → Flask / SQLAlchemy → PostgreSQL 16.
Avec Kubernetes : port-forward → Service mon-crud-service → Pods Flask → Service postgres-service → PostgreSQL → PVC de 1 Gio.

## Prérequis

Python 3.11 ou ultérieur, Docker Desktop en mode Linux et Docker Compose. Pour Kubernetes : kubectl et Minikube installés. Commandes ci-dessous pour PowerShell, depuis ce dossier.

## 1. Application locale (SQLite)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Ouvrir http://127.0.0.1:5000. SQLite est réservé au lancement local et son fichier n’est pas livré. Arrêter avec Ctrl+C.

## 2. Image Docker seule (SQLite)

```powershell
docker build -t mon-crud:v1 .
docker run --rm --name gestion-etudiants-demo -p 127.0.0.1:8080:5000 mon-crud:v1
```

Ouvrir http://localhost:8080. Ce mode est une démonstration : les données disparaissent à la suppression du conteneur. Utiliser un autre port si 8080 est déjà occupé.

## 3. Docker Compose et PostgreSQL

```powershell
py scripts/init_env.py
docker compose up -d --build
docker compose ps
docker compose logs --tail=30 web
```

Ouvrir http://localhost:8081. Le script crée des valeurs aléatoires dans `.env` et refuse d’écraser un fichier existant. Le fichier est exclu de Git et de l’image. Le volume `postgres_data` conserve la base. Pour arrêter sans effacer les données : `docker compose down`.

Ne pas changer le mot de passe d’un volume PostgreSQL déjà initialisé : modifier `.env` ne modifie pas le mot de passe en base. Pour tester cette copie à côté de l’original, utiliser un projet Compose distinct et un port libre.

## 4. Kubernetes avec Minikube

Utiliser un espace dédié pour ne pas modifier le déploiement original déjà validé.

```powershell
minikube start --driver=docker
docker build -t mon-crud:v1 .
minikube image load mon-crud:v1
kubectl create namespace gestion-etudiants-demo
kubectl -n gestion-etudiants-demo create secret generic gestion-etudiants-secrets --from-env-file=.env
kubectl -n gestion-etudiants-demo apply -f kubernetes/deployment.yaml
kubectl -n gestion-etudiants-demo rollout status deployment/postgres --timeout=180s
kubectl -n gestion-etudiants-demo rollout status deployment/mon-crud --timeout=180s
kubectl -n gestion-etudiants-demo port-forward service/mon-crud-service 8082:5000
```

Ouvrir http://localhost:8082. Garder le terminal du port-forward ouvert. Si ce port est déjà occupé, choisir par exemple `8083:5000`. PostgreSQL peut démarrer après Flask ; un redémarrage initial du Pod Flask peut alors survenir. Vérifier le rollout avant de poursuivre.

## 5. Scaling et résilience

Le manifeste démarre volontairement avec un réplica pour montrer le passage à trois. Attendre le premier démarrage avant de scaler pour que la table soit initialisée.

```powershell
kubectl -n gestion-etudiants-demo scale deployment mon-crud --replicas=3
kubectl -n gestion-etudiants-demo rollout status deployment/mon-crud
kubectl -n gestion-etudiants-demo get deployments,pods,services,pvc
$demoPod = kubectl -n gestion-etudiants-demo get pods -l app=mon-crud -o jsonpath='{.items[0].metadata.name}'
kubectl -n gestion-etudiants-demo delete pod $demoPod
kubectl -n gestion-etudiants-demo get pods -w
```

Arrêter l’observation avec Ctrl+C une fois les trois Pods prêts. Capturer l’ancien nom, le nouveau nom et l’état `3/3`. Le test ne prouve pas une haute disponibilité de PostgreSQL, qui reste à un seul réplica. Relancer le port-forward s’il s’interrompt.

## Validation et remise

Voir [VALIDATION.md](VALIDATION.md) pour les résultats observés et [REMISE.md](REMISE.md) pour la checklist. Le code livré est une copie nettoyée : les secrets sont maintenant fournis séparément. Les validations de l’ancien déploiement ne valent pas validation complète de cette configuration nettoyée.

## Limites

Projet d’apprentissage utilisant le serveur de développement Flask, sans authentification ni protection CSRF. À exécuter localement avec des données fictives ; ce n’est pas un service destiné à être exposé sur Internet. Les Secrets Kubernetes ne constituent pas à eux seuls un chiffrement au repos. Les dépendances sont contraintes par plage de versions, sans verrouillage exact.

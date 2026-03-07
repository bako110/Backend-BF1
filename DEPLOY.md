# 🚀 Déploiement sur Fly.io

Ce guide explique comment déployer votre backend BF1 sur Fly.io.

## 📋 Prérequis

1. **Compte Fly.io** : Créez un compte sur [fly.io](https://fly.io)
2. **MongoDB Atlas** : Base de données MongoDB hébergée
3. **Cloudinary** : Pour la gestion des médias (optionnel)

## 🛠 Installation de Fly CLI

### Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri https://fly.io/install.ps1 -UseBasicParsing | Invoke-Expression
```

### macOS/Linux
```bash
curl -L https://fly.io/install.sh | sh
```

## 🔧 Configuration

### 1. Connexion à Fly.io
```bash
fly auth login
```

### 2. Initialisation de l'application
```bash
# Dans le répertoire de votre projet
fly launch --no-deploy
```

### 3. Configuration des variables d'environnement
```bash
# Variables obligatoires
fly secrets set MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/bf1_db_prod"
fly secrets set JWT_SECRET_KEY="votre_cle_secrete_tres_forte"
fly secrets set CLOUDINARY_CLOUD_NAME="votre_cloud_name"
fly secrets set CLOUDINARY_API_KEY="votre_api_key"
fly secrets set CLOUDINARY_API_SECRET="votre_api_secret"

# Variables optionnelles
fly secrets set EMAIL_HOST="smtp.gmail.com"
fly secrets set EMAIL_PORT="587"
fly secrets set EMAIL_USER="votre_email@gmail.com"
fly secrets set EMAIL_PASSWORD="votre_app_password"
fly secrets set ALLOWED_ORIGINS_STR="https://votredomaine.com"
```

### 4. Configuration du domaine (optionnel)
```bash
# Ajouter un domaine personnalisé
fly ips allocate-v4
fly ips allocate-v6

# Configurer le certificat SSL
fly certs create votredomaine.com
```

## 🚀 Déploiement

### Premier déploiement
```bash
fly deploy
```

### Déploiements suivants
```bash
fly deploy
```

### Déploiement avec monitoring
```bash
fly deploy --strategy rolling
```

## 📊 Monitoring et Gestion

### Vérifier le statut
```bash
fly status
```

### Voir les logs
```bash
fly logs
```

### Ouvrir l'application
```bash
fly open
```

### Accéder au terminal
```bash
fly ssh console
```

### Scaling
```bash
# Augmenter les ressources
fly scale memory 1024  # 1GB RAM
fly scale count 2      # 2 instances

# Réduire pour économiser
fly scale memory 512   # 512MB RAM
fly scale count 1      # 1 instance
```

## 🔍 Test de l'API

Une fois déployé, testez votre API :

```bash
# Santé de l'API
curl https://votre-app.fly.dev/health

# Documentation Swagger
https://votre-app.fly.dev/docs
```

## 🛠 Configuration avancée

### Mise à l'échelle automatique
Éditez `fly.toml` :
```toml
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  max_machines_running = 10
```

### Volumes persistants (si nécessaire)
```bash
fly volumes create data --size 10 --region cdg
```

### Base de données Redis (optionnel)
```bash
fly redis create
# Puis ajouter REDIS_URL dans les secrets
```

## 🔧 Dépannage

### Problèmes courants

1. **Erreur de connexion MongoDB**
   - Vérifiez MONGODB_URI
   - Autorisez l'IP de Fly.io dans MongoDB Atlas

2. **Application qui ne démarre pas**
   ```bash
   fly logs --app votre-app
   ```

3. **Problèmes de mémoire**
   ```bash
   fly scale memory 1024
   ```

4. **Réinitialiser les secrets**
   ```bash
   fly secrets list
   fly secrets unset SECRET_NAME
   ```

## 📞 Support

- [Documentation Fly.io](https://fly.io/docs/)
- [Community Forum](https://community.fly.io/)
- [Discord](https://fly.io/discord)

## ✅ Checklist de déploiement

- [ ] Fly CLI installé et connecté
- [ ] MongoDB Atlas configuré
- [ ] Variables d'environnement définies
- [ ] Première application déployée avec `fly deploy`
- [ ] Tests API réussis sur `/health` et `/docs`
- [ ] Domaine personnalisé configuré (optionnel)
- [ ] Monitoring mis en place

Votre backend BF1 devrait maintenant être accessible via `https://votre-app.fly.dev` ! 🎉
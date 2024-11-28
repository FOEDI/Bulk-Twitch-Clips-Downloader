# Bulk Twitch Clips Downloader

Un outil graphique permettant de télécharger en masse des clips Twitch selon différents critères.

![image](https://github.com/user-attachments/assets/a4a07168-7f90-4421-b0de-71b646a8c93c)

## Fonctionnalités

- Interface graphique intuitive
- Téléchargement de tous les clips d'une chaîne créés par un utilisateur spécifique
- Filtrage par période (date de début et fin)
- Barre de progression globale et par clip
- Possibilité d'annuler le téléchargement en cours
- Logs détaillés des opérations
- Gestion des erreurs
- Organisation automatique des clips dans des dossiers dédiés

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/FOEDI/Bulk-Twitch-Clips-Downloader.git
cd Bulk-Twitch-Clips-Downloader
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
   - Windows :
   ```bash
   .\venv\Scripts\activate
   ```
   - Linux/MacOS :
   ```bash
   source venv/bin/activate
   ```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration

1. Créez une application Twitch :
   - Connectez-vous sur [dev.twitch.tv](https://dev.twitch.tv)
   - Allez dans la [Console](https://dev.twitch.tv/console)
   - Cliquez sur "Créer une application"
   - Remplissez les informations requises
   - Notez votre Client ID et générez un Client Secret

2. Créez un fichier `config.json` à la racine du projet :
```json
{
    "client_id": "VOTRE_CLIENT_ID",
    "client_secret": "VOTRE_CLIENT_SECRET"
}
```

## Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. Dans l'interface :
   - Entrez le nom de la chaîne Twitch
   - Entrez le nom du créateur des clips
   - Sélectionnez la période souhaitée
   - Cliquez sur "Démarrer le téléchargement"

Les clips seront téléchargés dans un dossier nommé selon le format :
`bulkdownload_CHANNEL_CREATOR_STARTDATE_ENDDATE`

## Structure du projet

```
twitch-clip-downloader/
│
├── main.py                # Point d'entrée de l'application
├── config_manager.py      # Gestion de la configuration
├── info_dialog.py         # Fenêtre "À propos"
├── twitch_downloader.py   # Logique de téléchargement
├── requirements.txt       # Dépendances du projet
├── config.json           # Configuration (à créer)
└── README.md             # Ce fichier
```

## Dépendances principales

- PyQt6 : Interface graphique
- requests : Communication avec l'API Twitch
- tqdm : Barres de progression

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

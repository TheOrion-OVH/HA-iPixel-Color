# BKLight pour Home Assistant (iPixel) 🌈✨

Cette intégration permet de contrôler vos **dalles LED 32x32 BKLight** (achetées chez **Action**) directement depuis Home Assistant. Elle a été conçue pour offrir une expérience visuelle premium avec des animations fluides et intelligentes.

---

## 🌟 Fonctionnalités Détaillées

### 🎨 Texte, Couleurs & Effets
- **Messages Personnalisés** : Envoyez n'importe quel texte avec choix de la police (CUSONG, TINY, etc.).
- **Mode Arc-en-Ciel** : Un effet spécial qui applique un dégradé multicolore dynamique à votre message (réglable de 0 à 4).
- **Vitesse & Couleurs** : Contrôlez la précision du défilement et la couleur de chaque message.

### 🖼️ Images & GIFs
- **Galerie Personnelle** : Affichez vos propres GIFs ou images via une simple URL.
- **Redimensionnement Intelligent** : L'intégration adapte automatiquement la taille (Crop ou Fit) pour un rendu parfait sur 32x32.

### 🚀 Animations d'Ambiance
- **Générateurs Inclus** : 15 animations cultes (Feu, Matrix, Aurora, Plasma, Pac-Man, Vagues, Neige, Rainbow, Equalizer, Confettis, Feu d'artifice, Snake, Tetris, Dino Google, Pingouin).

### 🎮 Jeux Interactifs
- **Pierre-Feuille-Ciseaux (PFC)** : Défiez votre dalle LED ! Choisissez votre coup dans le sélecteur et appuyez sur "Jouer PFC". La dalle affiche **instantanément** le duel et le gagnant.

### 🖌️ Dessin & Création
- **Dessin Pixel** : Contrôlez chaque pixel individuellement via automatisations pour créer vos propres motifs ou icônes statiques.


### ☀️ Mode Solaire Intelligent (Sun Sync)
Votre dalle devient un véritable indicateur céleste synchronisé avec Home Assistant :
- **Position Dynamique** : Le soleil monte ou descend sur l'écran en fonction de son élévation réelle dans votre ciel.
- **Cycle Jour/Nuit** : Le système bascule automatiquement entre un soleil rayonnant et un croissant de lune poétique sur fond étoilé.
- **Rendu Premium** : Ciel dégradé (Aube, Midi, Crépuscule) et reflets marins sur l'horizon.

### 🌦️ Mode Météo Animé (Weather Pixel-Art)
Un tableau de bord météo magnifique qui s'anime selon les conditions :
- **Animations Météo** : Pluie avec éclaboussures, Neige tourbillonnante, Orages avec flashs, Brouillard dérivant.
- **Données en Temps Réel** : Affiche la température et l'humidité de vos capteurs HA avec un effet de "verre givré" translucide.

### 🛠️ Horloge & Paramètres de Précision
- **Styles d'Heure** : Plusieurs styles d'affichage de l'horloge (0 à 8).
- **Affichage Date** : Un interrupteur dédié permet de choisir d'afficher ou non la date. 📅
- **Orientation** : Faites pivoter l'affichage (0°, 90°, 180°, 270°) instantanément.

### 💾 Persistance & Robustesse
- **Mémoire d'État** : Vos choix d'animations, de polices, d'orientation et de messages sont **sauvegardés automatiquement**. Après un redémarrage de Home Assistant, la dalle retrouve ses derniers réglages. ✅
- **Interface Épurée** : Les sélecteurs (Luminosité, Orientation) appliquent les changements en temps réel, éliminant les boutons de validation inutiles.

---

## ⚙️ Guide d'Installation Détaillé

L'installation se décompose en deux parties : le **Proxy** (pour parler à la dalle) et l'**Intégration** (pour la contrôler).

### 1. Installation du Proxy (Docker)
Le proxy doit être installé sur une machine équipée du Bluetooth (ex: Raspberry Pi, NAS, Serveur Linux) située à proximité de votre dalle.

1. Créez un dossier dédié (ex: `ipixel-proxy`) sur votre serveur.
2. Téléchargez ou copiez le fichier `docker-compose.yml` du dépôt dans ce dossier.
3. Créez un fichier `.env` dans le même dossier et remplissez-le ainsi :
   ```env
   IPIXEL_ADDRESS=XX:XX:XX:XX:XX:XX  # L'adresse MAC Bluetooth de votre dalle
   IPIXEL_PORT=5042                 # Le port de communication (par défaut 5042)
   IPIXEL_HOST=0.0.0.0              # Laissez 0.0.0.0 pour accepter les connexions
   ```
4. Lancez le proxy avec la commande :
   ```bash
   docker-compose up -d
   ```

### 2. Installation de l'Intégration HA
Une fois le proxy lancé, vous devez ajouter l'intelligence dans Home Assistant.

#### via HACS (Recommandé)
1. Ouvrez **HACS** > **Intégrations**.
2. Cliquez sur les 3 points en haut à droite > **Dépôts personnalisés**.
3. Ajoutez l'URL de ce dépôt GitHub et sélectionnez la catégorie **Intégration**.
4. Recherchez et téléchargez **HA iPixel Color**.
5. **Redémarrez Home Assistant.**

#### via Installation Manuelle
1. Copiez le dossier `custom_components/ha_ipixel_color` dans le dossier `config/custom_components/` de votre Home Assistant.
2. **Redémarrez Home Assistant.**

### 3. Configuration de l'Appareil
1. Dans Home Assistant, allez dans **Paramètres** > **Appareils et Services**.
2. Cliquez sur **Ajouter une intégration** en bas à droite.
3. Recherchez **iPixel** (ou **HA iPixel Color**).
4. Suivez l'assistant de configuration :
   - **Nom** : Donnez un nom à votre dalle (ex: "Tableau Salon").
   - **URL WebSocket** : Entrez l'adresse de votre proxy (ex: `ws://192.168.1.50:5042`).
5. Validez ! Votre dalle est maintenant prête.

---

## ⚠️ Compatibilité & Prérequis
- **Matériel** : Uniquement les dalles LED 32x32 vendues chez **Action** (Marque BKLight).
- **Logiciel** : Home Assistant installé et fonctionnel + un serveur Docker pour le proxy.

---
*Transformez votre intérieur avec des pixels intelligents.*

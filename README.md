# BKLight pour Home Assistant 🌈✨

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
- **Générateurs Inclus** : 9 animations cultes prêtes à l'emploi (Feu, Matrix, Aurora, Plasma, Pac-Man, Vagues, Neige, Rainbow, Equalizer).

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
- **Styles d'Heure** : Plusieurs styles d'affichage de l'horloge.
- **Orientation Locale** : Faites pivoter l'affichage (0°, 90°, 180°, 270°) selon la pose de votre dalle.
- **Dessin Pixel** : Contrôlez chaque pixel individuellement pour créer vos propres motifs via automatisations.

---

## 🏗️ Comment ça marche ?

L'installation est simple et se fait en deux étapes :

### 1. Le Proxy (docker-compose)
Le programme qui parle à la dalle doit être sur une machine avec Bluetooth (ex : Raspberry Pi ou NAS).
- Créez un dossier avec le fichier `docker-compose.yml`.
- Configurez votre adresse Bluetooth dans le fichier `.env`.
- Lancez avec `docker-compose up -d`.

### 2. L'Intégration (Home Assistant)
- Installez l'intégration via HACS ou manuellement.
- Allez dans **Paramètres > Appareils > BKLight**.
- Saisissez simplement l'adresse de votre proxy.

---

## ⚠️ Compatibilité
Cette intégration est optimisée **uniquement pour les dalles 32x32 vendues chez Action** (Marque BKLight).

---
*Transformez votre intérieur avec des pixels intelligents.*

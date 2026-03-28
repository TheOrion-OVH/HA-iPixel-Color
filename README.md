# HA iPixel Color

Une intégration native et complète pour Home Assistant permettant de contrôler les panneaux LED iPixel (via le proxy WebSocket) avec une synchronisation parfaite de l'état.

![HA iPixel Color](https://img.shields.io/badge/Home_Assistant-Integration-blue.svg) ![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)

## 🌟 Fonctionnalités

- **Alimentation** : Switch optimiste On / Off
- **Luminosité** : Curseur dynamique (0-100%)
- **Texte Custom** : Message, couleurs hex, police, animations (défilement, clignotement), vitesse, mode Arc-en-ciel.
- **Images Distantes** : Envoi de GIFs ou PNG via URL locale ou publique. Redimensionnement (Crop / Fit).
- **Générateurs d'animations Python embarqués** :
  - 🔥 Feu, 💻 Matrix, ❄️ Neige, 🌌 Aurora, 🌊 Vagues, 🌈 Rainbow, 🌀 Plasma, 👾 Pac-Man, 🎶 Equalizer.
- **Paramètres avancés** : Styles d'horloge, Gestion de l'orientation (0, 90, 180, 270°), Dessin pixel par pixel.
- **Configuration UI pure** : Plus besoin de bidouiller du YAML, tout se fait visuellement (Config Flow).

---

## 📦 Installation via HACS (Recommandé)

1. Ouvrez **HACS** dans votre interface Home Assistant.
2. Cliquez sur l'onglet **Intégrations**.
3. Cliquez sur les 3 petits points verticaux en haut à droite > **Dépôts personnalisés**.
4. Collez l'URL de **ce dépôt GitHub**.
5. Sélectionnez la catégorie : **Intégration** et cliquez sur Ajouter.
6. HACS va vous proposer de télécharger `HA iPixel Color`. Installez-le.
7. **Redémarrez complètement Home Assistant.**

---

## ⚙️ Configuration

1. Dans Home Assistant, naviguez vers **Paramètres > Appareils et Services**.
2. Cliquez sur le bouton **+ Ajouter une intégration** en bas à droite.
3. Recherchez `HA iPixel Color`.
4. La fenêtre de configuration (Setup Wizard) apparaît :
   - **Adresse MAC (Bluetooth)** : Saisissez l'adresse MAC de votre panneau (ex: `11:22:33:44:55:66`). Ceci sert d'ID unique pour Home Assistant.
   - **URI du Proxy WebSocket** : Saisissez l'adresse du conteneur Docker `pypixelcolor.websocket` (ex: `localhost:5042` ou l'IP de votre NAS/Pi).
5. Validez, et Home Assistant générera automatiquement un Appareil contenant des dizaines d'entités de contrôles (sliders, boutons, inputs texte) parfaitement organisées.

---

## 📡 Services natifs exposés

Cette intégration expose également tous les contrôles directement dans Node-RED ou les automatisations HA via des appels de services natifs :
- `ha_ipixel_color.send_image` (path, resize_method)
- `ha_ipixel_color.send_text` (message, color, bg_color, font, speed, rainbow_mode)
- `ha_ipixel_color.set_power` (on_state)
- `ha_ipixel_color.set_brightness` (level)
- `ha_ipixel_color.set_clock_mode` (style)
- `ha_ipixel_color.set_orientation` (orientation)
- `ha_ipixel_color.set_pixel` (x, y, color)
- `ha_ipixel_color.clear`

---

## ⚠️ Prérequis

L'intégration a besoin d'un serveur WebSocket `pypixelcolor` pour fonctionner. 
Vous devez avoir un conteneur Docker ou un script tournant avec la commande :
```bash
python3 -m pypixelcolor.websocket -a VOTRE_MAC_BLUETOOTH -p 5042
```

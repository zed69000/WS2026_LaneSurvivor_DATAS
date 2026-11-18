# WS2026_LaneSurvivor_DATAS · les sources des assets

Ce dossier contient les **fichiers de travail** (Blender, Photoshop…) du projet Unity
`WS2026_LaneSurvivor`. Il est rangé **exactement comme** le dossier `Assets` d’Unity :

```
WS2026_LaneSurvivor_DATAS/                  WS2026_LaneSurvivor/Assets/
  Art/3D/Characters/SM_Player.blend  ->   Art/3D/Characters/SM_Player.fbx
  Art/3D/Environment/Decor/...       ->   Art/3D/Environment/Decor/...
  Art/3D/Environment/Route/...       ->   Art/3D/Environment/Route/...
  Art/2D/Textures/  (fichiers .psd)  ->   Art/2D/Textures/  (fichiers .png)
  Art/2D/UI/                         ->   Art/2D/UI/
  Art/Animation/                     ->   Art/Animation/
  Tools/                                 (outils : l'add-on Blender)
```

Le projet Unity et ce dossier doivent être **l’un à côté de l’autre** :
`.../WS2026_LaneSurvivor` et `.../WS2026_LaneSurvivor_DATAS`.

## Nomenclature

| Préfixe | Ce que c’est | Exemple |
|---|---|---|
| `SM_` | Static Mesh : un modèle 3D | `SM_Arbre.blend` / `SM_Arbre.fbx` |
| `SK_` | Skinned Mesh : un modèle avec squelette (animé) | `SK_Player.fbx` |
| `ANIM_` | Une animation | `ANIM_Player_Course.fbx` |
| `MAT_` | Un matériau (même nom dans Blender et Unity !) | `MAT_Prairie_Feuillage` |
| `T_` | Une texture | `T_Arbre_Couleur.png` |
| `PF_` | Un prefab (dans Unity) | `PF_Arbre` |
| `SH_` | Un shader (dans Unity) | `SH_CustomStyle` |

Règles :
- Un fichier = un asset, et **le même nom** de la source jusqu’au prefab (`SM_Arbre` → `PF_Arbre`).
- Pas d’espace, pas d’accent dans les noms de fichiers.
- Les matériaux s’appellent **pareil** dans Blender et dans Unity : à l’import, Unity
  rebranche tout seul nos matériaux (`MAT_...` dans `Assets/Materials`).

## Blender → Unity, en un Ctrl+S

1. Installer une fois l’add-on : Blender › Edit › Preferences › Add-ons ›
   flèche en haut à droite › **Install from Disk…** › `Tools/LaneSurvivor_ExportUnity.py` › cocher.
2. Ouvrir un `.blend` de ce dossier, le modifier, **Ctrl+S**.
3. Le FBX est réécrit automatiquement au même endroit dans `WS2026_LaneSurvivor/Assets`.
4. Revenir dans Unity : le modèle est mis à jour **partout** (tous les prefabs qui l’utilisent).

Bouton manuel : vue 3D › touche **N** › onglet **Lane Survivor** › *Exporter vers Unity*.

## Règles de modélisation

- **1 mètre dans Blender = 1 mètre dans Unity.**
- **Origine aux pieds** de l’objet (posé sur le sol, Z = 0).
- **L’avant** d’un personnage regarde vers **-Y** dans Blender (vue de face, touche 1 du pavé).
  Les ennemis, eux, regardent vers +Y (ils viennent vers le joueur).
- **Low poly** : quelques dizaines à quelques centaines de faces. Shading **Flat**.
- Les couleurs viennent des matériaux Unity (`SH_CustomStyle`) : pas besoin de texture.

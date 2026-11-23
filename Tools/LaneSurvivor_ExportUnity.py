# ==================================================================
#  LANE SURVIVOR : EXPORT VERS UNITY (add-on Blender)
# ==================================================================
#  Installation (une seule fois) :
#    Blender > Edit > Preferences > Add-ons > flèche en haut à droite
#    > Install from Disk... > choisir ce fichier > cocher l'add-on.
#
#  Utilisation :
#    Chaque fois qu'on SAUVEGARDE (Ctrl+S) un .blend rangé dans
#    WS_LaneSurvivor_DATAS, le FBX est exporté AUTOMATIQUEMENT
#    au même endroit dans le projet Unity :
#
#      WS_LaneSurvivor_DATAS/Art/3D/Decor/SM_Arbre.blend
#   -> WS_LaneSurvivor/Assets/Art/3D/Decor/SM_Arbre.fbx
#
#    On revient dans Unity : le modèle est mis à jour partout.
#    (Bouton manuel aussi : vue 3D > touche N > onglet "Lane Survivor")
#
#  Règles pour que ça marche bien :
#    - 1 mètre dans Blender = 1 mètre dans Unity
#    - le point d'origine de l'objet = ses pieds (posé au sol)
#    - "avant" du personnage = vers -Y dans Blender (vue de face)
#    - les matériaux s'appellent comme dans Unity (MAT_...)
#
#  Textures : chaque image utilisée par un matériau est écrite en PNG
#  dans un dossier Textures, à côté du FBX, sous le nom
#  T_<Matériau sans MAT_>_<Rôle>.png  (BaseColor, Normal, Roughness...).
#  Unity la branche tout seul sur le bon matériau (BaseColor et Normal).
# ==================================================================
bl_info = {
    "name": "Lane Survivor : export vers Unity",
    "author": "Workshop Unity 2026",
    "version": (1, 1),
    "blender": (4, 2, 0),
    "location": "Vue 3D > N > Lane Survivor",
    "description": "Exporte le .blend en FBX dans le projet Unity, à chaque sauvegarde",
    "category": "Import-Export",
}

import os
import bpy
from bpy.app.handlers import persistent

SUFFIXE_DATAS = "_DATAS"


def chemin_unity(chemin_blend):
    """WS_X_DATAS/Art/.../SM_Truc.blend  ->  WS_X/Assets/Art/.../SM_Truc.fbx"""
    chemin = os.path.normpath(chemin_blend)
    morceaux = chemin.split(os.sep)
    for i, dossier in enumerate(morceaux):
        # "WS_X_DATAS" -> "WS_X", et aussi "WS_X_DATAS-main" -> "WS_X-main" (téléchargement ZIP)
        if SUFFIXE_DATAS in dossier:
            projet = dossier.replace(SUFFIXE_DATAS, "")
            racine = os.sep.join(morceaux[:i] + [projet, "Assets"])
            relatif = os.sep.join(morceaux[i + 1:])
            return os.path.join(racine, os.path.splitext(relatif)[0] + ".fbx")
    return None


def role_texture(noeud):
    """À quoi sert l'image : BaseColor, Normal, Roughness... (d'après ce qu'elle alimente)"""
    for sortie in noeud.outputs:
        for lien in sortie.links:
            cible, prise = lien.to_node, lien.to_socket.name
            if cible.type == 'NORMAL_MAP' or prise == 'Normal':
                return "Normal"
            if prise in ('Base Color', 'Color') and cible.type in ('BSDF_PRINCIPLED', 'EMISSION', 'BSDF_DIFFUSE', 'MIX_SHADER'):
                return "BaseColor"
            if prise in ('Roughness', 'Metallic', 'Alpha'):
                return prise
            if prise == 'Emission Color':
                return "Emission"
    return None


def exporter_textures(dossier_fbx):
    """Écrit en PNG les images des matériaux, dans <dossier du FBX>/Textures."""
    dossier = os.path.join(dossier_fbx, "Textures")
    ecrites = []
    materiaux = {s.material for o in bpy.data.objects if o.type == 'MESH'
                 for s in o.material_slots if s.material}
    for mat in materiaux:
        if not mat.node_tree:
            continue
        base = mat.name[4:] if mat.name.startswith("MAT_") else mat.name
        for noeud in mat.node_tree.nodes:
            if noeud.type != 'TEX_IMAGE' or not noeud.image or noeud.image.source not in ('FILE', 'TILED'):
                continue
            image = noeud.image
            role = role_texture(noeud) or bpy.path.clean_name(os.path.splitext(image.name)[0])
            nom = "T_%s_%s.png" % (base, role)
            try:
                _ = image.pixels[0]          # charge l'image si besoin
                if not image.has_data:
                    raise RuntimeError("image introuvable : " + image.filepath)
                os.makedirs(dossier, exist_ok=True)
                format_avant = image.file_format
                image.file_format = 'PNG'
                image.save(filepath=os.path.join(dossier, nom))
                image.file_format = format_avant
                ecrites.append(nom)
            except Exception as erreur:
                print("[Lane Survivor] Texture non exportée :", image.name, "-", erreur)
    return ecrites


def exporter_fbx(chemin_fbx):
    os.makedirs(os.path.dirname(chemin_fbx), exist_ok=True)
    textures = exporter_textures(os.path.dirname(chemin_fbx))
    if textures:
        print("[Lane Survivor] Textures :", ", ".join(textures))
    bpy.ops.export_scene.fbx(
        filepath=chemin_fbx,
        use_selection=False,
        object_types={'MESH'},
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_space_transform=True,
        mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,
    )


@persistent
def export_a_la_sauvegarde(_dummy=None):
    scene = bpy.context.scene
    if not getattr(scene, "ls_export_auto", True):
        return
    cible = chemin_unity(bpy.data.filepath)
    if cible:
        exporter_fbx(cible)
        print("[Lane Survivor] Exporté vers Unity :", cible)


class LS_OT_exporter(bpy.types.Operator):
    bl_idname = "lane_survivor.exporter_unity"
    bl_label = "Exporter vers Unity"
    bl_description = "Exporte ce fichier en FBX dans le projet Unity"

    def execute(self, context):
        cible = chemin_unity(bpy.data.filepath)
        if not cible:
            self.report({'ERROR'}, "Le .blend doit être sauvegardé dans un dossier ..._DATAS")
            return {'CANCELLED'}
        exporter_fbx(cible)
        self.report({'INFO'}, "Exporté : " + cible)
        return {'FINISHED'}


class LS_PT_panneau(bpy.types.Panel):
    bl_label = "Lane Survivor"
    bl_idname = "LS_PT_panneau"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lane Survivor"

    def draw(self, context):
        col = self.layout.column()
        col.prop(context.scene, "ls_export_auto", text="Export auto à la sauvegarde")
        col.operator("lane_survivor.exporter_unity", icon='EXPORT')
        cible = chemin_unity(bpy.data.filepath) if bpy.data.filepath else None
        col.label(text=os.path.basename(cible) if cible else "Sauvegarder dans ..._DATAS")


def register():
    bpy.types.Scene.ls_export_auto = bpy.props.BoolProperty(default=True)
    bpy.utils.register_class(LS_OT_exporter)
    bpy.utils.register_class(LS_PT_panneau)
    if export_a_la_sauvegarde not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(export_a_la_sauvegarde)


def unregister():
    if export_a_la_sauvegarde in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(export_a_la_sauvegarde)
    bpy.utils.unregister_class(LS_PT_panneau)
    bpy.utils.unregister_class(LS_OT_exporter)
    del bpy.types.Scene.ls_export_auto


if __name__ == "__main__":
    register()

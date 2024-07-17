import os
import bpy
import bpy.utils.previews
from bpy.types import Panel, Operator

bl_info = {
    "name": "Kwobbler",
    "blender": (4, 1, 1),
    "category": "3D View",
    "location": "3D View > Kwobbler",
    "version": (1, 0, 0),
    "author": "Kent Edoloverio",
    "description": "Adds PS1 effect into your meshes",
    "wiki_url": "",
    "tracker_url": "",
}

class KWobbler(Operator):
    bl_idname = "geonode.append_ps1_nodes"
    bl_label = "SETUP PS1"

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(__file__), "..", "Kwobbler/data", "Kwobbler.blend")
    
    def import_file(self):
        # Check if the file exists
        if not os.path.isfile(self.source_file):
            self.report({'ERROR'}, "File not found: {}".format(self.source_file))
            return {'CANCELLED'}
        return {'FINISHED'}

    def import_node_group(self, node_group_name):
        # Load the custom node group from the blend file
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]

        # Check if the node group was successfully loaded
        if not data_to.node_groups or not data_to.node_groups[0]:
            self.report({'ERROR'}, "Failed to load the node group: {}".format(node_group_name))
            return {'CANCELLED'}

        self.report({'INFO'}, "Successfully appended node group: {}".format(node_group_name))
        return {'FINISHED'}

    def create_plane_with_node_group(self, node_group_name):
        collection = bpy.data.collections.new("Kwobbler")
        bpy.context.scene.collection.children.link(collection)

        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = bpy.context.object
        collection.objects.link(plane)
        bpy.context.scene.collection.objects.unlink(plane)

        geom_nodes_modifier = plane.modifiers.new(name="GeometryNodes", type='NODES')

        if node_group_name in bpy.data.node_groups:
            geom_nodes_modifier.node_group = bpy.data.node_groups[node_group_name]
        else:
            self.report({'ERROR'}, "Node group not found: {}".format(node_group_name))
            return {'CANCELLED'}

        self.report({'INFO'}, "Plane created and node group assigned.")
        return {'FINISHED'}

    def execute(self, context):
        if self.import_file() == {'CANCELLED'}:
            return {'CANCELLED'}

        if self.import_node_group("Kwobbler") == {'CANCELLED'}:
            self.report({'WARNING'}, "Make sure you select the Scene Collection")
            return {'CANCELLED'}

        if self.create_plane_with_node_group("Kwobbler") == {'CANCELLED'}:
            return {'CANCELLED'}
        
        return {'FINISHED'}

class KWobblerPanel(Panel):
    bl_idname = "VIEW3D_PT_kwobbler"
    bl_label = "Kwobbler"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Kwobbler'

    def draw(self, context):
        pcoll = icon_preview["main"]
        kofi = pcoll["kofi"]
        deviant = pcoll["deviant"]
        github = pcoll["github"]

        layout = self.layout

        col = layout.row(align=False)
        col.enabled = True
        col.scale_x = 2.0
        col.scale_y = 2.0
        col.operator("geonode.append_ps1_nodes")

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        kofi = box.operator(
            'wm.url_open',
            text='KO-FI',
            icon_value=kofi.icon_id,
            emboss=False
        )
        kofi.url = 'https://ko-fi.com/kents_workof_art'

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        deviant = box.operator(
            'wm.url_open',
            text='DEVIANT ART',
            icon_value=deviant.icon_id,
            emboss=False
        )
        deviant.url = 'https://www.deviantart.com/kents001'

        box = layout.box()
        box.scale_y = 1.5
        box.scale_x = 1.5
        github = box.operator(
            'wm.url_open',
            text='GITHUB',
            icon_value=github.icon_id,
            emboss=False
        )
        github.url = 'https://github.com/kents00'

icon_preview = {}

classes = (
    KWobbler,
    KWobblerPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    pcoll = bpy.utils.previews.new()

    absolute_path = os.path.join(os.path.dirname(__file__), 'data/')
    relative_path = "icons"
    path = os.path.join(absolute_path, relative_path)
    pcoll.load("kofi", os.path.join(path, "kofi.png"), 'IMAGE')
    pcoll.load("deviant", os.path.join(path, "deviantart.png"), 'IMAGE')
    pcoll.load("github", os.path.join(path, "github.png"), 'IMAGE')
    icon_preview["main"] = pcoll

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
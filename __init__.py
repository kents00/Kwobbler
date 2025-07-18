import os
import bpy
import bpy.utils.previews
from bpy.types import Panel, Operator

bl_info = {
    "name": "Kwobbler",
    "blender": (4, 5, 0),
    "category": "3D View",
    "location": "3D View > Kwobbler",
    "version": (2, 0, 0),
    "author": "Kent Edoloverio",
    "description": "Adds PS1 effect into your meshes",
    "warning" : "Make sure no objects are selected in your collection, click on the Scene Collection in the outliner, and click the Setup PS1 button in the Kwobbler panel.",
    "wiki_url": "https://kentedoloverio.gumroad.com/l/kwobbler",
    "tracker_url": "https://github.com/kents00/Kwobbler/issues",
}

class KWobbler(Operator):
    bl_idname = "geonode.append_ps1_nodes"
    bl_label = "SETUP PS1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.selected_objects:
            self.report({'WARNING'}, "Please deselect all objects in the Scene Collection before running this operator.")
            return {'CANCELLED'}

        self.source_file = os.path.join(os.path.dirname(__file__), "..", "Kwobbler/data", "Kwobbler.blend")

        if self.import_file() == {'CANCELLED'}:
            return {'CANCELLED'}

        if self.import_node_group("Kwobbler") == {'CANCELLED'}:
            self.report({'WARNING'}, "Make sure you select the Scene Collection")
            return {'CANCELLED'}

        if self.create_plane_with_node_group("Kwobbler") == {'CANCELLED'}:
            return {'CANCELLED'}

        return {'FINISHED'}

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
        collection, plane = self.get_or_create_collection_and_plane("Kwobbler")
        if not collection or not plane:
            return {'CANCELLED'}

        geom_nodes_modifier = self.get_or_create_geometry_nodes_modifier(plane)
        if not geom_nodes_modifier:
            self.report({'ERROR'}, "Failed to create GeometryNodes modifier.")
            return {'CANCELLED'}

        if not self.assign_node_group_to_modifier(geom_nodes_modifier, node_group_name):
            return {'CANCELLED'}

        self.report({'INFO'}, "Node group assigned.")
        return {'FINISHED'}

    def get_or_create_collection_and_plane(self, collection_name):
        if collection_name in bpy.data.collections:
            self.report({'WARNING'}, f"{collection_name} collection already exists. Not creating another collection.")
            collection = bpy.data.collections[collection_name]
            if collection.objects:
                plane = collection.objects[0]
                self.report({'INFO'}, f"Using existing object: {plane.name}")
            else:
                plane = self.create_plane()
                if plane:
                    self.link_plane_to_collection(plane, collection)
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
            self.report({'INFO'}, f"Created {collection_name} collection.")
            plane = self.create_plane()
            if plane:
                self.link_plane_to_collection(plane, collection)
        return collection, plane if 'plane' in locals() else (None, None)

    def create_plane(self):
        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = bpy.context.object
        return plane

    def link_plane_to_collection(self, plane, collection):
        if plane.name not in collection.objects:
            collection.objects.link(plane)
        if plane.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(plane)

    def get_or_create_geometry_nodes_modifier(self, plane):
        for modifier in plane.modifiers:
            if modifier.type == 'NODES':
                self.report({'INFO'}, "Using existing GeometryNodes modifier.")
                return modifier
        return plane.modifiers.new(name="GeometryNodes", type='NODES')

    def assign_node_group_to_modifier(self, modifier, node_group_name):
        if node_group_name in bpy.data.node_groups:
            modifier.node_group = bpy.data.node_groups[node_group_name]
            return True
        else:
            self.report({'ERROR'}, f"Node group not found: {node_group_name}")
            return False

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

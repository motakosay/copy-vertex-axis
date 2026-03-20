bl_info = {
    "name": "Copy Vertex Axis (Global)",
    "author": "Yahia Kamal",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Edit Mode > Vertex Menu",
    "description": "Copy global axis from first selected vertex to second selected",
    "category": "Mesh",
}

import bpy
import bmesh

class MESH_OT_copy_vertex_axis(bpy.types.Operator):
    """Copy coordinate axis (global) from first selected vertex to all others"""
    bl_idname = "mesh.copy_vertex_axis"
    bl_label = "Copy Vertex Axis (Global)"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Which axis to copy (global)",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")]
    )

    def execute(self, context):
        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        # Selection order matters
        sel_history = [e for e in bm.select_history if isinstance(e, bmesh.types.BMVert)]
        if len(sel_history) < 2:
            self.report({'ERROR'}, "Select at least 2 vertices in order (first = source, others = targets)")
            return {'CANCELLED'}

        source_vert = sel_history[0]

        mat = obj.matrix_world
        inv = mat.inverted()

        # Global coords of source
        source_global = mat @ source_vert.co
        source_value = getattr(source_global, self.axis.lower())

        # Apply to all other selected verts
        for target_vert in sel_history[1:]:
            target_global = mat @ target_vert.co
            setattr(target_global, self.axis.lower(), source_value)
            target_vert.co = inv @ target_global

        bmesh.update_edit_mesh(me)
        return {'FINISHED'}


# Add to menus
def menu_func(self, context):
    self.layout.operator(MESH_OT_copy_vertex_axis.bl_idname, text="Copy Vertex Axis (Global)")


# Register / Unregister
classes = (MESH_OT_copy_vertex_axis,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

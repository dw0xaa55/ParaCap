# TODO:
# - [ ]  name the empty in n-menu (?)
# - [ ]  put parallax calculation in own function

# Copyright (C) 2025 C. Huffenbach

bl_info = {
    "name": "ParaCap",
    "blender": (4, 2, 3),
    "category": "3D View",
}

import bpy
import numpy as np

class ParallaxCalculatorPanel(bpy.types.Panel):
    """Creates a Panel in the N-side menu"""
    bl_label       = "ParaCap"
    bl_idname      = "OBJECT_PT_paracap"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "ParaCap"
    bl_description = "ParaCap takes tracks from two video clips taken at adjacent positions to calculate the parallactic movement and create an empty with the resulting 3-dimensional movement."

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Input fields for the two empty objects
        layout.prop(scene, "empty_a")
        layout.prop(scene, "empty_b")
        layout.prop(scene, "distance")
        layout.prop(scene, "keyframe_count")
        layout.prop(scene, "act_width")

        # Button to calculate parallax
        layout.operator("object.calculate_parallax")

class CalculateParallaxOperator(bpy.types.Operator):
    """Calculate Parallax"""
    bl_idname  = "object.calculate_parallax"
    bl_label   = "Calculate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        empty_a        = context.scene.empty_a
        empty_b        = context.scene.empty_b
        distance       = context.scene.distance
        keyframe_count = context.scene.keyframe_count
        act_width      = context.scene.act_width
        fov            = bpy.context.scene.camera.data.angle / np.pi * 180

        new_empty      = bpy.data.objects.new("Parallax_Empty", None)
        context.collection.objects.link(new_empty)
        
        for i in range(keyframe_count):    # iterate through the keyframes
            bpy.context.scene.frame_set(i) # change to frame i
            P1  = empty_a.location         # save locations of empties for currently active keyframe
            P2  = empty_b.location
            
            # calculate parallax distance
            d   = P1 - P2
            d   = np.sqrt(d[0]**2+d[1]**2+d[2]**2)
            d   *= fov / act_width            

            # put empty at calculated points and create a keyframe
            new_empty.location.x = P2.x + (P1.x - P2.x)
            new_empty.location.y = -d
            new_empty.location.z = P2.z
            new_empty.keyframe_insert(data_path="location", frame=i)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ParallaxCalculatorPanel)
    bpy.utils.register_class(CalculateParallaxOperator)
    bpy.types.Scene.empty_a        = bpy.props.PointerProperty(type=bpy.types.Object, name="Track Right")
    bpy.types.Scene.empty_b        = bpy.props.PointerProperty(type=bpy.types.Object, name="Track Left")
    bpy.types.Scene.distance       = bpy.props.FloatProperty(name="Distance between Cameras", default=1.0, min=0.0)
    bpy.types.Scene.keyframe_count = bpy.props.IntProperty(name="Keyframe Count", default=10, min=1)
    bpy.types.Scene.act_width      = bpy.props.FloatProperty(name="Width of Acting Area", default=5.0, min=1.0)

def unregister():
    bpy.utils.unregister_class(ParallaxCalculatorPanel)
    bpy.utils.unregister_class(CalculateParallaxOperator)
    del bpy.types.Scene.empty_a
    del bpy.types.Scene.empty_b
    del bpy.types.Scene.distance
    del bpy.types.Scene.keyframe_count
    del bpy.types.Scene.act_width

if __name__ == "__main__":
    register

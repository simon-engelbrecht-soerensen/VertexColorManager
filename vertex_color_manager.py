bl_info = {
    "name": "Vertex Color Manager",
    "author": "Simon Engelbrecth Sørensen",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > Vertex Color Manager",
    "description": "VC Manager",
    "category": "Development",
}

import bpy

import random

from bpy.props import BoolProperty

RGB = [random.uniform(0,1) for i in range(4)]



class Properties(bpy.types.PropertyGroup):
    
    enumOrigin : bpy.props.EnumProperty(
    name = "Origin",
    description = "Where to offset from",
    items= [
        ('OP1', "Object Origin", ""),
        ('OP2', "3D Cursor", ""),
        ],        
    )
    
    boolSelectedOnly : bpy.props.BoolProperty(
    name = "Selected",
    description = "Only set color for selection",
    default = False
    )
    

   
class VCM_OT_pivot_bake(bpy.types.Operator):
    """Baking the pivot"""
    bl_idname = "vertcolormanager.bake_pivot"
    bl_label = "Bake Pivot To Vertex Colors"
    
    def execute(self, context):
        mode = bpy.context.active_object.mode
        obj = bpy.context.active_object
        
        # we need to switch from Edit mode to Object mode so the selection gets updated
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = bpy.context.active_object.data
        selectedVerts = [v for v in mesh.vertices if v.select]
        
        posToColor = (obj.location.x, obj.location.y, obj.location.z, 0)
        
        VCMTool = context.scene.VCMTool
        
        origin = (0,0,0)
        
        if VCMTool.enumOrigin == 'OP1':            
            origin = obj.matrix_world.translation
        if VCMTool.enumOrigin == 'OP2':    
            origin = bpy.context.scene.cursor.location
            
        largestDistance = 0
        for polygon in mesh.polygons:           
            for i, index in enumerate(polygon.vertices):
                v = mesh.vertices[index]
                vPos = obj.matrix_world @ v.co
                distance = (origin - vPos).length
                if largestDistance < distance:
                    largestDistance = distance

               
        #if should only apply to selected
        if VCMTool.boolSelectedOnly == True:   
            for polygon in mesh.polygons:
                for v in selectedVerts:
                    for i, index in enumerate(polygon.vertices):
                        if v.index == index:            
                            loop_index = polygon.loop_indices[i]

                            v = mesh.vertices[index]                        
                            vPos = obj.matrix_world @ v.co
                            
                            distance = (origin - vPos).length
                            normalDist = distance / largestDistance
                            vertOffset = origin + vPos
                           
                            vertOffsetNorm = vertOffset.normalized()
                            mesh.vertex_colors.active.data[loop_index].color = (vertOffset.x, vertOffset.y, vertOffset.z, normalDist)#(vertOffset.x, vertOffset.y, vertOffset.z, 0)

        else:
            for polygon in mesh.polygons:
                for i, index in enumerate(polygon.vertices):
                    loop_index = polygon.loop_indices[i]

                    v = mesh.vertices[index]
                    vPos = obj.matrix_world @ v.co
                    
                    distance = (origin - vPos).length
                    normalDist = distance / largestDistance
                    vertOffset = origin + vPos
                   
                    vertOffsetNorm = vertOffset.normalized()
                    mesh.vertex_colors.active.data[loop_index].color = (vertOffset.x, vertOffset.y, vertOffset.z, normalDist)#(vertOffset.x, vertOffset.y, vertOffset.z, 0)


        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)
        #print(selectedVerts[0])
        
        mesh = bpy.context.active_object.data
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')

        
        
        #bpy.ops.paint.vertex_paint_toggle()
        return {'FINISHED'}


class VCM_OT_clear_to_black(bpy.types.Operator):
    """Clear to black"""
    bl_idname = "vertcolormanager.clear_to_black"
    bl_label = "Clear"
    
    def execute(self, context):
        mode = bpy.context.active_object.mode
        obj = bpy.context.active_object
        
        # we need to switch from Edit mode to Object mode so the selection gets updated
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = bpy.context.active_object.data
        selectedVerts = [v for v in mesh.vertices if v.select]
        
        for polygon in mesh.polygons:
            for i, index in enumerate(polygon.vertices):
                loop_index = polygon.loop_indices[i]
                
                mesh.vertex_colors.active.data[loop_index].color = (0, 0, 0, 0)


        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)
        
        mesh = bpy.context.active_object.data
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')        

        return {'FINISHED'}

class VIEW3D_PT_vertex_color_manager(bpy.types.Panel):
    pass
    
    bl_space_type = "VIEW_3D" #3d viewport area
    bl_region_type = "UI" #sidebar
    
    bl_label = "Vertex Color Manager"
    bl_category = "VC Manager"    
    
    
    def draw(self, context):
        """define panel"""
        scene = context.scene
        VCMTool = scene.VCMTool
        layout = self.layout
        
        row = self.layout.row()
        row.operator("vertcolormanager.bake_pivot", text = "Bake Pivot in RGB and distance in A")
        layout.prop(VCMTool, "enumOrigin")
        layout.prop(VCMTool, "boolSelectedOnly")
        row.operator("vertcolormanager.clear_to_black", text = "Clear")
        #things inside panel
        
        
classes = [Properties, VIEW3D_PT_vertex_color_manager, VCM_OT_pivot_bake, VCM_OT_clear_to_black]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
        bpy.types.Scene.VCMTool = bpy.props.PointerProperty(type = Properties)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.VCMTool
   
if __name__ == "__main__":
    register()
    
    
 


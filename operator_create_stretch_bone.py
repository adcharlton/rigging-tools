import bpy
from mathutils import Vector
from bpy.props import IntProperty

def print_current_bones(armature):
    bpy.context.scene.update()
    
    print("Current edit bones")
    for b in armature.data.bones:
        print(b.name)

    print("Current pose bones")
    for b in armature.pose.bones:
        print(b.name)

def subdivide_bone(armature, bone, divisions):
    div = 1/(divisions+1)
    
    new_bones = []
    
    for i in range(0,divisions+1):
        new_bone = armature.data.edit_bones.new(bone.name + "__" + str(i))
        new_bone.head.xyz = bone.head.xyz + ((bone.tail.xyz - bone.head.xyz) * div * i)
        new_bone.tail.xyz = bone.head.xyz + ((bone.tail.xyz - bone.head.xyz) * div * (i+1))
        
        new_bones.append(new_bone)
        
    return new_bones
    

def make_stretchy_bone(bone, divisions):
    armature = bpy.context.selected_objects[0]
    name = bone.name
    
    new_bones = subdivide_bone(armature, bone, divisions)
    target_bone = None
    
    print_current_bones(armature)
    
    for i, child_bone in enumerate(new_bones):
        child_bone.use_connect = False
        if target_bone:
            child_bone.parent = target_bone
        
        armature.update_from_editmode()
    
        target_bone = armature.data.edit_bones.new(child_bone.name + '_target')
        target_bone.head.xyz = child_bone.tail.xyz
        target_bone.tail.xyz = child_bone.tail.xyz + Vector((0, 0.1, 0))
        target_bone.parent = bone
        
        pose_bone = armature.pose.bones[child_bone.name]
        stretch_constraint = pose_bone.constraints.new(type="STRETCH_TO")
        stretch_constraint.target = armature
        stretch_constraint.subtarget = target_bone.name

    pose_bone = armature.pose.bones[bone.name]
    stretch_constraint = pose_bone.constraints.new(type="STRETCH_TO")
    stretch_constraint.target = armature
    stretch_constraint.subtarget = target_bone.name
    target_bone.parent = None

class MakeStretchyBoneOperator(bpy.types.Operator):
    """Converts a bone to a stretchy bone"""
    bl_idname = "bone.make_stretchy_bone"
    bl_label = "Make stretchy bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    divisions = bpy.props.IntProperty(name='Divisions', default=1)

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE' and \
               context.object.mode == 'EDIT' and \
               context.selected_editable_bones != None
    
    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        print(context.selected_editable_bones)
        make_stretchy_bone(context.selected_editable_bones[0], self.divisions)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MakeStretchyBoneOperator)


def unregister():
    bpy.utils.unregister_class(MakeStretchyBoneOperator)


if __name__ == "__main__":
    register()
import bpy
import numpy as np


# Creating a panel for options
class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel" # adding a label for the panel
    bl_idname = "PT_TestPanel" # add a Panel Type ID name
    
    # Telling where this panel will be located on our screen
    bl_space_type = "VIEW_3D" # defines the window layout 
    bl_region_type = "UI"
    bl_category = "New Tab" # creating a new tab
    
    def draw(self, context):
        layout = self.layout # can change the layout here
        
        # anytime we want a space we add this line
        row = layout.row() 
        
        # shows text and an icon
        row.label(text = "Added a cube", icon = "CUBE") 
        row = layout.row()
        
        # Adds operation to add a new cube object as a button under the tab
        # Can find different objects to add by adding new objects in the window and see the line generated in the INFO window
        row.operator("mesh.primitive_cube_add")
        
        row = layout.row() 
        
        # adding text option
        row.operator("object.text_add")


# to get views to show up, you need to register and unregister class type
def register():
    bpy.utils.register_class(TestPanel)

def unregister():
    bpy.utils.unregister_class(TestPanel)


#######################################################################
# Code below taken from example 
# GitHub: https://gist.github.com/CGArtPython/7fb9f9ad079408ebe1f81b18f1928f72
#######################################################################
        
# adding everything for the camera
def set_end_frame(frame_count):
    bpy.context.scene.frame_end = frame_count
    
# setting the frames per second
def set_fps(fps):
    bpy.context.scene.render.fps = fps

# Creates an empty object that the camera should be tracking
def create_object_empty(x, y, z, sx, sy, sz):
    bpy.ops.object.empty_add()
    empty = bpy.context.active_object
    
    # setting the starting location
    empty.location.x = x
    empty.location.y = y
    empty.location.z = z
    
    # setting the size
    empty.scale.x = sx
    empty.scale.y = sy
    empty.scale.z = sz
    return empty


def add_path(radius, x, y, z, rx, ry, rz):
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius)
    path = bpy.context.active_object
    
    path.location.x = x
    path.location.y = y
    path.location.z = z
    
    path.rotation_euler.x = rx
    path.rotation_euler.y = ry
    path.rotation_euler.z = rz
    return path

# tells how the empty object should move throughout the environment
# What we would change for the PyQt
def animate_empty(empty, location_offset, frame_count):
    empty.keyframe_insert("location", frame=1)
    empty.location.y = location_offset
    empty.keyframe_insert("location", frame=frame_count)

# Add the camera to the current scene at a set location and rotation
def add_camera():
    # Need to add the camera to the scene
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    
    # tell the computer where to add the camera
    camera.location.x = 0  #7.5
    camera.location.y = -5  #-7
    camera.location.z = 0   #5
    
    camera.rotation_euler.x = 0 #64
    camera.rotation_euler.y = 0 #-0.5
    camera.rotation_euler.z = 0 #47 
    return camera
    
def animate_camera(camera, rotation_offset, frame_count):
    camera.keyframe_insert("location", frame=1)
    #camera.location.y = location_offset
    camera.rotation_euler.z = rotation_offset# change the rotation around the z-axis by some offset
    camera.keyframe_insert("location", frame=frame_count)
  

def animate_obj(obj, rotation_offset, frame_count):
    # Set an initial key frame at our current start location
    
    obj.keyframe_insert("location", frame=1)
    bpy.context.object.constraints["Follow Path"].offset = 15
#    obj_constraint = obj.constraints.new("FOLLOW_PATH")
#    obj_constraint.offset = rotation_offset
    
    obj.keyframe_insert("location", frame=frame_count)  

# Add constraint to track an "empty" object
def obj_track_empty(obj, empty):
    obj_constraint = obj.constraints.new("TRACK_TO")
    obj_constraint.target = empty
    
    #bpy.ops.object.constraint_add(type="TRACK_TO")
    #obj.constraints["Track To"].target = empty
    
# Get an object to follow a particular path
def obj_follow_path(obj, path, use_curve_follow):
    obj_constraint = obj.constraints.new("FOLLOW_PATH")
    obj_constraint.target = path
    obj_constraint.use_curve_follow = use_curve_follow
    
    #bpy.ops.object.constraint_add(type="FOLLOW_PATH")
    #obj.constraints["Follow Path"].target = path

def make_obj_child_of(child, parent):
    child_constraint = child.constraints.new("CHILD_OF")
    child_constraint.target = parent
    #bpy.ops.object.constraint_add(type='CHILD_OF')
    #obj.constraints["Child Of"].target = empty


if __name__ == "__main__":
    register()
    
    location_offset = 3
    rotation_offset = 15 # offset by 15 degrees
    frame_count = 100
    fps = 30
    radius = 5
    rotation = 90 * (np.pi/180) # stores in radians
    
    
    set_end_frame(frame_count)
    set_fps(fps)
    
    # Create all the objects
    obj_empty = create_object_empty(0, 0, 0, 0.5, 0.5, 0.5)
    camera = add_camera()
    horizontal_path = add_path(radius, 0, 0, 0, 0, 0, 0)
    vertical_path = add_path(radius, radius, 0, 0, rotation, rotation, 0) # To get in correct position when constraints are added
    
    # empties to have camera follow on the paths
    # Want both to start in the same position
    # FOR GUI: This is what we offset to make camera move!    
    hPath_empty = create_object_empty(0, 0, 0, 0.25, 0.25, 0.25)
    vPath_empty = create_object_empty(0, 0, 0, 0.25, 0.25, 0.25)
        
    # Set the constraints for each object
    obj_follow_path(hPath_empty, horizontal_path, True)
    obj_follow_path(vPath_empty, vertical_path, True)
    
    # Need vertical path to follow the horizontal path
    obj_follow_path(vertical_path, horizontal_path, True)  

    # Make objects children to place objects at locations in the scene
    make_obj_child_of(vertical_path, hPath_empty)
    make_obj_child_of(camera, hPath_empty)
    make_obj_child_of(camera, vPath_empty)
    
    # Have the camera track the object in the center
    obj_track_empty(camera, obj_empty)    
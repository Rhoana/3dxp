import fnmatch

from . import log

def match_name(_list, _glob='*'):
    in_name = lambda n: fnmatch.fnmatchcase(n, _glob)
    return (o for o in _list if in_name(o.name))

def in_groups(_list, _glob='*'):
    # All objects shared in list
    all_obj = set(_list.pop().objects)
    for _g in _list:
        all_obj &= set(_g.objects)
    # All shared objects that match
    return match_name(all_obj, _glob)

def near_z(obj, z):
    all_m = obj.material_slots
    all_i = range(len(all_m))
    def sort_name(i):
        m_name = all_m[i].name
        m_num = int(m_name.split('.')[0])
        return abs(z - m_num)
    # All materials closest to z
    return sorted(all_i, key=sort_name)

def move_z(obj, z):
    groups = obj.users_group
    VOL = next(match_name(groups, 'VOL*'))
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Translate image by origin and offset
    vol_z = VOL.origin[-1]
    sub_z = SUB.offset[-1]
    origin_z = vol_z + sub_z
    # Move to specified Z
    stack_z = SRC.from_mesh[-1] * z
    obj.location.z = origin_z + stack_z
    # Set texture to specified Z
    mat_num = near_z(obj, z)[0]
    obj.active_material_index = mat_num

def move_world_z(obj, w_z):
    """ Move to slice z (in blender units)
    """
    groups = obj.users_group
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Get the range of the subvolume
    sub_depth = SUB.subvolume[-1]
    low_z = SUB.offset[-1]
    # Get the z with respect to the stack
    stack_z = w_z - low_z
    # Use mesh z to move if in range
    if 0 <= stack_z <= sub_depth:
        mesh_z = stack_z / SRC.from_mesh[-1]
        move_z(obj, mesh_z)
        obj.hide = False
    # Hide the object
    else:
        obj.hide = True

def move_vox_z(obj, vox_z):
    """ Move to slice z (in voxel units)
    """
    groups = obj.users_group
    SRC = next(match_name(groups, 'SRC*'))
    w_z = vox_z / SRC.to_vox[-1]
    move_world_z(obj, w_z)


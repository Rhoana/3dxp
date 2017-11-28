import fnmatch

from . import cycler
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

def near_z(nodes, mesh_z):
    # Node names with only digits
    dig = lambda n: n.name.split('.')[0]
    is_dig = lambda n: dig(n).isdigit()
    all_z = filter(is_dig, nodes)
    def sort_name(node):
        n_num = int(dig(node))
        return abs(mesh_z - n_num)
    # All materials closest to z
    return sorted(all_z, key=sort_name)

def slice_z(obj, mesh_z):
    material = obj.active_material
    node_tree = material.node_tree
    nodes = node_tree.nodes
    z_node = near_z(nodes, mesh_z)[0]
    # Activate texture for z node
    cycler.link(material, z_node)

def slice_w_z(obj, w_z, rel=True):
    """ Material for z (in blender units)
    """
    groups = obj.users_group
    VOL = next(match_name(groups, 'VOL*'))
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Translate image by origin and offset
    if not rel:
        vol_z = VOL.origin[-1]
        sub_z = SUB.offset[-1]
        w_z = w_z - vol_z - sub_z
    # Get local z texture
    mesh_z = w_z / SRC.from_mesh[-1]
    # Set texture to specified Z
    slice_z(obj, mesh_z)

def move_z(obj, mesh_z):
    groups = obj.users_group
    VOL = next(match_name(groups, 'VOL*'))
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Translate image by origin and offset
    vol_z = VOL.origin[-1]
    sub_z = SUB.offset[-1]
    origin_z = vol_z + sub_z
    # Move to specified Z
    stack_z = SRC.from_mesh[-1] * mesh_z
    obj.location.z = origin_z + stack_z
    # Set texture to specified Z
    slice_z(obj, mesh_z)

def move_world_z(obj, w_z):
    """ Move to slice z (in blender units)
    """
    groups = obj.users_group
    SUB = next(match_name(groups, 'SUB*'))
    SRC = next(match_name(groups, 'SRC*'))
    # Get the range of the subvolume
    sub_depth = SUB.subvolume[-1]
    sub_z = SUB.offset[-1]
    # Get the z with respect to the stack
    stack_z = w_z - sub_z
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
    print('v_z', vox_z)
    groups = obj.users_group
    SRC = next(match_name(groups, 'SRC*'))
    w_z = vox_z / SRC.to_vox[-1]
    print('w_z', w_z)
    print('')
    move_world_z(obj, w_z)

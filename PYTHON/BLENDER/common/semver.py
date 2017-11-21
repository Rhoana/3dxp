import bpy

def all():
    def make_v1_scope(*args, **kwargs):
        return {
            'SCALE': args,
            'Types': dict(SCALE='3f', version='3i', **kwargs),
            'Name': ('SCALE', 'version'),
            'Type': 'Group',
        }
    v1_0_0 = {
        'SRC': make_v1_scope('to_um', 'to_vox', 'from_mesh'),
        'SUB': make_v1_scope('subvolume', 'offset'),
        'VOL': make_v1_scope('volume', 'origin', tmp='s'),
    }
    return {
        (1,0,0): v1_0_0 
    }

def name(version, scope):
    target = version.get(scope, {})
    props = target.get('Name', ())
    prop_kinds = read(version, scope, *props)
    for prop, kind in prop_kinds:
        yield prop, kind

def read(version, scope, *keys):
    target = version.get(scope, {})
    types = target.get('Types', {})
    for prop, key in target_props(target, *keys):
        kind = types.get(prop, types[key])
        yield prop, kind

def keys(version, scope, *keys):
    target = version.get(scope, {})
    for prop, key in target_props(target, *keys):
        yield prop

def target_props(target, *keys):
    if not keys:
        keys = target['Types'].keys()
    for key in keys:
        for prop in target.get(key, [key]):
            yield prop, key

def latest(versions):
    v_now = sorted(versions.keys()).pop()
    return versions[v_now], v_now

def setup(versions):
    bpy_props = {
        '3f': bpy.props.FloatVectorProperty,
        '3i': bpy.props.IntVectorProperty,
        's': bpy.props.StringProperty,
    }
    version = latest(versions)[0]
    # All objects targeted by version
    for scope, values in version.items():
        bpy_type = getattr(bpy.types, values['Type'])
        for key, fmt in read(version, scope):
            typer = bpy_props[fmt]
            if not hasattr(bpy_type, key):
                setattr(bpy_type, key, typer(key))

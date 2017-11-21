import bpy
import struct, base64, zlib

from . import semver
from . import sizer
from . import log

def to_name_hash(_format, _values):
    name_bytes = struct.pack(_format, *_values)
    name_zip = zlib.compress(name_bytes)
    name_hash = base64.encodebytes(name_zip)
    return name_hash.decode('utf-8').rstrip('\n')

def get_group_name(version, given, scope):
    name_fmt = ''
    name_vals = []
    # Check all the groups
    for key, new_fmt in semver.name(version, scope):
        name_vals += given[key]
        name_fmt += new_fmt
    # Compress values into a unique name
    uniq = to_name_hash(name_fmt, name_vals)
    return "{}:{}".format(scope, uniq)

def set_props(given, new_group, new_keys):
    for key in new_keys:
        value = given[key]
        setattr(new_group, key, value)

def get_group(version, given, scope):
    msg = 'Using {} {}'
    # Name group by specific properties
    name = get_group_name(version, given, scope)

    # Create new group if no group matches
    if name not in bpy.data.groups.keys():
        bpy.ops.group.create(name=name)
        new_group = bpy.data.groups[name]
        new_keys = semver.keys(version, scope)
        set_props(given, new_group, new_keys)
        msg = 'Made new {} {}'

    log.yaml('Debug', msg.format(scope, name))
    log_scale(version, given, scope)
    return bpy.data.groups[name]

def get_groups(versions, arg):
    given = sizer.get_scale(arg)
    # Add version number to given details
    version, v_name = semver.latest(versions)
    given['version'] = v_name
    given['tmp'] = arg.tmp

    groups = ['VOL', 'SUB', 'SRC']
    getter = lambda g: get_group(version, given, g)
    return {g:getter(g) for g in groups}

def log_scale(version, given, scope):
    messages = {
        'from': '1 %s unit = {1:g},{2:g},{3:g} x {0}μm',
        'to': '{0}μm = {1:g},{2:g},{3:g} × %s unit',
    }
    to_um = given['to_um'][0]
    for k in semver.keys(version, scope, 'SCALE'):
        if k == 'to_um':
            continue
        keywords = k.split('_')
        fmt = '{1:g},{2:g},{3:g} × {0}μm'
        if keywords[0] in messages:
            fmt = messages[keywords[0]] % keywords[-1]
        log.yaml(k, fmt.format(to_um, *given[k]))

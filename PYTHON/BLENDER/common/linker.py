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

def get_name(given, item):
    name_fmt = ''
    name_vals = []
    # Check all the groups
    for key in item['Keys']['Name']:
        name_vals += given[key]
        name_fmt += item['Types'][key]
    # Compress values into a unique name
    uniq = to_name_hash(name_fmt, name_vals)
    return "{}:{}".format(item['Name'], uniq)

def keywords(version, arg):
    given = sizer.get_scale(arg)
    # Add version number to given details
    given['tmp'] = getattr(arg,'tmp','tmp')
    given['version'] = version['Name']

    return given
    
def groups(versions, arg):

    version = versions[0]
    given = keywords(version, arg)
    # Get the size of world units
    world_um = max(given['to_um'])

    # Name, keys, values for all groups
    for scope, item in version['Items'].items():
        print (item['Type'])
        # Name group, get all keys and vlues
        props = {k:given[k] for k in item['Keys']['All']}
        name = get_name(given, item)
        if item['Type'] == 'Group':
            make_group(name, props)
            yield scope, name
        # Log keys and values for scale 
        for k in item['Keys']['SCALE']:
            log_scale(k, given[k], '%d μm' % world_um)

def make_group(name, props):
    msg = 'Using {}'
    # Create new group if no group matches
    if name not in bpy.data.groups.keys():
        bpy.ops.group.create(name=name)
        new_group = bpy.data.groups[name]
        # Fill all properties in group   
        for key, val in props.items():
            setattr(new_group, key, val)
        msg = 'Made new {}'

    log.yaml('Debug', msg.format(name))

def log_scale(k, v, world='1 BU'):
    default_fmt = '{1:g},{2:g},{3:g} × {0}'
    fmts = {
        'from': '1 {u} unit = {1:g},{2:g},{3:g} x {0}',
        'to': '{0} = {1:g},{2:g},{3:g} × {u} unit',
    }
    kw = k.split('_')
    fmt = fmts.get(kw[0], default_fmt)
    msg = fmt.format(world, *v, u=kw[-1])
    log.yaml(k, msg)

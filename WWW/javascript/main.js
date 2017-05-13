RATE = 1;
INTERV = 600;
NEWEVENT = false;
allstates = {allslices:[]};
allstates.allframes = [];
animation = false;
loading = false;
buffer = 0;

// Default frames
ALLFRAMES = []
// Declare depth and slice
ALLSLICE = 0
slice = 0;

function slice_mover(zed, delta=false){

  now = Number(buffer)
  buffer = Number(!buffer)

  // get location information  
  var vp = document.getElementById('view');
  var move_now = document.getElementById('move'+now)
  var move_buffer = document.getElementById('move'+buffer)
  var xyz_origin = move_buffer.getAttribute('translation')
  var origin = xyz_origin.split('-')[0]
  var z_old = slice
  var z_new = zed

  // get new z
  if (delta){
    z_new = Number(z_old) + zed
  }
  if (z_new < 0 || z_new >= ALLSLICE) {
    return 1;
  }
  if (loading){
    return 0;
  }
  loading = true
  slice = z_new
 
  // get texture inforrmation
  var now_hide = move_now.children[0]
  var buffer_hide = move_buffer.children[0] 

  buffer_shape = buffer_hide.children[0]
  buffer_parent = buffer_shape.children[0]
  buffer_texture = document.createElement('Texture')
  buffer_img = document.createElement('img')
  buffer_parent.innnerHTML = ''

  // hide current slice location
  buffer_hide.setAttribute('scale','1 -1 1')
  now_hide.setAttribute('scale','0 0 0')

  buffer_img.onload = function() {

    buffer_texture.appendChild(buffer_img)
    buffer_parent.appendChild(buffer_texture)

    // update visible slices
    now_hide.setAttribute('scale','1 -1 1')
    buffer_hide.setAttribute('scale','0 0 0')
    move_now.setAttribute('translation', origin +'-'+ slice)
    move_buffer.setAttribute('translation', origin +'-'+ slice)
    clipPlanes[0].Move(slice/ALLSLICE);
    clipPlanes[1].Move(slice/ALLSLICE);

    // move camera if animating
    if (animation) {
      var frame_new = ALLFRAMES[ALLSLICE-slice];
      vp.setAttribute('orientation',frame_new[1]);
      vp.setAttribute('position',frame_new[0]);
    }
    loading = false
  }
  var pad = "00000";
  if (pad.length){
    var sli = (pad+slice).slice(-pad.length)
    buffer_img.src = 'images/'+ sli +'.jpg'
  }
  else{
    buffer_img.src = 'images/'+ slice +'.jpg'
  }
  buffer_img.style.display = "none" 

  // return sucess
  return 0
};

function animate() {
  animation = !animation;
  var interv = setInterval(function() {
    if (!animation || slice_mover(-1*RATE, true)){
      clearInterval(interv);
    }    
  }, INTERV);
};

function parse_args() {
  var args = document.location.search.substring(1).split('&');
  argsParsed = {};
  for (var i=0; i < args.length; i++) {
      arg = unescape(args[i]);

      if (arg.length == 0) {
        continue;
      }

      if (arg.indexOf('=') == -1) {
          argsParsed[arg.replace(new RegExp('/$'),'').trim()] = true;
      }
      else {
          kvp = arg.split('=');
          argsParsed[kvp[0].trim()] = kvp[1].replace(new RegExp('/$'),'').trim();
      }
  }
  return argsParsed
}

interpolate = function(k_slices, k_frames) {
  // Interpolation array
  var output = [];
  // Go through all slices
  for ( var k = 1; k < k_slices.length; k++) {
    // Get starting and the ending slices
    var z0 = k_slices[k-1];
    var z1 = k_slices[k];
    var z_diff = Math.abs(z1 - z0);
    // Get starting and ending positions, rotations
    var p0 = k_frames[k-1][0];
    var r0 = k_frames[k-1][1];
    var p1 = k_frames[k][0];
    var r1 = k_frames[k][1];
    // Now in the range between the slices
    for (var offset=0; offset < z_diff; offset++) {
      // Get the interpolation fraction
      var fraction = offset / z_diff;

      //////////////////////////
      // Get the axis of rotation
      var ax0 = vec3.fromValues(r0[0], r0[1], r0[2]);
      var ax1 = vec3.fromValues(r1[0], r1[1], r1[2]);
      // Convert the rotations to quaternions
      var q0 = quat.setAxisAngle(quat.create(), ax0, r0[3]);
      var q1 = quat.setAxisAngle(quat.create(), ax1, r1[3]);
      // Interpolate the quaternions
      var q_i = quat.slerp(quat.create(), q0, q1, fraction)
      // Get the new axis and angle
      var ax_i = vec3.create()
      var rad_i = quat.getAxisAngle(ax_i, q_i)
      // Get the interpolated rotation
      var rot_i = [ax_i[0], ax_i[1], ax_i[2], rad_i]

      //////////////////////////
      // Get the translation position
      var tran0 = vec3.fromValues(p0[0], p0[1], p0[2])
      var tran1 = vec3.fromValues(p1[0], p1[1], p1[2])
      // Linear interpolate the positions
      var tran_i = vec3.lerp(vec3.create(), tran0, tran1, fraction)
      // Get the interpolated position
      var pos_i = [tran_i[0], tran_i[1], tran_i[2]]

      /////////////////////////
      // Push to the output array
      var frame_i = [pos_i.join(' '), rot_i.join(' ')]
      output.push(frame_i)
    }
  }
  return output
}

function startup(_depth) {

  // Get the depth and first slice from the html
  ALLSLICE = _depth;
  slice = _depth - 1;

  runtime = document.getElementById("r").runtime;
  scene = document.getElementById( "scene" );

  search_dict = parse_args()
  // Get json from the url
  if ('keyframes' in search_dict){
    var loaded = search_dict.keyframes
    var key_slices = JSON.parse(loaded).allslices
    var key_frames = JSON.parse(loaded).allframes
    // Crop slices and frames to the lower of the two lengths
    var key_count = Math.min(key_slices.length, key_frames.length)
    key_slices = key_slices.slice(0, key_count)
    key_frames = key_frames.slice(0, key_count)
    // Interpolate the keyframes
    ALLFRAMES = interpolate(key_slices, key_frames)
  }
  // two clipping planes
  clipScopeX = document.getElementById( "clipScopeX" );
  clipScopeY = document.getElementById( "clipScopeY" );
  clipPlanes = [];
  clipPlanes.push( new ClipPlane(clipScopeX, scene, runtime) );
  clipPlanes.push( new ClipPlane(clipScopeY, scene, runtime) );

  slice_mover(slice)
  
};

//
// viewpoint changed
function viewFunc(evt) {
// show viewpoint values
  if (evt && NEWEVENT) {
    NEWEVENT = false
    var pos = evt.position;
    var rot = evt.orientation;

    var camPos = [pos.x, pos.y, pos.z];
    var camRot = [rot[0].x, rot[0].y, rot[0].z, rot[1]];

    allstates.allslices.push(slice);
    allstates.allframes.push([camPos, camRot]);
  }
}

function pop_state(){
  document.body.className = 'red';
  setTimeout(function(){
    document.body.className = '';
  },1000);
  allstates.allslices.pop();
  allstates.allframes.pop();
}

function save_state(){
  document.body.className = 'green';
  setTimeout(function(){
    document.body.className = '';
  },1000);
  var vp = document.getElementById('view');
  vp.addEventListener('viewpointChanged', viewFunc);
  vp.setAttribute('bind', true);
  NEWEVENT = true;
}

function save_states(){
  document.body.className = 'green';
  setTimeout(function(){
    document.body.className = '';
  },1000)
  // Get keyframe info
  var sv_keyframes = JSON.stringify(allstates, null,'\t');
  var saved = encodeURIComponent(sv_keyframes);
  // Open this page with the keyframes in the URL
  window.open(window.location.pathname+'?keyframes='+saved, '_self');
}

function user_down(){
  animation = false;
  slice_mover(RATE,true);
}
function user_up(){
  animation = false;
  slice_mover(-1*RATE,true);
}

var actions = {
  32: animate,
  38: user_down,
  40: user_up,
  37: pop_state,
  39: save_state,
  16: save_states 
}

window.onkeydown = function(event) {
  if (event.keyCode in actions){
    actions[event.keyCode]();
  }
}

//////
/**
 * Created by Timo on 16.06.2014.
 * Added passing of scope on 07.01.2014.
 */
var ClipPlane = function ( scope, proxyParent, runtime )
{
    var _axis = "X";

    var _scope = scope;

    var _clipPlane = null;

    var _color = "1 1 1";

    var _volume = null;

    var _clipping = -1;
  
    var _normal = new x3dom.fields.SFVec3f(_clipping, 0, 0);
  
    var _angle = 0;
  
    var _distance = 0;

    var _proxyTransform = null;

    var _proxyCoordinates = null;

    var _proxyParent = proxyParent;

    var _runtime = runtime;

    var initialize = function ()
    {
        updateVolume(_scope);
        createProxy();
        createClipPlane();
    };

    this.Move = function ( value )
    {
        if ( _axis == "X" )
        {
            _distance = ((_volume.max.x - _volume.min.x) * value) + _volume.min.x;
        }
        else if ( _axis == "Y" )
        {
            _distance = ((_volume.max.y - _volume.min.y) * value) + _volume.min.y;
        }
        else if ( _axis == "Z" )
        {
            _distance = ((_volume.max.z - _volume.min.z) * value) + _volume.min.z;
        }
    
    updateClipPlane();
    updateProxy();
    };
  
  this.Rotate = function ( value )
    {
    var rotMat;
    
    _angle += value;
    
        if ( _axis == "X" )
        {
            // Convert the value to a rotation Matrix
      rotMat = x3dom.fields.SFMatrix4f.rotationY( value );

      // Rotate the normal
      _normal = rotMat.multMatrixPnt( _normal );
        }
        else if ( _axis == "Y" )
        {
            // Convert the value to a rotation Matrix
      rotMat = x3dom.fields.SFMatrix4f.rotationZ( value );

      // Rotate the normal
      _normal = rotMat.multMatrixPnt( _normal );
        }
        else if ( _axis == "Z" )
        {
            // Convert the value to a rotation Matrix
      rotMat = x3dom.fields.SFMatrix4f.rotationX( value );

      // Rotate the normal
      _normal = rotMat.multMatrixPnt( _normal );
        }
    
    updateClipPlane();
    updateProxy();
    
    };

    this.Axis = function ( axis )
    {
        _axis = axis;
      
    _angle = 0;
    
    _distance = 0;
    
    if ( _axis == "X" )
        {
            _normal = new x3dom.fields.SFVec3f(_clipping, 0, 0);
        }
        else if ( _axis == "Y" )
        {
            _normal = new x3dom.fields.SFVec3f(0, _clipping, 0);
      
        }
        else if ( _axis == "Z" )
        {
            _normal = new x3dom.fields.SFVec3f(0, 0, _clipping);
        }

    updateProxy();
        updateClipPlane();
        updateProxyCoordinates();
    };

    this.Clipping = function ( clipping )
    {
        _clipping = clipping;

    _angle = 0;
    
    _distance = 0;
    
    if ( _axis == "X" )
        {
            _normal = new x3dom.fields.SFVec3f(_clipping, 0, 0);
        }
        else if ( _axis == "Y" )
        {
            _normal = new x3dom.fields.SFVec3f(0, _clipping, 0);
      
        }
        else if ( _axis == "Z" )
        {
            _normal = new x3dom.fields.SFVec3f(0, 0, _clipping);
        }
    
    updateProxy();
        updateClipPlane();
    };

    var updateVolume = function (scope)
    {
        _volume = _runtime.getBBox( scope );
    };

    var updateClipPlane = function ()
    {
        if ( _axis == "X" )
        {
            //_clipPlane.setAttribute("plane", _clipping + " 0 0 0");
      _clipPlane.setAttribute("plane", _normal.x + " " + _normal.y + " " + _normal.z + " " + _distance);
        }
        else if ( _axis == "Y" )
        {
            //_clipPlane.setAttribute("plane", "0 " + _clipping + " 0 0");
      _clipPlane.setAttribute("plane", _normal.x + " " + _normal.y + " " + _normal.z + " " + _distance);
      
        }
        else if ( _axis == "Z" )
        {
            //_clipPlane.setAttribute("plane", "0 0 " + _clipping + " 0");
      _clipPlane.setAttribute("plane", _normal.x + " " + _normal.y + " " + _normal.z + " " + _distance);
        }
    };
  
  var updateProxy = function ()
    {
    
    if ( _axis == "X" )
        {
            _proxyTransform.setAttribute("translation", -_distance * _clipping + " 0 0");
      _proxyTransform.setAttribute("rotation", "0 1 0 " + _angle );
        }
        else if ( _axis == "Y" )
        {
      _proxyTransform.setAttribute("translation", "0 " + -_distance  * _clipping + " 0");
      _proxyTransform.setAttribute("rotation", "0 0 1 " + _angle );
        }
        else if ( _axis == "Z" )
        {
            _proxyTransform.setAttribute("translation", "0 0 " + -_distance * _clipping);
      _proxyTransform.setAttribute("rotation", "1 0 0 " + _angle );
        }
    
    };

    var updateProxyCoordinates = function ()
    {
        var p0, p1, p2, p3, p4;

        if ( _axis == "X")
        {
            p0 = "0 " + _volume.max.y + " " + _volume.min.z + ", ";
            p1 = "0 " + _volume.min.y + " " + _volume.min.z + ", ";
            p2 = "0 " + _volume.min.y + " " + _volume.max.z + ", ";
            p3 = "0 " + _volume.max.y + " " + _volume.max.z + ", ";
            p4 = "0 " + _volume.max.y + " " + _volume.min.z;

            _proxyCoordinates.setAttribute("point", p0 + p1 + p2 + p3 + p4);
        }
        else if ( _axis == "Y" )
        {
            p0 = _volume.min.x + " 0 " + _volume.max.z + ", ";
            p1 = _volume.min.x + " 0 " + _volume.min.z + ", ";
            p2 = _volume.max.x + " 0 " + _volume.min.z + ", ";
            p3 = _volume.max.x + " 0 " + _volume.max.z + ", ";
            p4 = _volume.min.x + " 0 " + _volume.max.z;

            _proxyCoordinates.setAttribute("point", p0 + p1 + p2 + p3 + p4);
        }
        else if ( _axis == "Z" )
        {
            p0 = _volume.min.x + " " + _volume.max.y + " 0, ";
            p1 = _volume.min.x + " " + _volume.min.y + " 0, ";
            p2 = _volume.max.x + " " + _volume.min.y + " 0, ";
            p3 = _volume.max.x + " " + _volume.max.y + " 0, ";
            p4 = _volume.min.x + " " + _volume.max.y + " 0";

            _proxyCoordinates.setAttribute("point", p0 + p1 + p2 + p3 + p4);
        }
    };

    var createClipPlane = function()
    {
        _clipPlane = document.createElement("ClipPlane");
        _clipPlane.setAttribute("plane", _clipping + " 0 0 0");
        _clipPlane.setAttribute("cappingStrength", "0.003");
        _clipPlane.setAttribute("cappingColor", _color);

        _scope.appendChild( _clipPlane );
    };

    var createProxy = function()
    {
        _proxyTransform = document.createElement("Transform");

        var shape = document.createElement("Shape");

        var app = document.createElement("Appearance");

        var mat = document.createElement("Material");
        mat.setAttribute("emissiveColor", _color);

        var line = document.createElement("LineSet");
        line.setAttribute("vertexCount", "5");

        _proxyCoordinates = document.createElement("Coordinate");

        updateProxyCoordinates( _axis );

        _proxyTransform.appendChild( shape );

        shape.appendChild( app );

        app.appendChild( mat );

        shape.appendChild( line );

        line.appendChild( _proxyCoordinates );

        _proxyParent.appendChild( _proxyTransform );
    };

    initialize();
};

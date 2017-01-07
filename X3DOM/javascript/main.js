SLICE = 1773;
DECLINE = 5;
alldone = true;

function slice_mover(zed){

  if (zed < 0) {
    return;
  }

  move_slice = document.getElementById('move_slice')
  move_origin = move_slice.getAttribute('translation').split('-')[0]
  move_slice.setAttribute('translation',move_origin+'-'+ zed)

  new_t = document.createElement('texture');
  new_img = document.createElement('img');
  
  new_img.onload = function() {
    a = document.getElementById('ourappearance');

    // a.innerHTML = "";    
    new_t.appendChild(new_img);
    a.appendChild(new_t);

    alldone = true;

    // update clipping planes
    clipPlanes[0].Move(SLICE/1773);
    clipPlanes[1].Move(SLICE/1773);

  }
  new_img.src = 'images/'+zed+'.png';  

};

function animate() {
  if (SLICE < 0) {
    SLICE = 1773;
  }

  interv = setInterval(function() {
    if (alldone) {
      alldone = false;
      SLICE = SLICE-DECLINE;
      slice_mover(SLICE);
      curchild = a.children[0];
      a.removeChild(curchild);      
    }
    // alldone = false;
  }, 500)
};

window.onload = function() {

  runtime = document.getElementById("r").runtime;
  scene = document.getElementById( "scene" );

  // two clipping planes
  clipScopeX = document.getElementById( "clipScopeX" );
  clipScopeY = document.getElementById( "clipScopeY" );
  clipPlanes = [];
  clipPlanes.push( new ClipPlane(clipScopeX, scene, runtime) );
  clipPlanes.push( new ClipPlane(clipScopeY, scene, runtime) );

  // update camera
  // runtime.showAll();
  vp = document.getElementById('viewpoint2');
  vp.setAttribute('bind', true);



  slice_mover(SLICE);

  // animate();
  
};

window.onkeypress = function() {
  animate();
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
alldone = true;

function slice_mover(zed){
  move_slice = document.getElementById('move_slice')
  move_origin = move_slice.getAttribute('translation').split('-')[0]
  move_slice.setAttribute('translation',move_origin+'-'+ zed)

  // em_slice = document.getElementById('em_slice')
  // em_path = em_slice.getAttribute('src').split('/')[0]
  // em_slice.src = em_path+'/'+ zed +'.png'


  new_t = document.createElement('texture');
  new_img = document.createElement('img');
  
  new_img.onload = function() {
    a = document.getElementById('ourappearance');

    // a.innerHTML = "";    
    new_t.appendChild(new_img);
    a.appendChild(new_t);


    alldone = true;
  }
  new_img.src = 'images/'+zed+'.png';  

};

function animate() {
  SLICE = 1773;
  setInterval(function() {
    if (alldone) {
      alldone = false;
      slice_mover(SLICE--);
      curchild = a.children[0];
      a.removeChild(curchild);      
    }
    // alldone = false;
  }, 500)
};

window.onload = function() {

  document.getElementById('r').runtime.showAll();

};

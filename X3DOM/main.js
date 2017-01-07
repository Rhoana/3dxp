slice_mover = function(zed){
  move_slice = document.getElementById('move_slice')
  move_origin = move_slice.getAttribute('translation').split('-')[0]
  move_slice.setAttribute('translation',move_origin+'-'+ zed)

  em_slice = document.getElementById('em_slice')
  em_path = em_slice.getAttribute('src').split('/')[0]
  em_slice.src = em_path+'/'+ zed +'.png'
}

window.onload = function() {

  document.getElementById('r').runtime.showAll();

};

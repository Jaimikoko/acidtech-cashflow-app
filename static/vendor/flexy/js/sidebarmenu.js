/*! Flexy Bootstrap Lite - Sidebar Menu */
document.addEventListener("DOMContentLoaded",function(){
  var toggler=document.querySelector(".sidebartoggler");
  var wrapper=document.getElementById("main-wrapper");
  if(toggler&&wrapper){
    toggler.addEventListener("click",function(e){
      e.preventDefault();
      wrapper.classList.toggle("show-sidebar");
    });
  }
});

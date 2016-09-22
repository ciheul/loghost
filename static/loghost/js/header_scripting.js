$(document).ready(function() {
  
  // header styling and name event
  $('#cross-check').find('.item').each(function(){
    if ( $(this).hasClass('active') ) {
      $('.nav-point').html($(this).find('a').html());
      $('#cross-check').css({'background-color':'rgba(0,0,0,.03)'});
      return;
    }
  });

  // missed clicked
  $('#cross-check div.item').click(function() {
    window.location.replace($(this).find('a').attr('href'));
    return;
  });

});
class Toggle {

  constructor(){ this.init(); }

  init() { 
    $('.toggle-yes.on').addClass("btn-success"); 
    $('.toggle-no.on').addClass("btn-primary"); 
    $('.btn-toggle .off').addClass("btn-default"); 

    
    $('.btn-toggle').click( function(e) { 
      e.preventDefault(); 
      let $btns = $(this).find('.btn'); 
      $btns.toggleClass('on').toggleClass('off');
      $($btns[0]).toggleClass('btn-success').toggleClass('btn-default'); 
      $($btns[1]).toggleClass('btn-primary').toggleClass('btn-default'); 
      let $field =  $("#organization_deactivated"), val = $field.val();
      $field.val( val === 'true' ? 'false' : 'true' ); 
    });
    
  }
}

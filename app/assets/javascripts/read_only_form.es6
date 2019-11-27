class ReadOnlyForm {

  constructor(){ this.init(); }

  init() { 
    let $rdonly =  $('.readonly');
    $rdonly.find('input, select,textarea').attr('disabled', 'disabled' );
    $rdonly.find('.help-block').remove();
   }

}

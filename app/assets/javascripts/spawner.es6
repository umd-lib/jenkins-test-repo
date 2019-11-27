class Spawner {
  
  constructor() {
    ($) => {
      $('.spawner').click( (e) =>{
        e.preventDefault(); 
        let model = $('form').data("model-klass"); 
        $('form input[name=authenticity_token]').attr('disabled', false); 
        $('form').append("<input name='" + model + "[spawned]' value='1' type='hidden'></input>"); 
        $('form .copy').attr('disabled', false);
        $('form').submit();
      })
    }(jQuery); 
  
  }
  
}

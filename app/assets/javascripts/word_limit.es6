class WordLimit {

  constructor(){ 
    let initF = this.init;
    $('.word-limit').each( function() { 
       initF($(this));  
     });
  }

  init($el) { 
    const navKeys = [33,34,35,36,37,38,39,40]; 
    const limit = parseInt($el.data('word-limit')); 
    const $help = $el.siblings(".help-block"); 
    const filter = function() { this.length > 0 };
    
    const countWords = () => { 
      return $.grep( $.trim($el.val()).split(/\s+/), function(word) { return word.length > 0 }).length;
    }
    
    const countMsg = (count) => {
      if ( count > 0 )  { return "<span class='pull-right counter'>( " + count + " words remaining )</span>" }
      if ( count  == 0 ) { return "<span class='pull-right counter'>125 word limit reached.</span>" }
      if ( count < 0 ) { return "<span class='pull-right counter'>Limit exceeded (" + ( count * -1 ) + " words over )</span>" }
    } 
    
    let current = countWords();

    let countCheck = () => { 
      let check = countWords();
      let alert = "text-muted";
      if ( check != current ) {
        current = check; 
        let left = limit - current;  
        
        alert = left > 0 ? 'text-warning' : 'text-danger'; 
        
        $help.find('.counter').remove(); 
        $help.append(countMsg(left)); 
        
        let toggleAlert = ()=> {
          $help.find(".counter").removeClass( (index, className) => { 
            return (className.match (/(^|\s)text-\S+/g) || []).join(' '); 
           }).addClass(alert);
        }
        setTimeout(toggleAlert, 5);
        
      
      } 
    }

    $el.on("keyup blur paste", (e) => {
      switch(e.type) {
        case 'keyup':
          if ($.inArray(e.which, navKeys) < 0) { countCheck(); } 
          break;
        case 'paste':
          setTimeout(countCheck, (e.type === 'paste' ? 5 : 0));
          break;
        default:
          countCheck(); 
      } 
    });

  }
}

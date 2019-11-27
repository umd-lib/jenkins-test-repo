class UnitSelector {

  constructor(){ this.init(); }

  init() { 

    let show_dept_units = (dept_id)=> {
      /* The depts_and_units is set in the form header erb file.
       * its passed in from ruby, like { 2: [ 8, 7, 6 ], 3: [ 5, 4 ] } */
      let units = new Set(depts_and_units[dept_id]); 
      let $unit_select = $('.unit-select');
      let spinner = new Spinner({ position: 'relative', top: '0%' }).spin( );
			$unit_select.parent()[0].insertBefore( spinner.el, $unit_select.next()[0] ); 
      $unit_select.prop('disabled', 'disabled');
      $unit_select.find('option').each( (i, el)=> { 
        let $el = $(el); 
        if ( units.has(parseInt(el.value)) || el.value === "" ) { $el.show(); } 
        else { $el.hide(); }
      });  
     
      setTimeout(()=> { $('.spinner').remove(); $unit_select.prop('disabled', false); }, 1000);
    }
    
    /* whenever the department changes, we update unit options */ 
    $('.department-select').on( 'change', (e)=>  {
      let dept_id = parseInt(e.target.value); 
      show_dept_units(dept_id); 
      $('.unit-select').val(''); 
    });
   
    /* initialize the unit selector. only show values for out dept */
    if ($('.department-select').length) {
      show_dept_units($('.department-select').val());
    }
  }
}

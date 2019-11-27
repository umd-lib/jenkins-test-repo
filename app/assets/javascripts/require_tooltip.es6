class RequireTooltip {

  constructor(){ this.init(); }

  init() { 
    $('label.required').tooltip({ title: "REQUIRED" })  
  }

}

class App {
 
  /* here we can call things we want to happen everywhere.. */
  constructor() {
    $( () => { 
      /* Make form date inputs use jquery datepicker */ 
      $('.datepicker').datepicker({ dateFormat: "yy-mm-dd" });
      /* Turn our show pages into read-only forms */ 
      new ReadOnlyForm(); 
      new StatusUpdate();
      new Toggle();
      new UnitSelector();
      new WordLimit();
      new Spawner();
      new RequireTooltip();
  }) 

  }

}

const app = new App();

class StatusUpdate {

  constructor(){ this.init(); }

  init() { 
    
    $("#select-all").change( ()=> { $('.select-record > input').click(); });
    
    $('#change-review-status a').click( (e)=>  {
      var $el = $(e.target); 
      
      let $checkboxes = $(".select-record input:checked");
      if ( $checkboxes.length < 1 ) { alert("Please select records for udating using the checkboxes in the first column"); return }
      
      var reviewStatus = $el.data('review-status');
      var recordType = $el.data('record-type');
      
      var updateReviewStatus = (id)=> {
        let url = window.location.pathname + "/" + id + '.json';   
        let data = {};
        data[recordType] = { review_status_id: reviewStatus};
        let fail = ()=> { alert("Sorry but there was an issue with Record  " + id); };
        
        return $.ajax({ url: url, type: "PUT", dataType: 'json', data: data, error: fail })
          .fail( fail );
      }
      
      var promises = [];
      $(".table.table-striped").spin({ scale: 4 });
      $.each( $checkboxes,  (i,el) => {
        promises.push( updateReviewStatus( $(el).val() ) ); 
      });
      // window.location.reload();
      $.when.apply($, promises).done( () => { window.location.reload(); });
  
    });
  }
}

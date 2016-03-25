$(function() {
    // init plugin (with callback)
    $('.clearable').clearSearch({ callback: function() { 
      $(document).trigger('onClearSearchEvent');
    } } );

    // update value
    $('.clearable').val('').change();
    
    // change width
    $('.clearable').width('200px').change();
});

$(function() {
    // init plugin (with callback)
    $('.clearableParticipantsList').clearSearch({ callback: function() { 
      searchParticipantList();
    } } );

    // update value
    $('.clearableParticipantsList').val('').change();
    
    // change width
    $('.clearableParticipantsList').width('200px').change();
});


searchParticipantList = function() {
  if (this.liveSearchTimer) {
    clearTimeout(this.liveSearchTimer);
  }

  this.liveSearchTimer = setTimeout(function() {
    var querryDict = {}
    $('#participantsSearchWrapper').find('.clearableParticipantsList').each(function(index, value){
      val = $(value);
      val.css("background-color", "white");
      name = val.context.name;
      value = val.context.value.trim();
      if (value) {
        querryDict[name] = value;
      }
    });
    this.participantsListViewGrid.remove();
    var collection = new Apros.collections.Participants();
    if (!jQuery.isEmptyObject(querryDict))
      collection.updateQuerryParams(querryDict);
    var participant_list_view = new Apros.views.ParticipantsInfo({collection: collection, el: '#participantsListViewGridBlock'});
    participant_list_view.render();
  }, 1000)
}

highlightSearchBar = function(item) {
  $('#participantsSearchWrapper').find('.clearableParticipantsList').each(function(index, value){
    val = $(value);
    name = val.context.name;
    if (name == item['tag'])
      val.css("background-color", "#B1C2CC");
  });
}
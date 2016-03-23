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

cloneHeader = function() {
  console.log("usa");
  var clonedHeader = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').clone(true);
  // $('#coursesListViewGridBlock').find('.bbGrid-grid-head').css("display", "none");
  // console.log(clonedHeader);
  
  clonedHeader.css("position", "absolute");
  clonedHeader.css("top", "0px");
  clonedHeader.css("left", "0px");

  clonedHeader.css("font-size", "12px");
  clonedHeader.css("cursor", "pointer");
  clonedHeader.css("background", "whitesmoke");
  clonedHeader.css("border-collapse", "separate");
  clonedHeader.css("border-spacing", "0");
  clonedHeader.css("table-layout", "fixed");
  var head = $('#coursesListViewGridBlock').find('.bbGrid-grid-head')[0];
  var width = window.getComputedStyle(head).width;
  var height = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').height();
  clonedHeader.css("width", width);
  clonedHeader.css("height", height);

  var tr = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').find('tr')[0];
  var trwidth = window.getComputedStyle(tr).width;
  var trheight = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').find('tr').height();
  clonedHeader.find('tr').css("width", trwidth);
  clonedHeader.find('tr').css("height", trheight);
  clonedHeader.find('tr').css("border-radius", "4px 0 0 0");
  
  var thWidths = []
  $('#coursesListViewGridBlock').find('.bbGrid-grid-head').find('th').each(function(index, value){
    console.log($(value));
    var width = window.getComputedStyle(value).width;
    thWidths.push(width);
  });
  console.log(thWidths);
  var i = 0
  clonedHeader.find('th').each(function(index, value){
    $(value).css("width", thWidths[i]);
    i = i+1;
  });

  // var thwidth = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').find('th').width();
  var thheight = $('#coursesListViewGridBlock').find('.bbGrid-grid-head').find('th').height();
  // clonedHeader.find('th').css("width", thwidth);
  clonedHeader.find('th').css("height", thheight);
  clonedHeader.find('th').css("background-color", "#f8f8f8");
  clonedHeader.find('th').css("box-sizing", "content-box");
  clonedHeader.find('th').css("overflow", "hidden");
  clonedHeader.find('th').css("white-space", "normal");
  clonedHeader.find('th').css("border-bottom", "1px solid #ccc");
  clonedHeader.find('th').css("border-top", "1px solid #ccc");
  clonedHeader.find('th').css("border-left", "1px solid #ccc");
  clonedHeader.find('th').css("display", "table-cell");
  clonedHeader.find('th').css("line-height", "1.28571rem");
  clonedHeader.find('th').css("padding", ".57143rem .71429rem .71429rem");
  clonedHeader.find('th').css("font-size", "1rem");
  clonedHeader.find('th').css("font-weight", "bold");
  clonedHeader.find('th').css("color", "#222");
  clonedHeader.find('th').css("text-align", "left");
  clonedHeader.find('th').css("margin", "0");
  console.log(clonedHeader);
  $('#coursesListViewGridBlock').prepend(clonedHeader);
}

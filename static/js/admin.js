function setTableColumns(row, charNumber){
    $('td', row).each(function(key, value){
      var maxChars = (typeof charNumber[key] !== 'undefined') ? charNumber[key] : null;
      var rowData = $(this);
      var unfilteredText = rowData.text();
      rowData.attr("title", unfilteredText);
      if(maxChars && maxChars < unfilteredText.length){
        rowData.text(unfilteredText.substring(0, maxChars) + "...");
      }
    });
}

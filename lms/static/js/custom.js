
$('.new-theme [data-block-type="pb-mrq"] input[type="checkbox"]').change(function (event) {

    if (event.target.checked) {
        console.log('checked')
        $(event.target).parent().addClass("selected")
    } else {
        console.log('not checked')
        $(event.target).parent().removeClass("selected")
    }
});



///  for MCQ radio buttons

$(function () {
    $('input[type=radio]').change(function (e) {
        var parent = $(e.target).parents('[data-block-type="pb-mcq"]');
        
        $(parent).find(".choice-selector").removeClass("selected")
        $(event.target).parent().addClass("selected");

    })
})



///  for POLL radio buttons

$(function () {
    $('input[type=radio]').change(function (e) {
        var parent = $(e.target).parents('[data-block-type="poll"]');
        $(parent).find(".poll-input-container").removeClass("selected")
        $(event.target).parent().addClass("selected");

    })

    // Poll Results
    $(".poll-result-input-container input[type=radio]:checked").parent().addClass('selected')
})



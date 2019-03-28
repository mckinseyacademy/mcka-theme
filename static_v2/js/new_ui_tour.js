
$(window).load(function()
{
  $('.newFeatureTour').modal('show');
  $.ajax({
        type: 'GET',
        url: '/accounts/new-ui-visited/',
        success: function (response) {
            console.log("New UI tour visited");
        },
        error: function (error) {

        }
    });
});

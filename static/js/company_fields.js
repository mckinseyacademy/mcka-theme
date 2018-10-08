$(function() {

    function validateFields(fields)
    {
        for(var i =0;i <fields.length;++i)
        {
            if(fields.indexOf(fields[i]) !== i )
            {
                return gettext("2 or more fields can not have the same name");
            }
            if(!fields[i].match(/^[0-9a-zA-Z]+$/))
            {
                return gettext("Only alphanumeric characters and spaces allowed");
            }
        }
    }

    $('#closeCompanyField').on('click',function()
    {
        $('#companyfields').foundation('reveal', 'close');
        $('#customFieldsTable').html('');
    });

    $('#submitCompanyFields').on('click',function()
    {
        var fields = [];
        $('#customFieldsTable .field').each(function(){ fields.push(this.value )});
        $('#companyCustomFieldsContainer .bbGrid-row').each(function(){ fields.push(this.dataset.title)   });
        var error = validateFields(fields);
        if(error)
        {
            $('#companyfields .error').text(error);
        }
        else
        {
            $('form#additionalFieldForm').submit();
        }

    });

    function addRow()
    {
        if(($('#companyCustomFieldsContainer .bbGrid-row').length + $('#customFieldsTable .field').length) < 4) {
            var field_number = $('#customFieldsTable .field').length;
            $('i.fa-plus').removeClass().addClass('fa fa-minus');
            $('#customFieldsTable').append('<div class="additional-field"><input class="field" type="text" name="field_name_'+field_number+'"><i class="fa fa-plus"></i></div>');
            $('.fa-plus').on('click', addRow);
            $('.fa-minus').unbind('click');
            $('.fa-minus').on('click', removeRow);
        }
        else
        {
           $('#companyfields .error').text(gettext('You can only add up to 4 fields'));
        }
    }
    function removeRow(evt)
    {
        $('#companyfields .error').text('');
        $(evt.target).parent().remove();
    }

    $(document).on('opened.fndtn.reveal', '#companyfields', function () {
        if ($('#companyCustomFieldsContainer .bbGrid-row').length < 4) {

            $('#companyfields .error').text('');
            $('#customFieldsTable').html('');
            $('#customFieldsTable').append('<div class="additional-field"><input class="field" type="text" name="field_name_0"><i class="fa fa-plus"></i></div>');
            $('.fa-plus').on('click', addRow);

        }
        else {
            $('#companyfields .error').text(gettext('You can only add up to 4 fields'));
            $('#submitCompanyFields').addClass('disabled');
        }
    });

});

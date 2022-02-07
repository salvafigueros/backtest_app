document.getElementById('exit').addEventListener('change', function () {
    var style_trailing = this.value == "trailingstop" ? 'block' : 'none';
    var style_time = this.value == "exittime" ? 'block' : 'none';
    document.getElementById('trailing_stop_configuration').style.display = style_trailing;
    document.getElementById('exit_time_configuration').style.display = style_time;
});

$(document).ready(function(){
    var maxField = 10; //Input fields increment limitation
    var addButton = $('.add_asset_backtesting_portfolio'); //Add button selector
    var wrapper = $('.field_wrapper_backtesting_portfolio'); //Input field wrapper
    var fieldHTML = '<div><p><label>Ticker:</label> <input type="text" name="asset[]" /></p><a href="javascript:void(0);" class="remove_asset_backtesting_portfolio" title="Remove field">Eliminar Activo<img src=""/></a></div>'; //New input field html 
    var x = 1; //Initial field counter is 1
    $(addButton).click(function(){ //Once add button is clicked
        if(x < maxField){ //Check maximum number of input fields
            x++; //Increment field counter
            $(wrapper).append(fieldHTML); // Add field html
        }
    });
    $(wrapper).on('click', '.remove_asset_backtesting_portfolio', function(e){ //Once remove button is clicked
        e.preventDefault();
        $(this).parent('div').remove(); //Remove field html
        x--; //Decrement field counter
    });
});
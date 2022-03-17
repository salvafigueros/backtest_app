document.getElementById('exit_trade').addEventListener('change', function () {
    var style_trailing = this.value == "trailing_stop" ? 'block' : 'none';
    var style_time = this.value == "exit_time" ? 'block' : 'none';
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


function saveBacktesting(user_id, starting_cash, currency, ticker_list, strategy, time_frame, exit_trade, exit_configuration){
    $.ajax({
        type: "POST",
        url: "/backtesting/save-backtesting",
        data: JSON.stringify({ user_id: user_id,
            starting_cash: starting_cash,
            currency: currency,
            ticker_list: ticker_list,
            strategy: strategy,
            time_frame: time_frame,
            exit_trade: exit_trade,
            exit_configuration: exit_configuration}),
        contentType: "application/json",
        datatType: 'json',
        success:function(result){
            $(result["button"]).html("Guardado");
        }
    });
}

function shareBacktesting(backtesting_id){
    $.ajax({
        type: "POST",
        url: "/backtesting/share",
        data: JSON.stringify({ backtesting_id: backtesting_id}),
        contentType: "application/json",
        datatType: 'json',
        success:function(result){
            $(".share_backtesting").html("Compartido");
        }
    });
}


function saveBacktestingManual(backtesting_manual_id){
    var backtesting_manual_name = window.prompt("Pon un Nombre al Backtesting: ")

    $.ajax({
        type: "POST",
        url: "/other/backtesting-manual/save",
        data: JSON.stringify({ backtesting_manual_id: backtesting_manual_id,
                                backtesting_manual_name: backtesting_manual_name}),
        contentType: "application/json",
        datatType: 'json',
        success:function(result){
            $(".save_backtesting_manual").remove()
           // $(".share_backtesting").html("Compartido");
        }
    });
}
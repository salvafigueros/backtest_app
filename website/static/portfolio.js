$(document).ready(function(){
    var maxField = 10; //Input fields increment limitation
    var addButton = $('.add_button'); //Add button selector
    var wrapper = $('.field_wrapper'); //Input field wrapper
    var fieldHTML = '<div><h3>Activo 1</h3><p><label>Ticker:</label> <input type="text" name="asset[]" /></p><p><label>Nº de Acciones/Contratos:</label> <input type="number" name="quantity[]" /></p><a href="javascript:void(0);" class="remove_button" title="Remove field">Eliminar Activo<img src=""/></a></div>'; //New input field html 
    var x = 1; //Initial field counter is 1
    $(addButton).click(function(){ //Once add button is clicked
        if(x < maxField){ //Check maximum number of input fields
            x++; //Increment field counter
            $(wrapper).append(fieldHTML); // Add field html
        }
    });
    $(wrapper).on('click', '.remove_button', function(e){ //Once remove button is clicked
        e.preventDefault();
        $(this).parent('div').remove(); //Remove field html
        x--; //Decrement field counter
    });
});


function confirm_share_portfolio(){
    var opcion = confirm("Clicka en Aceptar si quiere hacer pública la cartera");
    if (opcion == true) {
        return true;
	} else {
        return false;
	}   
}

function confirm_finish_portfolio(){
    var opcion = confirm("Clicka en Aceptar si quiere terminar la cartera");
    if (opcion == true) {
        return true;
	} else {
        return false;
	}   
}

function show_modify_position(position_id) {
    var x = document.getElementById(position_id);
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

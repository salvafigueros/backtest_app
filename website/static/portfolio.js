
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


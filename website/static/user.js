function show_modify_user_name() {
    var x = document.getElementById("modify_user_name");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function show_modify_user_full_name() {
    var x = document.getElementById("modify_user_full_name");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function show_modify_user_password() {
    var x = document.getElementById("modify_user_password");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}


function confirm_delete_user(){
    var opcion = confirm("Clicka en Aceptar si quiere eliminar a este usuario");
    if (opcion == true) {
        return true;
	} else {
        return false;
	}   
}

function confirm_modify_user(){
    var opcion = confirm("Clicka en Aceptar si quiere modificar la información de este usuario");
    if (opcion == true) {
        return true;
	} else {
        return false;
	}   
}

function confirm_modify_password(){
    var opcion = confirm("Clicka en Aceptar si quiere cambiar la contraseña.");
    if (opcion == true) {
        return true;
	} else {
        return false;
	}   
}

function show_upload_stock_prices(){
    var stock = document.getElementById("upload_stock_prices");
    var future = document.getElementById("upload_future_prices");
    if (stock.style.display === "none") {
        stock.style.display = "block";
        future.style.display = "none"
    } else {
        stock.style.display = "none";
    }
}

function show_upload_future_prices(){
    var stock = document.getElementById("upload_stock_prices");
    var future = document.getElementById("upload_future_prices");
    if (future.style.display === "none") {
        future.style.display = "block";
        stock.style.display = "none";
    } else {
        future.style.display = "none";
    }
}

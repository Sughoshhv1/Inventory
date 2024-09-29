function cheeck(){
    const c=document.getElementById("sp1");

    if(c.value.length==10){
        alert("succesfully signed in!!!!!!!");
        window.location.href="/login";
    }
    else{
        alert("invalid number of digits !!!!!!!!!!!!!!!!!!!");
    }
}


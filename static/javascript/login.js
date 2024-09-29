function check(){
    const user=document.getElementById("ip2");
    const pass=document.getElementById("ip1");
    const check1=parseInt("1234")

    if(user.value=='abcd'){
        if(pass.value.length==4){
            if(pass.value==check1){
                alert("succesfully logged in!!!!!!!");
                window.location.href="index.html";

            }
        }
    }
    else{
        alert("Try again")
    }
}
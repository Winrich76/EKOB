document.addEventListener("DOMContentLoaded", function() {


   let divPicture=document.getElementById('add_picture');
   let checkAddPicture=document.getElementById('check_add_picture');



   checkAddPicture.checked=false;
    checkAddPicture.addEventListener("change", function () {
        if (this.checked){
            divPicture.style.display="block"

        }else {
            divPicture.style.display="none"
        }

    })
});


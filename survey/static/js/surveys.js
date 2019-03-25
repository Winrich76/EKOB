document.addEventListener("DOMContentLoaded", function() {

    // ================= script table

    let details=document.querySelectorAll(".details");
    let headDetails=document.getElementById("head_details").children;
    let infoTable=document.getElementById("info_table");
    let infoDiv=document.getElementById('info_div');

    let trDataId=document.querySelectorAll(".data_id");

    let btnUpdate=document.getElementById("update");
    let btnDelete=document.getElementById("delete");
    let btnExecution=document.getElementById("execution");



    for (let detail of details ){
        detail.addEventListener('click', function () {
            infoDiv.classList.remove('invisible');

            let row=detail.children;

            for (let tr of trDataId ){
                 if (tr.dataset.id===row[0].id){
                     tr.style.display="table-row";
                 } else{
                     tr.style.display="none"
                 }
             }


            btnUpdate.parentElement.action=row[0].id;
            btnDelete.parentElement.action='delete/'+row[0].id;
            btnExecution.parentElement.action='execution/'+row[0].id;

                                                                // dodawanie elemnetów prawej górnej tabeli
            infoTable.innerHTML="";
            let i=0;
            for (let item of row){
                let newRow="<tr><th class='form_up'></th><td class='maxWidth'></td></tr>";
                infoTable.innerHTML +=newRow;
                infoTable.lastElementChild.firstElementChild.innerHTML=headDetails[i].innerHTML;
                infoTable.lastElementChild.lastElementChild.innerHTML=item.innerHTML;
                i+=1;
            }

        })
    }


    // ==================script django_filter

    let checkValid=document.getElementById("check_valid");
    let validDate=document.getElementById('id_valid_date_1');
    // let today=document.getElementById('today');
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    today = yyyy+'-'+ mm + '-' + dd;


    if (validDate.value){
        checkValid.checked=true;
    }else{
        checkValid.checked=false;
    }

    checkValid.addEventListener('change', function () {
       if (this.checked){
           // validDate.value=today.value;
           validDate.value=today;


       }else{
           validDate.value="";
       }

    })

});


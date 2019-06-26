document.addEventListener("DOMContentLoaded", function() {


   let divPicture=document.getElementById('add_picture');
   let checkAddPicture=document.getElementById('check_add_picture');
   let checkDeleteContracts=document.querySelectorAll('.delete_contract');
   let checkDeleteProjects=document.querySelectorAll('.delete_project');
   let checkDeleteDocuments=document.querySelectorAll('.delete_document');

   for (let checkDeleteContract of checkDeleteContracts){
       checkDeleteContract.checked=false;
   }
    for (let checkDeleteProject of checkDeleteProjects){
       checkDeleteProject.checked=false;
   }
    for (let checkDeleteDocument of checkDeleteDocuments){
       checkDeleteDocument.checked=false;
   }


   checkAddPicture.checked=false;
    checkAddPicture.addEventListener("change", function () {
        if (this.checked){
            divPicture.style.display="block"

        }else {
            divPicture.style.display="none"
        }

    })
});


document.addEventListener("DOMContentLoaded", function() {

    tr_all=document.querySelectorAll('.choice_tr');

    for (let tr of tr_all){
        tr.addEventListener('click', function () {

            window.open(tr.id, "_self");
        })
    }
});


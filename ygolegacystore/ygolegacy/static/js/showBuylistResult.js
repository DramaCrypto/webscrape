function updateInventory(element) {
    //document.getElementById("form-" + element_id).submit();
    $.ajax("/live/inventory?card_id="+element.id+"&new_value="+element.value, function(result) {
    console.log(result)
});

}

$(document).ready(function(){

     $('#set-code-box-buy, #new_buylist_searchbar').on('keyup change', function (event) {

        var inputVal = $('#new_buylist_searchbar').val();
        var setCodeVal = "";
                console.log('test', inputVal);
        if(inputVal.length<1){
            $("#results").hide();
        }
        else{
            $("#results").show();
            if (window.XMLHttpRequest) {
                // code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp = new XMLHttpRequest();
            } else {
                // code for IE6, IE5
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }
            xmlhttp.onreadystatechange = function() {

                if (this.readyState == 4 && this.status == 200) {
                    if ($('#cards').length > 0) {
                          document.getElementById("cards").innerHTML = "";
                        }
                    if ($('#saved').length > 0) {
                        document.getElementById("saved").innerHTML = "";
                    }
                    document.getElementById("results").innerHTML = this.responseText;

                }
            };

            if (document.getElementById('set-code-box-buy').checked) {
                setCodeVal = "1";
            } else {
                setCodeVal = "0";
            }
            xmlhttp.open("GET","/live/buylist/result?term="+inputVal+"&set_code="+setCodeVal,true);
            xmlhttp.send();
        }
    });
  });
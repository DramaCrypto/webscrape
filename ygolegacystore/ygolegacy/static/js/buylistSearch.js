$(document).ready(function(){
    $("#results").hide();

    $( "#buylist_searchbar" ).keyup(function( event ) {
        var inputVal = $(this).val();

        var raceVal = "";
        if (document.getElementById('race-checkbox').checked) {
            raceVal = "1";
        } else {
            raceVal = "0";
        }

        var typeVal = "";
        if (document.getElementById('type-checkbox').checked) {
            typeVal = "1";
        } else {
            typeVal = "0";
        }

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

            xmlhttp.open("GET","/live/buylist-result?term="+inputVal+"&race="+raceVal+"&type="+typeVal,true);
            xmlhttp.send();
        }
    });
  });
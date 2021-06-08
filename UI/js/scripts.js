/*!
* Start Bootstrap - Shop Homepage v4.3.0 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2021 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

async function getListings() {
    alert("hi")
    //$(selector).filter('.dishwasher.washer/dryer');
    let response = await fetch('https://kojk6n7n2e.execute-api.us-east-2.amazonaws.com/test/login');
    
    let data = await response.json()
    return data;
}

function displayFilters() {
    $(".dishwasher").filter("washer/dryer");
}

//$( "div, span, p.myClass" ).css( "border", "3px solid red" );

$(document).ready(function() {

    $('input').click(function() {
        var category = $(this).val();
    
        $('.' + category).each(function () {
            var anyChecked = false;
            var classArray = this.className.split(/\s+/);
    
            for(idx in classArray)
            {
                if ($('#filter-' + classArray[idx]).is(":checked"))
                {
                    anyChecked = true;
                    break;
                }
            }
    
            if (! anyChecked) $(this).hide();
            else $(this).show();
    
        });
    
    });

});
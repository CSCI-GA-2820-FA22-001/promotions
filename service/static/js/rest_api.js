$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_type").val(res.type);
        if (res.active == true) {
            $("#promotion_active").val("true");
        } else {
            $("#promotion_active").val("false");
        }
        $("#promotion_product_id").val(res.product_id);
        $("#promotion_value").val(res.value);
        $("#promotion_start").val((res.start_date).slice(0,10));
        $("#promotion_end").val((res.expiration_date).slice(0,10));
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_type").val("");
        $("#promotion_active").val("");
        $("#promotion_product_id").val("");
        $("#promotion_value").val("");
        $("#promotion_start").val("");
        $("#promotion_end").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a promotion
    // ****************************************

    $("#create-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let active = $("#promotion_active").val() == "true";
        let product_id = $("#promotion_product_id").val();
        let value = $("#promotion_value").val();
        let start = $("#promotion_start").val();
        let end = $("#promotion_end").val();

        let data = {
            "id": promotion_id,
            "name": name,
            "type": type,
            "active": active,
            "product_id": parseInt(product_id),
            "value": value,
            "start_date": start,
            "expiration_date": end
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a promotion
    // ****************************************

    $("#update-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let active = $("#promotion_active").val() == "true";
        let product_id = $("#promotion_product_id").val();
        let value = $("#promotion_value").val();
        let start = $("#promotion_start").val();
        let end = $("#promotion_end").val();

        let data = {
            "id": parseInt(promotion_id),
            "name": name,
            "type": type,
            "active": active,
            "product_id": parseInt(product_id),
            "value": value,
            "start_date": start,
            "expiration_date": end
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/promotions/${promotion_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a promotion
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let active = $("#active").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (type) {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }
        if (active) {
            if (queryString.length > 0) {
                queryString += '&active=' + active
            } else {
                queryString += 'active=' + active
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Type</th>'
            table += '<th class="col-md-2">Active</th>'
            table += '<th class="col-md-2">Product_Id</th>'
            table += '<th class="col-md-2">value</th>'
            table += '<th class="col-md-2">start</th>'
            table += '<th class="col-md-2">end</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table +=  `<tr id="row_${i}"><td>${promotion.id}</td><td>${promotion.name}</td><td>${promotion.type}</td><td>${promotion.active}</td><td>${promotion.product_id}</td><td>${promotion.value}</td><td>${(promotion.start_date).slice(0,10)}</td><td>${(promotion.expiration_date).slice(0,10)}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})

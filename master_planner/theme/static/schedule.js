function get_schedule(schedule_id) {
    const httpRequest = new XMLHttpRequest();
    const url = "/api/get_schedule/".concat(schedule_id);
    httpRequest.open("GET", url);

    httpRequest.onload = () => {
        console.log(httpRequest.response)
    }
    httpRequest.send()
    return httpRequest.response
}

function get_course(course_code) {
    const url = "/api/get_course/" + course_code;
    var checkbox = $("#check-" + course_code);
    var hp = $("#hp");

    if (checkbox.is(":checked")) {
        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                hp.text(parseInt(response.hp.replace("*", "")) + parseInt(hp.text()));
            }
        });
    } else {
        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                hp.text(parseInt(parseInt(hp.text()) - response.hp.replace("*", "")));
            }
        });
    }
}

function add_course(course_code) {
    var checkbox = $("#check-" + course_code);
    var my_courses = $("#my-courses");
    const url = "/api/get_course/" + course_code;

    if (checkbox.is(":checked")) {
        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                add_course_table(response, my_courses);
                add_course_db(1);
            }
        })

    } else {
        $("#my-course-" + course_code).remove();
        delete_course_db(1);
    }
}


function add_course_table(response, my_courses) {

    remove_course_btn = $("<span>", {
        text: "delete", 
        class: "material-symbols-outlined cursor-pointer font-2xl",
        
        })
    my_courses.append($("<tr>", {
    id: "my-course-" + response.course_code,
    class: "bg-white",
    append: [
            $("<td>", {text: response.course_code}),
            $("<td>", {text: response.course_name}),
            $("<td>", {text: response.hp}),
            $("<td>", {text: response.level}),
            $("<td>", {text: response.vof}),
            $("<td>", {append: [remove_course_btn] })
            ]
        })
    )
}

function load_course_info(course_code) {
    var course_container = $("#course-info-container-" + course_code);
    var info_container = $("#info-container-" + course_code);
    var examination_container = $("#examination-container-" + course_code);
    var loading = $("#courses-loader-" + course_code);
    
    if (info_container.children().length == 0) {
        $.ajax({
            url: "/api/get_extra_course_info/" + course_code, // The URL to which the AJAX request will be sent
            method: "GET", // The HTTP method (GET, POST, PUT, DELETE, etc.)
            dataType: "json", // The expected data type of the response
            success: function(response) {
              // The success callback function to handle the response
              info_container.append(course_info_div(response));
              examination_container.append(course_examination(response));

              loading.remove();
              console.log(response);
            },
            error: function(jqXHR, textStatus, errorThrown) {
              // The error callback function to handle any errors
              console.log("AJAX request failed: " + textStatus, errorThrown);
            }
          });
    }

    if (course_container.is(":visible")) {
        course_container.slideToggle(500);
    } else {
        course_container.slideToggle(500);
    }
    
}

function course_info_div(response) {
    // Assuming you have the variables response.course_code, response.course_name, response.examination, and response.examinator
    var courseCode = response.course_code;
    var courseName = response.course_name;
    var fields = response.main_field;
    var examinator = response.examinator;

    var info_1 = $('<div>', {
    class: 'flex space-x-2',
    append: [
        $('<p>', { class: 'text-xl font-bold', text: courseCode }),
        $('<p>', { text: courseName })
    ]
    });

    var info_2 = $('<div>', {
    class: 'flex space-y-2 flex-col text-black/75 ',
    append: [
        $('<p>', { text: 'Detaljer' , class: 'font-bold text-xl'}),
        $('<div>', {
        append: [
            $('<p>', { text: 'Huvudområde', class: 'font-bold'}),
            $('<p>', { text: fields.join(", ") })
        ]
        }),
        $('<div>', {
        append: [
            $('<p>', { text: 'Examinator', class: 'font-bold'}),
            $('<p>', { text: examinator })
        ]
        })
    ]
    });

    var info_container = $('<div>', {
        class: 'flex flex-col space-y-2',
        append: [
            info_1, 
            info_2
        ]
        
    });

    return info_container

}

function course_examination(response) {
    var examination = response.examination
    var courseCode = response.course_code;
    var container = $("#examination-container-" + courseCode);
    container.append($('<p>', { text: "Examinationsmoment", class: "font-bold font-xl"}));
    var table = $('<table>').appendTo(container);
    var thead = $('<thead>', {class: "text-xl text-black"}).appendTo(table);
    var tbody = $('<tbody>').appendTo(table);
    
    var trHead = $('<tr>').appendTo(thead);
    $('<th>').text('Kod').appendTo(trHead);
    $('<th>').text('Typ').appendTo(trHead);
    $('<th>').text('Hp').appendTo(trHead);
    $('<th>').text('Betygsskala').appendTo(trHead);

    for (var exam in examination) {
        var trBody = $('<tr>').appendTo(tbody);
        for (data in examination[exam]) {
            $('<td>').text(examination[exam][data]).appendTo(trBody);
        }
        tbody.append(trBody);
    }

    container.append($('<div>', { 
        class: "flex font-bold font-xl",
        append: [
            $("<a>", {
                href: "http://www.gamlatentor.se/LIU/" + courseCode,
                class: "bg-yellow-500 p-3 rounded-lg hover:bg-yellow-300 transition ease-in-out",
                text: "Gamla tentor"
            })
        ]
        })
        
    );

    return container
}

function add_course_db(scheduler_id) {
    var payload = JSON.stringify({"scheduler_id": scheduler_id});
    const url = "/api/account/choice";

    $.ajax({
        type: "POST",
        url: url,
        data: payload,
        success: function (response) {
            console.log(response);
        }
    });
}

function delete_course_db(scheduler_id) {
    var payload = JSON.stringify({"scheduler_id": scheduler_id});
    const url = "/api/account/choice";

    $.ajax({
        type: "DELETE",
        url: url,
        data: payload,
        success: function (response) {
            console.log(response);
        }
    });
}



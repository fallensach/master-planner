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
        class: "material-symbols-outlined cursor-pointer font-2xl text-black/75",
        
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
            $("<td>", {append: [remove_course_btn], class: "flex items-center"})
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

function get_courses_semester(semester, profile_code) {
    var semester_btn = $("#semester-btn-" + semester + "-" + profile_code);
    const url = "/api/get_courses/" + profile_code + "/" + semester;

    $.ajax({
        type: "GET",
        url: url,
        success: function (semester_data) {
            highlight_semester(semester, profile_code); 
            replace_period_table(1, semester_data);
        }
    });
}

function replace_period_table(period, semester_data) {
    var table_body = $("#table-" + period);

    table_body.empty();
    $.each(semester_data["period_1"], function(key, value) {
        var course_row = $('<tr>').appendTo(table_body);
        course_row.append(
            $("<td>", {text: value["course"]["course_code"]}),
            $("<td>", {text: value["course"]["course_name"]}),
            $("<td>", {text: value["course"]["hp"]}),
            $("<td>", {text: value["course"]["level"]}),
            $("<td>", {text: value["course"]["vof"]}),
            make_expand_btn(value["course"]["course_code"]),
        )
        table_body.append(course_row);
    })
}

function make_expand_btn(course_code) {
    var courseData = { "course_code": course_code };

    var tdElement = $('<td>').attr('id', 'expand-' + courseData["course_code"]).addClass('flex justify-center');

    var labelElement = $('<label>').addClass('swap bg-slate-300 rounded-md transition ease-in-out drop-shadow-sm hover:bg-yellow-500');

    var inputElement = $('<input>').attr({
        'type': 'checkbox',
        'id': courseData["course_code"],
        'class': 'hidden'
    }).on('click', function() {
        load_course_info(this.id);
    });

    var spanElementUp = $('<span>').addClass('material-symbols-outlined swap-on rounded-lg bg-yellow-500').text('keyboard_arrow_up');
    var spanElementDown = $('<span>').addClass('material-symbols-outlined swap-off').text('expand_more');

    labelElement.append(inputElement, spanElementUp, spanElementDown);
    tdElement.append(labelElement);

    return tdElement;
}

function highlight_semester(semester, profile_code) {
    var current_semester = $("#semester-btn-" + semester + "-" + profile_code);
    var semester_7 = $("#semester-btn-" + "7" + "-" + profile_code);
    var semester_8 = $("#semester-btn-" + "8" + "-" + profile_code);
    var semester_9 = $("#semester-btn-" + "9" + "-" + profile_code);
    var semesters = [semester_7, semester_8, semester_9];

    $.each(semesters, function(index, semester) {
        semester.removeAttr("class");
        semester.addClass("bg-slate-200 p-3 text-black/75 transition ease-in-out hover:bg-slate-500 hover:text-white");

    });
    
    current_semester.removeAttr("class")
    current_semester.addClass("bg-slate-800 p-3 text-white transition ease-in-out");
}
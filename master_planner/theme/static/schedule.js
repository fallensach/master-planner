$(document).ready(function () {
    var programs = JSON.parse($("#programs").text());
    const semester = $("#chosen-term").val();
    $("#id_program").autocomplete({
        source: programs,
        delay: 100,
        messages: {
            noResults: "Inga resultat",

        }
    });

    load_chosen_courses(semester);
});

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


function add_course(scheduler_id) {
    var checkbox = $("#check-" + scheduler_id);

    if (checkbox.is(":checked")) {
        add_course_db(scheduler_id);

    } else {
        delete_course_db(scheduler_id);

    }
}

function load_chosen_courses(semester) {
    const my_courses_1 = $("#my-courses-1");
    const my_courses_2 = $("#my-courses-2");
    const url = "/api/account/choices";

    $.ajax({
        type: "GET",
        url: url,
        success: function (picked_courses) {
            my_courses_1.empty();
            my_courses_2.empty();
            term_7_p_1 = picked_courses["semester_" + semester]["periods"]["period_1"]["courses"];
            term_7_p_2 = picked_courses["semester_" + semester]["periods"]["period_2"]["courses"];
            add_course_table(term_7_p_1, my_courses_1);
            add_course_table(term_7_p_2, my_courses_2);
            load_term_hp(picked_courses);
        }
    });
}

function load_term_hp(picked_courses) {
    for (var semester = 7; semester < 10; semester++) {
        semester_hp = $("#semester-" + semester + "-hp");
        semester_hp.text(picked_courses["semester_" + semester]["hp"]);
        for (var period = 1; period < 3; period++) {
            period_p = $("#semester-" + semester + "-p-" + period);
            period_p.text(picked_courses["semester_" + semester]["periods"]["period_" + period]["hp"])
        }
    }
}

function add_course_table(courses, my_courses) {
    $.each(courses, function (index, course_data) { 
        scheduler_id = course_data["scheduler_id"];
        remove_course_btn = $("<span>", {
            text: "delete", 
            class: "material-symbols-outlined cursor-pointer font-2xl text-black/75",
            onclick: "delete_course_db(" + scheduler_id + ")"
            })

        my_courses.append($("<tr>", {
            id: "my-course-" + scheduler_id,
            class: "bg-white font-bold",
            append: [
                    $("<td>", {text: course_data["course"]["course_code"], class: "text-center font-mono"}),
                    $("<td>", {text: course_data["course"]["course_name"], class: "w-2/5"}),
                    $("<td>", {text: course_data["course"]["hp"], class: "text-center"}),
                    $("<td>", {text: course_data["schedule"]["block"], class: "text-center"}),
                    $("<td>", {text: course_data["course"]["level"], class: "text-center"}),
                    $("<td>", {text: course_data["course"]["vof"], class: "text-center"}),
                    $("<td>", {append: [remove_course_btn], class: "flex items-center"})
                    ]
                })
            )        
    });

}

function load_course_info(course_code, scheduler_id) {
    var course_container = $("#course-info-container-" + scheduler_id);
    var info_container = $("#info-container-" + scheduler_id);
    var examination_container = $("#examination-container-" + scheduler_id);
    var loading = $("#courses-loader-" + scheduler_id);
    
    if (info_container.children().length == 0) {
        $.ajax({
            url: "/api/get_extra_course_info/" + course_code, // The URL to which the AJAX request will be sent
            method: "GET", // The HTTP method (GET, POST, PUT, DELETE, etc.)
            dataType: "json", // The expected data type of the response
            success: function(response) {
                console.log(response)
                // The success callback function to handle the response
                
                info_container.append(course_info_div(response));
                examination_container.append(course_examination(response, scheduler_id));
                loading.remove();
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

function course_examination(response, scheduler_id) {
    var examination = response.examination
    var courseCode = response.course_code;
    var container = $("#examination-container-" + scheduler_id);
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
    const semester = $("#chosen-term").val();


    $.ajax({
        type: "POST",
        url: url,
        data: payload,
        success: function (response) {
            console.log(response);
            load_chosen_courses(semester);
        }
    });
}

function delete_course_db(scheduler_id) {
    var payload = JSON.stringify({"scheduler_id": scheduler_id});
    const url = "/api/account/choice";
    const semester = $("#chosen-term").val();

    $.ajax({
        type: "DELETE",
        url: url,
        data: payload,
        success: function (response) {
            console.log(response);
            load_chosen_courses(semester);
        }
    });
}

function get_courses_semester(semester, profile_code) {
    const url = "/api/courses/" + profile_code + "/" + semester;

    $.ajax({
        type: "GET",
        url: url,
        success: function (semester_data) {
            highlight_semester(semester, profile_code); 
            replace_period_table(1, semester_data);
            replace_period_table(2, semester_data);
        }
    });
}

function replace_period_table(period, semester_data) {
    var table_body = $("#table-" + period);
    table_body.empty();

    $.each(semester_data[`period_${period}`], function(key, value) {
        var course_row = $('<tr>', {class: "bg-white hover:bg-slate-200/75 transition ease-in-out"}).appendTo(table_body);
        course_row.append(
            course_checkbox(value["scheduler_id"]),
            $("<td>", {text: value["course"]["course_code"], class: "text-center font-mono"}),
            $("<td>", {text: value["course"]["course_name"], class: "w-2/5"}),
            $("<td>", {text: value["course"]["hp"], class: "text-center"}),
            $("<td>", {text: value["schedule"]["block"], class: "text-center"}),
            $("<td>", {text: value["course"]["level"], class: "text-center"}),
            $("<td>", {text: value["course"]["vof"], class: "text-center"}),
            make_expand_btn(value["course"]["course_code"], value["scheduler_id"]),
        );
        table_body.append(course_row);
        table_body.append(expand_div(value["scheduler_id"]));
    })
}

function expand_div(scheduler_id) {
    var dropdown = $('<tr>').attr('id', 'dropdown-' + scheduler_id);
    var td = $('<td>').addClass('overflow-hidden p-0').attr('colspan', '8').attr('id', 'insert-' + scheduler_id);
    var courseInfoContainer = $('<div>').attr('id', 'course-info-container-' + scheduler_id).addClass('hidden overflow-hidden');
    var infoContainer = $('<div>').attr('id', 'info-container-' + scheduler_id).addClass('flex flex-col p-5 border-r-2 w-1/2 border-black/25');
    var examinationContainer = $('<div>').attr('id', 'examination-container-' + scheduler_id).addClass('flex flex-col p-5 space-y-2');
    
    var loadingButton = $('<button>').addClass('btn');
    var loadingSpinner = $('<span>').addClass('loading loading-spinner');
    var loadingText = $('<span>').text('Laddar');
    var coursesLoader = $('<span>').attr('id', 'courses-loader-' + scheduler_id).addClass('hidden').append(loadingButton.append(loadingSpinner).append(loadingText));
    
    var courseInfo = courseInfoContainer.append($('<div>').addClass('flex border-x-2 border-x-stone-100 border-t-2 border-t-stone-200 p-5 shadow-md bg-white mb-5 rounded-b-lg').append(coursesLoader).append(infoContainer).append(examinationContainer));
    
    var finalRow = td.append(courseInfo);
    dropdown.append(finalRow);
    
    return dropdown
}

function course_checkbox(scheduler_id) {
    var td = $('<td>', {align: "center"});
    var checkbox = $('<input>').attr({
    'type': 'checkbox',
    'onclick': 'add_course(this.value)',
    'class': 'checkbox flex checkbox-warning transition ease-in-out border-none bg-slate-300 hover:bg-slate-500 focus:ring-transparent',
    'id': 'check-' + scheduler_id,
    'value': scheduler_id
    });

    td.append(checkbox);

    return td
}

function make_expand_btn(course_code, scheduler_id) {

    var tdElement = $('<td>').attr('id', 'expand-' + scheduler_id).addClass('flex justify-center');

    var labelElement = $('<label>').addClass('swap bg-slate-300 rounded-md transition ease-in-out drop-shadow-sm hover:bg-yellow-500');

    var inputElement = $('<input>').attr({
        'type': 'checkbox',
        'value': scheduler_id,
        'name': course_code,
        'class': 'hidden'
    }).on('click', function() {
        load_course_info(this.name, this.value);
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
        semester.prop("disabled", false);
    });
    
    current_semester.removeAttr("class")
    current_semester.addClass("bg-slate-800 p-3 text-white transition ease-in-out");
    current_semester.prop("disabled", true);
}

function toggle_period(period) {
    var period_table = $("#period-" + period);
    var period_btn = $("#period-" + period + "-btn");
    var period_1_toggled = $("#period-" + 1 + "-btn").data("toggled");
    var period_2_toggled = $("#period-" + 2 + "-btn").data("toggled");

    var toggled = period_btn.data("toggled");

    if (period_1_toggled && period_2_toggled) {
        // Close the table
        period_table.slideToggle();
        period_btn.data("toggled", false);
        period_btn.removeAttr("class");
        period_btn.addClass("bg-slate-200 p-3 text-black/75 transition ease-in-out hover:bg-slate-500 hover:text-white");

    } else if (period == 1 && period_2_toggled && !toggled) {
        period_table.slideToggle();
        period_btn.data("toggled", true);
        period_btn.removeAttr("class");
        period_btn.addClass("bg-slate-800 p-3 text-white transition ease-in-out");

    } else if (period == 2 && period_1_toggled && !toggled) {
        period_table.slideToggle();
        period_btn.data("toggled", true);
        period_btn.removeAttr("class");
        period_btn.addClass("bg-slate-800 p-3 text-white transition ease-in-out");
    }
}

function highlight_semester_card(card_id, semester) {
    const term_7_card = $("#semester-7-card");
    const term_8_card = $("#semester-8-card");
    const term_9_card = $("#semester-9-card");
    const highlight_card = $("#" + card_id);
    $("#chosen-term").val(semester);


    var cards = [term_7_card, term_8_card, term_9_card];

    $.each(cards, function(index, card) {
        card.removeClass("card-active");
    });

    highlight_card.addClass("card-active");
}
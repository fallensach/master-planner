var header;
var sticky;
var all_courses;

$(document).ready(async function () {
    var programs = JSON.parse($("#programs").text());

    if (localStorage.getItem('term') != null) {
        semester = localStorage.getItem('term');
        console.log("Exists")
    } else {
        const semester = $("#chosen-term").val();
        localStorage.setItem("term", semester);
        console.log("Setting storage")
    }

    $("#id_program").autocomplete({
        source: programs,
        delay: 100,
        messages: {
            noResults: "Inga resultat",

        }
    });

    home = document.querySelector("#home-container");
    if (home != null) {
        home.onscroll = function() {scroll_home(home)};
    }
    get_courses_semester(semester);
    await load_chosen_courses(semester);
    loadRequirements();
});

function scroll_home(home) {
    header = document.querySelector("#pickable-courses");
    sticky = header.getBoundingClientRect().top;
    floatingRow = document.querySelector("#pop-up-row");
    table = document.querySelector("#tables-container");

    if (table.getBoundingClientRect().y > 95) {
        floatingRow.classList.add("hidden")
        }
    if (window.scrollY == sticky) {
        if (table.getBoundingClientRect().y < 80) {
            floatingRow.classList.remove("hidden")
        }

        header.classList.add("bg-yellow-accent");
        
    } else {
        header.classList.remove("bg-yellow-accent");

        }
    }

function check_course_boxes(periods) {
    for (var i = 1; i < 3; i ++) {
        var period = periods["period_" + i]["courses"];
        period.forEach(scheduler => {
            $("#check-" + scheduler["scheduler_id"]).prop("checked", true); 
            
        });
    }
}

async function add_course(scheduler_id) {
    var checkbox = $("#check-" + scheduler_id);
    semester = localStorage.getItem('term');
    if (checkbox.is(":checked")) {
        await add_course_db(scheduler_id);
        load_chosen_courses(semester);
    } else {
        await delete_course_db(scheduler_id);
    }
}

async function load_chosen_courses(semester) {
    const my_courses_1 = $("#my-courses-1");
    const my_courses_2 = $("#my-courses-2");
    const profile_code = $("#profile-code").val();
    const url = "/api/account/choices/" + profile_code;
    $.ajax({
        type: "GET",
        url: url,
        success: function (picked_courses) {
            my_courses_1.empty();
            my_courses_2.empty();
            term_p_1 = picked_courses["semester_" + semester]["periods"]["period_1"]["courses"];
            term_p_2 = picked_courses["semester_" + semester]["periods"]["period_2"]["courses"];
            add_course_table(term_p_1, my_courses_1, 1);
            add_course_table(term_p_2, my_courses_2, 2);
            load_term_hp(picked_courses);
            check_course_boxes(picked_courses["semester_" + semester]["periods"]);
            load_total_term_card(picked_courses);
        }
    });
}

function load_total_term_card(semesters_hp) {
    total_hp = $("#semesters-total-hp");
    total_hp_advanced = $("#semesters-total-hp-advanced");
    total_hp_basic = $("#semesters-total-hp-basic");

    for (var i = 7; i < 10; i++) {
        semester_hp = semesters_hp["semester_" + i]["hp"]["total"]
        check_mark = $("#semester-" + i + "-check");
        check_tooltip = $("#tooltip-term-" + i);
        $("#semester-" + i + "-total-hp").text(semester_hp)
        if (semester_hp < 30) {
            var needed_hp = 30 - semester_hp;
            check_mark.addClass("fill-red-500")
            check_tooltip.text("Du behöver minst 30 hp per termin. Du behöver " + needed_hp + " hp till");
        } else {
            check_mark.addClass("fill-green-500");
            check_mark.removeClass("fill-red-500");
            check_tooltip.text("Minst 30 hp uppnådd");
        }
    }

    total_hp.text(semesters_hp["hp"]["total"]);
    total_hp_advanced.text(semesters_hp["hp"]["a_level"]);
    total_hp_basic.text(semesters_hp["hp"]["g_level"]);
}

function load_term_hp(picked_courses) {
    for (var semester = 7; semester < 10; semester++) {
        semester_hp = $("#semester-" + semester + "-hp");
        advanced_hp = $("#semester-" + semester + "-advanced");
        basic_hp = $("#semester-" + semester + "-basic");

        advanced_hp.text(picked_courses["semester_" + semester]["hp"]["a_level"]);
        basic_hp.text(picked_courses["semester_" + semester]["hp"]["g_level"]);
        semester_hp.text(picked_courses["semester_" + semester]["hp"]["total"]);

        for (var period = 1; period < 3; period++) {
            period_p = $("#semester-" + semester + "-p-" + period);
            period_p.text(picked_courses["semester_" + semester]["periods"]["period_" + period]["hp"]["total"])
        }
    }
}

function add_course_table(courses, my_courses, period) {
    if (courses.length == 0) {
        my_courses.append($("<tr>", {
            id: "my-course-placeholder-" + period,
            class: "bg-white font-bold",
            append: [
                    $("<td>", {text: "Inga kurser valda", class: "px-20", colspan:"8"}),
                    ]
                })
            ) 
    }
    
    $.each(courses, function (index, course_data) { 
        scheduler_id = course_data["scheduler_id"];
        remove_course_btn = $("<span>", {
            text: "delete", 
            class: "material-symbols-outlined cursor-pointer font-2xl text-black/75",
            onclick: `delete_course_db(\'${scheduler_id}\')`
            })

        my_courses.append($("<tr>", {
            id: "my-course-" + scheduler_id,
            class: "bg-white font-bold transition ease hover:bg-slate-200",
            append: [
                    $("<td>", {text: course_data["course"]["course_code"], class: "text-center font-mono"}),
                    $("<td>", {class: "w-2/5 underline"}).append($("<a>", {href: "https://studieinfo.liu.se/kurs/" + course_data["course"]["course_code"], 
                                                                 text: course_data["course"]["course_name"],
                                                                 class: "hover:text-yellow-500 transition ease",
                                                                 target: "_blank"
                                                                })),
                    $("<td>", {text: course_data["course"]["hp"], class: "text-center"}),
                    $("<td>", {text: course_data["schedule"]["block"], class: "text-center"}),
                    $("<td>", {text: course_data["course"]["level"], class: "text-center"}),
                    $("<td>", {text: course_data["vof"], class: "text-center"}),
                    make_expand_btn(course_data["course"]["course_code"], course_data["scheduler_id"], "my"),
                    $("<td>", {append: [remove_course_btn], class: "text-center"}),
                    ]
                })
            )
        my_courses.append(expand_div(course_data["scheduler_id"], "my"))
           
    });

}

async function load_course_info(course_code, scheduler_id, container_type) {
    var course_container = $("#course-info-container-" + scheduler_id + "-" + container_type);
    var info_container = $("#info-container-" + scheduler_id + "-" + container_type);
    var examination_container = $("#examination-container-" + scheduler_id + "-" + container_type);
    
    if (info_container.children().length == 0) {
        $.ajax({
            url: "/api/get_extra_course_info/" + course_code, // The URL to which the AJAX request will be sent
            method: "GET", // The HTTP method (GET, POST, PUT, DELETE, etc.)
            dataType: "json", // The expected data type of the response
            success: function(response) {
                // The success callback function to handle the response
                
                info_container.append(course_info_div(response));
                examination_container.append(course_examination(response, scheduler_id, container_type));
                course_container.slideToggle(200);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // The error callback function to handle any errors
                console.log("AJAX request failed: " + textStatus, errorThrown);
            }
          });
    } else {
        toggle_details(course_container);
    }

    
}

function toggle_details(course_container) {
    if (course_container.is(":visible")) {
        course_container.slideToggle(200);
    } else {
        course_container.slideToggle(200);
    }
}

function course_info_div(response) {
    var courseCode = response.course.course_code;
    var courseName = response.course.course_name;
    var fields = response.main_fields;
    var examinator = response.examinator;

    var info_1 = $('<div>', {
    class: 'flex items-center space-x-2',
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

function course_examination(response, scheduler_id, container_type) {
    var examination = response.examinations
    var courseCode = response.course.course_code;
    var container = $("#examination-container-" + scheduler_id + "-" + container_type);
    container.append($('<p>', { text: "Examinationsmoment", class: "font-bold font-xl"}));
    var table = $('<table>').appendTo(container);
    var thead = $('<thead>', {class: "text-xl text-black"}).appendTo(table);
    var tbody = $('<tbody>').appendTo(table);
    
    var trHead = $('<tr>').appendTo(thead);
    $('<th>').text('Kod').appendTo(trHead);
    $('<th>').text('Typ').appendTo(trHead);
    $('<th>').text('Hp').appendTo(trHead);
    $('<th>').text('Betygsskala').appendTo(trHead);

    $.each(examination, function (i) { 
        var trBody = $('<tr>').appendTo(tbody);
        trBody.append($('<td>').text(examination[i]["code"]));
        trBody.append($('<td>').text(examination[i]["name"]));
        trBody.append($('<td>').text(examination[i]["hp"]));
        trBody.append($('<td>').text(examination[i]["grading"]));
        tbody.append(trBody);
    });

    container.append($('<div>', { 
        class: "flex font-bold font-xl",
        append: [
            $("<a>", {
                href: "http://www.gamlatentor.se/LIU/" + courseCode,
                class: "bg-yellow-500 p-3 rounded-lg hover:bg-yellow-300 transition ease-in-out",
                text: "Gamla tentor",
                target: "_blank"
            })
        ]
        })
        
    );

    return container
}

async function add_course_db(scheduler_id) {
    var payload = JSON.stringify({"scheduler_id": scheduler_id});
    const url = "/api/account/choice";

    $.ajax({
        type: "POST",
        url: url,
        data: payload,
        success: function (response) {
            $("#check-" + response["scheduler_id"]).prop("checked", true);
        }
    });
}

async function delete_course_db(scheduler_id) {
    var payload = JSON.stringify({"scheduler_id": scheduler_id});
    const url = "/api/account/choice";
    semester = localStorage.getItem('term');

    $.ajax({
        type: "DELETE",
        url: url,
        data: payload,
        success: function (response) {
            load_chosen_courses(semester)
            $("#check-" + response["scheduler_id"]).prop("checked", false);
            $("#check-" + scheduler_id).prop("checked", false);
        }
    });
}

function sort_courses(tag, id) {
    var semester = $("#chosen-term").val();
    th = $("#" + id);
    th.data("ascend", !th.data("ascend"));

    for (var i = 1; i < 3; i++) {
        var sorted_courses = Object.keys(all_courses["period_" + i])
        .map(function(key) {
            return all_courses["period_" + i][key];
        })
        .sort(function(a, b) {
            if (tag == "block") {
                return a.schedule[tag].localeCompare(b.schedule[tag]);
            }
            return a.course[tag].localeCompare(b.course[tag]);
        });

        if (th.data("ascend")) {
            sorted_courses.reverse();
        } 

        all_courses["period_" + i] = sorted_courses
    }

    get_courses_semester(semester, true)
}

function get_courses_semester(semester, sort=false) {
    profile_code = $("#profile-code").val();
    localStorage.setItem('term', semester);
    if (sort) {
        replace_period_table(1, all_courses);
        replace_period_table(2, all_courses);
        load_chosen_courses(semester);

    } else {
        const url = "/api/courses/" + profile_code + "/" + semester;
        $.ajax({
            type: "GET",
            url: url,
            success: function (semester_data) {
                all_courses = semester_data;
                highlight_semester(semester);
                highlight_semester_card(`semester-${semester}-card`, semester);
                replace_period_table(1, semester_data);
                replace_period_table(2, semester_data);
                load_chosen_courses(semester)
            }
        });
    }

}

function replace_period_table(period, semester_data) {
    var table_body = $("#table-" + period);
    table_body.empty();

    $.each(semester_data[`period_${period}`], function(key, value) {
        var course_row = $('<tr>', {class: "bg-white text-left hover:bg-slate-200 font-bold transition ease-in-out"}).appendTo(table_body);
        course_row.append(
            course_checkbox(value["scheduler_id"]),
            $("<td>", {text: value["course"]["course_code"], class: "text-left font-mono"}),
            $("<td>", {class: "w-2/5 underline"}).append($("<a>", {href: "https://studieinfo.liu.se/kurs/" + value["course"]["course_code"], 
                                                         text: value["course"]["course_name"],
                                                         class: "hover:text-yellow-500 transition ease",
                                                         target: "_blank"
                                                        
                                                        })),
            $("<td>", {text: value["course"]["hp"]}),
            $("<td>", {text: value["schedule"]["block"]}),
            $("<td>", {text: value["course"]["level"]}),
            $("<td>", {text: value["vof"]}),
            make_expand_btn(value["course"]["course_code"], value["scheduler_id"], "all"),
        );
        table_body.append(course_row);
        table_body.append(expand_div(value["scheduler_id"], "all"));
    })
}

function expand_div(scheduler_id, container_type) {
    var dropdown = $('<tr>').attr('id', 'dropdown-' + scheduler_id + "-" + container_type);
    var td = $('<td>').addClass('overflow-hidden p-0').attr('colspan', '8').attr('id', 'insert-' + scheduler_id + "-" + container_type);
    var courseInfoContainer = $('<div>').attr('id', 'course-info-container-' + scheduler_id + "-" + container_type).addClass('hidden overflow-hidden');
    var infoContainer = $('<div>').attr('id', 'info-container-' + scheduler_id + "-" + container_type).addClass('flex flex-col p-5 border-r-2 w-1/2 border-black/25');
    var examinationContainer = $('<div>').attr('id', 'examination-container-' + scheduler_id + "-" + container_type).addClass('flex flex-col p-5 space-y-2');
    
    
    var courseInfo = courseInfoContainer.append($('<div>').addClass('flex border-x-2 border-x-stone-100 border-t-2 border-t-stone-200 p-5 shadow-md bg-white mb-5 rounded-b-lg').append(infoContainer).append(examinationContainer));
    
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

function make_expand_btn(course_code, scheduler_id, container_type) {

    var tdElement = $('<td>').attr('id', 'expand-' + scheduler_id).addClass('flex justify-center');

    var labelElement = $('<label>').addClass('swap bg-slate-300 rounded-md transition ease-in-out drop-shadow-sm hover:bg-yellow-500');

    var inputElement = $('<input>').attr({
        'type': 'checkbox',
        'value': scheduler_id,
        'name': course_code,
        'data-type': container_type,
        'class': 'hidden'
    }).on('click', function() {
        load_course_info(this.name, this.value, container_type);
    });

    var spanElementUp = $('<span>').addClass('material-symbols-outlined swap-on rounded-lg bg-yellow-500').text('keyboard_arrow_up');
    var spanElementDown = $('<span>').addClass('material-symbols-outlined swap-off').text('expand_more');

    labelElement.append(inputElement, spanElementUp, spanElementDown);
    tdElement.append(labelElement);

    return tdElement;
}

function highlight_semester(semester) {
    var current_semester = $("#semester-btn-" + semester);
    var semester_7 = $("#semester-btn-" + "7");
    var semester_8 = $("#semester-btn-" + "8");
    var semester_9 = $("#semester-btn-" + "9");
    
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
    var period_2 = $("#toggle-period-2");

    var toggled = period_btn.data("toggled");

    if (period_1_toggled && period_2_toggled) {
        // Close the table
        period_table.slideToggle(200);
        period_btn.data("toggled", false);
        period_btn.removeAttr("class");
        period_btn.addClass("bg-slate-200 p-3 text-black/75 transition ease-in-out hover:bg-slate-500 hover:text-white");

        if (period != 2) {
            period_2.removeAttr("style")
        }

    } else if (period == 1 && period_2_toggled && !toggled) {
        period_table.slideToggle(200);
        period_btn.data("toggled", true);
        period_btn.removeAttr("class");
        period_btn.addClass("bg-slate-800 p-3 text-white transition ease-in-out");
        period_2.css("visibility", "collapse")

    } else if (period == 2 && period_1_toggled && !toggled) {
        period_table.slideToggle(200);
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

    var cards = [term_7_card, term_8_card, term_9_card];

    $.each(cards, function(index, card) {
        card.removeClass("card-active");
    });

    highlight_card.addClass("card-active");
}

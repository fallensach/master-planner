$(document).ready(function () {
    loadRequirements();
})


function loadRequirements() {
    fields = $("#semester-field-reqs");
    profiles = $("#semester-profile-reqs");
    term = $("#overview-7-card");

    for (var i = 0; i < 10; i++) {
        field = reqListItem("Informatik", 30);
        profile = reqListItem("Ai och maskininlörning", 12);
        fields.append(field)
        profiles.append(profile)
    }

    term.append(createWarning("7"))

}

function reqListItem(fieldName, hp) {
    const li = $('<li>').addClass('flex space-x-3 items-center');
    const span = $('<span>').addClass('flex space-x-5 justify-between items-center w-full text-base font-normal leading-tight text-gray-600 dark:text-gray-400');
    const p1 = $('<p>').text(fieldName);
    const p2 = $('<p>').text(hp);
    p2.addClass('text-lg')

    span.append(p1, p2);
    li.append(span);
    
    return li
}

function createWarning(semester) {
    const alertContent = $('<div>')
    .attr('id', 'alert-additional-content-' + semester)
    .addClass('p-4 flex flex-col text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800')
    .attr('role', 'alert');

    const alertHeader = $('<div>').addClass('flex items-center');

    const alertTitle = $('<h3>').addClass('text-lg font-medium').text('Varning schemakrock');

    alertHeader.append($('<span>').addClass('sr-only').text('Info'), alertTitle);

    const alertMessage = $('<div>').addClass('mt-2 mb-4 text-sm h-full').text('Du har en eller flera schemakrockar i denna termin.');

    const alertButtons = $('<div>').addClass('flex');
    const viewSchemaBtn = $('<button>')
    .attr('type', 'button')
    .addClass('text-white bg-red-800 hover:bg-red-900 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-xs px-3 py-1.5 mr-2 text-center inline-flex items-center dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800')
    .html('<svg class="-ml-0.5 mr-2 h-3 w-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 14"><path d="M10 0C4.612 0 0 5.336 0 7c0 1.742 3.546 7 10 7 6.454 0 10-5.258 10-7 0-1.664-4.612-7-10-7Zm0 10a3 3 0 1 1 0-6 3 3 0 0 1 0 6Z"/></svg>Visa schema');

    const dismissBtn = $('<button>')
    .attr('type', 'button')
    .addClass('text-red-800 bg-transparent border border-red-800 hover:bg-red-900 hover:text-white focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-xs px-3 py-1.5 text-center dark:hover:bg-red-600 dark:border-red-600 dark:text-red-500 dark:hover:text-white dark:focus:ring-red-800')
    .attr('data-dismiss-target', '#alert-additional-content-' + semester)
    .attr('aria-label', 'Close')
    .text('Avvisa');

    viewSchemaBtn.click(function () { 
       window.location.href = '../home'; 
    });

    alertButtons.append(viewSchemaBtn, dismissBtn);
    alertContent.append(alertHeader, alertMessage, alertButtons);

    return alertContent
}
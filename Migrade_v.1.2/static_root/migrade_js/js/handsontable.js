$(document).ready(function () {
        // Embed JavaScript code directly in the template
        var data = {{ data_json|safe }}; // Data passed from the view

        var container = document.getElementById('handsontable-container');
        var hot = new Handsontable(container, {
            data: data,
            colHeaders: ['Name', 'LRN', 'Sex'],
            rowHeaders: true,
            contextMenu: true,
            readOnly: true,
            stretchH: 'all',
        });
    });



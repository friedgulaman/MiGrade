$(document).ready(function () {
    // Button to toggle the right-side panel
    $("#togglePanelBtn").click(function () {
        $("#rightSidePanel").css("right", "0");
    });

    // Button to close the right-side panel
    $("#closePanelBtn").click(function () {
        $("#rightSidePanel").css("right", "-300px");
    });
});
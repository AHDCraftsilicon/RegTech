$(document).ready(function () {
    $(".c-toggle").click(function () {
        $(".side-bar").toggleClass("showmenu");
        $(".contain-main-part").toggleClass("full-contain-main-part");
    });
});

$(document).ready(function () {

    $('.select2').select2();

    // Listen for the 'select2:open' event
    $(document).on('select2:open', (e) => {
        const selectId = e.target.id;

        // Use a timeout to ensure the search field is rendered
        setTimeout(() => {
            $(".select2-search__field[aria-controls='select2-" + selectId + "-results']").each(function (key, value) {
                value.focus();
            });
        }, 100); // Adjust the delay as needed
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const currentPath = window.location.pathname;

    // Select all sidebar links
    const menuLinks = document.querySelectorAll('#side-main-menu .c-menu a');

    // Loop through each link
    menuLinks.forEach(link => {
        // Check if link's href matches the current path
        if (link.getAttribute('href') === currentPath) {
            // Add 'active' class to the parent <li> element
            link.parentElement.classList.add('active');
        }
    });
});


$(document).ready(function () {
    // When any link inside the dropdown is clicked
    $('#menu1sub1sub1 a').click(function () {
        // Remove 'active' class from all links inside the dropdown
        $('#menu1sub1sub1 a').removeClass('active');

        // Add 'active' class to the clicked link
        $(this).addClass('active');
    });
});


(function () {
    'use strict';
    window.addEventListener('load', function () {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation');
        // Loop over them and prevent submission
        var validation = Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();

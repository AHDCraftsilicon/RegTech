document.addEventListener('DOMContentLoaded', function () {
    const selectElements = document.querySelectorAll('.my-select');

    selectElements.forEach(function (selectElement) {
        new Choices(selectElement);
    });
});
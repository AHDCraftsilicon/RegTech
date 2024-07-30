$('select').each(function () {
    if (document.getElementsByClassName('popup-select')) {
        console.log('yes');
        $(this).select2({
            dropdownParent: $(this).parent(),
            selectionCssClass: "select2-form-control"
        });
    } else {
        console.log('noo');
        $(this).select2({
            dropdownParent: $(this).parent(),
            selectionCssClass: "select2-form-control"
        });
    }
});
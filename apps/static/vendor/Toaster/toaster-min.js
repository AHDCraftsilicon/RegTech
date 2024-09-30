function NotifyMessage(notifyParameter) {

    console.log(notifyParameter.type);
    
    // Remove existing toasts if they exist
    $("#toastContainer").empty();

    // Determine toast type class
    var toastClass = notifyParameter.type 
    // === 'info' ? 'bg-success' : 'bg-danger';
    console.log(toastClass);
    
    //var toastContainer = $('<div id="toastContainer" class="toast-container position-fixed bottom-0 end-0 p-3">');
    // Create toast structure
    var toastHtml = `
        <div class="toast align-items-center text-white ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
        <div class="toast-body">
                    ${notifyParameter.message}
        </div>
        </div>
        </div>`;
    // Append toast to container
    $("#toastContainer").append(toastHtml);

    // Initialize and show toast
    var toastElement = $("#toastContainer .toast").last()[0];
    var toast = new bootstrap.Toast(toastElement, {
        autohide: true,//notifyParameter.autoHideAfter != null, // Enable autohide if autoHideAfter is set
        delay: notifyParameter.autoHideAfter || 5000 // Default to 50 seconds if autoHideAfter is not set
    });

    // Make sure the toast element is correctly selected and initialized
    if (toastElement) {
        toast.show();
    } else {
        console.error('Toast element is null or undefined.');
    }

    // Handle positioning
    var canvasWidth = $(window).width();
    var toastWidth = $(toastElement).outerWidth(true); // `outerWidth(true)` includes margin
    var marginRight = 30;
    var rightPosition = canvasWidth - toastWidth - marginRight;

    // Apply the position
    $(toastElement).css({
        'position': 'absolute',
        'right': rightPosition + 'px'
    });
}
function enableFullScreen(elementId) {
    var elem = document.getElementById(elementId);

    if (elem) {
        /* If fullscreen mode is available, show the element in fullscreen */
        if (
            document.fullscreenEnabled || /* Standard syntax */
            document.webkitFullscreenEnabled || /* Safari */
            document.msFullscreenEnabled /* IE11 */
        ) {
            /* Show the element in fullscreen */
            if (elem.requestFullscreen) {
                elem.requestFullscreen(); /* Standard syntax */
            } else if (elem.webkitRequestFullscreen) { /* Safari */
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) { /* IE11 */
                elem.msRequestFullscreen();
            }
        } else {
            console.log("Fullscreen mode is not supported by this browser.");
        }
    } else {
        console.log("Element with id '" + elementId + "' not found.");
    }
}


function copyToClipboard(element) {
    var temp = document.createElement("textarea");
    document.body.appendChild(temp);
    temp.value = document.querySelector(element).textContent;
    temp.select();
    document.execCommand("copy");
    document.body.removeChild(temp);
    alert("JSON copied to clipboard!")
}


function Json_Download(element) {
    // Get the JSON string from the <pre> element by its ID
    const jsonContent = document.getElementById(element).textContent.trim();

    try {
        // Validate if the content is valid JSON
        const jsonObject = JSON.parse(jsonContent);

        // Convert JSON object back to string for pretty-printing
        const jsonString = JSON.stringify(jsonObject, null, 2);

        // Create a Blob with the JSON data
        const blob = new Blob([jsonString], { type: "application/json" });

        // Generate a timestamp for the filename
        const now = new Date();
        const timestamp = now.toISOString().replace(/[:.]/g, '-'); // Clean up format for filename

        // Create a temporary <a> tag for downloading
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${timestamp}.json`;  // Filename with timestamp

        // Append, click, and remove the link
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

    } catch (error) {
        console.error("Invalid JSON data:", error);
        alert("Invalid JSON format in the <pre> element.");
    }
}

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

// js/common.js

// Function to remove all HTML tags from a string
function stripHtmlTags(input) {
    return input.replace(/<\/?[^>]+(>|$)/g, "");  // Regular expression to match and remove HTML tags
}

// Common function to handle input events
function onInputEvent(event) {
    // Get the current input element
    const inputElement = event.target;

    // Remove any HTML tags from the input value
    const cleanValue = stripHtmlTags(inputElement.value);

    // Update the input value without HTML tags
    inputElement.value = cleanValue;

}

// Attach the event listener to all input fields
document.addEventListener('DOMContentLoaded', () => {
    // Get all input elements
    const inputs = document.querySelectorAll('input, textarea, select');

    // Attach the input event listener to each input element
    inputs.forEach(input => {
        input.addEventListener('input', onInputEvent);
    });
});

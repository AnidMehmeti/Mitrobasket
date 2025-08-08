// Get form input elements by their ID
const form = document.getElementById('form');
const full_name = document.getElementById('full_name');
const age = document.getElementById('age');

// Show error message and style input with error class
const setError = (element, message) => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = message;
    inputControl.classList.add('error');
    inputControl.classList.remove('success');
};

// Show success styling and clear value
const setSuccess = element => {
    const inputControl = element.parentElement;
    const errorDisplay = inputControl.querySelector('.error');

    errorDisplay.innerText = '';
    inputControl.classList.add('success');
    inputControl.classList.remove('error');
    element.value = ''; // Clears input value after successful submission
};

// Age validation – show custom messages for invalid age range
age.addEventListener('input', () => {
    const ageValue = Number(age.value);

    if (ageValue > 20) {
        age.setCustomValidity('Jeni të mëdhenjë për të regjistruar.');
    } else if (ageValue < 6) {
        age.setCustomValidity('Jeni të vegjël për të regjistruar.');
    } else {
        age.setCustomValidity('');
    }
});

// Form input validation for name
const validateInputs = () => {
    const full_nameValue = full_name.value.trim();

    if (full_nameValue === '') {
        setError(full_name, "Full name is required.");
    } else {
        setSuccess(full_name);
    }

};

// Restrict input to only letters, spaces, dash, and Albanian characters
document.querySelectorAll('.only-letters').forEach(function(input) {
    input.addEventListener('input', function () {
        this.value = this.value.replace(/[^A-Za-zÇçëË\s\-]/g, '');
    });
});

// Automatically format phone numbers to: +383 4X XXX XXX
function formatPhoneNumber(input) {
    const prefix = "+383 4";

    if (!input.value.startsWith(prefix)) {
        input.value = prefix;
    }

    // Remove non-digit characters and keep only 7 digits after prefix
    let remaining = input.value.slice(prefix.length).replace(/\D/g, "").slice(0, 7);

    let formatted = "";
    if (remaining.length > 0) {
        formatted += remaining[0];
    }
    if (remaining.length > 1) {
        formatted += " " + remaining.slice(1, 4);
    }
    if (remaining.length > 4) {
        formatted += " " + remaining.slice(4);
    }

    input.value = prefix + formatted;
}

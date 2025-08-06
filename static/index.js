const form = document.getElementById('form'); // Merr elementin e formës nga ID-ja 'form'
const full_name = document.getElementById('full_name'); // Merr elementin e emrit të plotë nga ID-ja 'full_name'
const age = document.getElementById('age'); // Merr elementin e moshës nga ID-ja 'age'
const email = document.getElementById('email'); // Merr elementin e email-it nga ID-ja 'email'



const setError = (element, message) => { // Funksioni që vendos mesazhin error 
    const inputControl = element.parentElement; // Marrësi i prindit të elementit
    const errorDisplay = inputControl.querySelector('.error'); 

    errorDisplay.innerText = message; // Vendos tekstin e gabimit në elementin e shfaqjes
    inputControl.classList.add('error'); // E shton klasën 'error' në prindin e elementit
    inputControl.classList.remove('success'); // E hiq klasën 'success' nga prindi i elementit
};

const setSuccess = element => { // Funksioni që vendos mesazhin e sukseshëm
    const inputControl = element.parentElement; 
    const errorDisplay = inputControl.querySelector('.error'); 

    errorDisplay.innerText = ''; // Duhet të shkruhet dicka
    inputControl.classList.add('success'); // E shton klasën 'success' në prindin e elementit
    inputControl.classList.remove('error'); // E hiq klasën 'error' nga prindi i elementit
    element.value = ''; // Fshin vlerën e elementit pasi klikon "submit"
};

const isValidEmail = email => { // Funksioni që verifikon nëse një email është i vlefshëm
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    // Verifikimi i sintaksës të email-it
    return re.test(String(email).toLowerCase()); // Kthe rezultatin e verifikimit të email-it
};

  const ageInput = document.getElementById('age');

  ageInput.addEventListener('input', () => {
    const age = Number(ageInput.value);

    if (age > 20) {
      ageInput.setCustomValidity('Jeni shumë të mëdhnjë për t’u regjistruar.');
    } else if (age < 6) {
      ageInput.setCustomValidity('Jeni shumë të vegjël për t’u regjistruar.');
    } else {
      ageInput.setCustomValidity('');
    }
  });

const validateInputs = () => { // Funksioni që kontrollon fushat e inputit
    const full_nameValue = full_name.value.trim(); // Merr vlerën e emrit të plotë dhe heq hapësira të tepërta
    const emailValue = email.value.trim(); // Merr vlerën e email-it dhe heq hapësira të tepërta

    if (full_nameValue === '') { // Nëse emri është i zbrazët
        setError(full_name, "Duhet ta shkruani emrin"); // Mesazh për klikimin e josukseshëm
    } else {
        setSuccess(full_name); // Shkrimi i emrit është i vlefshëm
    }



    if (emailValue === '') { // Nëse email-i është i zbrazët
        setError(email, "Duhet ta shkruani email-in"); // Mesazh për klikimin e josukseshëm
    } else if (!isValidEmail(emailValue)) { // Nëse email-i nuk është i vlefshëm sipas verifikimit
        setError(email, "Duhet ta shkruani një email të vlefshëm"); // Mesazh për klikimin e josukseshëm
    } else {
        setSuccess(email); // Shkrimi i email-it është i vlefshëm
    }
};

const pass=document.getElementById("contraseña"),
      icon=document.querySelector(".bx")
icon.addEventListener("click", cambio =>{
    if(pass.type === "password"){
        pass.type= "text"
        icon.classList.remove('bx-show-alt')
        icon.classList.add('bx-low-vision')
    }else{
        pass.type= "password"
        icon.classList.remove('bx-low-vision')
        icon.classList.add('bx-show-alt')
    }
})
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); 
        const nombre = document.getElementById('nombre').value.trim();
        const apellido = document.getElementById('apellido').value.trim();
        const email = document.getElementById('email').value.trim();

        if (nombre === '') {
            alert('Por favor, ingresa tu nombre.');
            return;
        }

        if (apellido === '') {
            alert('Por favor, ingresa tu apellido.');
            return;
        }

        if (email === '') {
            alert('Por favor, ingresa tu correo electrónico.');
            return;
        }

        if (!validateEmail(email)) {
            alert('Por favor, ingresa un correo electrónico válido.');
            return;
        }

        if (contraseña === '') {
            alert('Por favor, ingresa tu contraseña.');
            return;
        }

        if (contraseña.length < 8) {
            alert('La contraseña debe tener al menos 8 caracteres.');
            return;
        }
o
        alert('¡Formulario enviado con éxito!');
        form.submit();
    });

    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
});

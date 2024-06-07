const checkbox = document.getElementById('check');
const btnleft = document.querySelector(".btn-left"),
      btnright =document.querySelector(".btn-right"),
       slider = document.querySelector("#slider"),
      sliderSections =document.querySelectorAll(".slider-section")

let currentIndex = 0;
// Agrega un event listener para detectar cambios en el checkbox
checkbox.addEventListener('change', function() {
    // Selecciona el elemento <ul> dentro de la navbar-left
    const navbarLeftUl = document.querySelector('.navbar-left ul');

    // Verifica si el checkbox está marcado
    if (checkbox.checked) {
        navbarLeftUl.style.right=0;
        navbarLeftUl.style.left='auto';
    } else {
        
        navbarLeftUl.style.left = ('-100%'); // Esto restaurará el color de fondo por defecto
    }
});
btnleft.addEventListener("click", e => moveToLeft());
btnright.addEventListener("click", e => moveToRight());

function moveToRight() {
    currentIndex = (currentIndex + 1) % sliderSections.length;
    updateSliderPosition();
}

function moveToLeft() {
    currentIndex = (currentIndex - 1 + sliderSections.length) % sliderSections.length;
    updateSliderPosition();
}

function updateSliderPosition() {
    const slideWidth = sliderSections[currentIndex].offsetWidth;
    const newPosition = -currentIndex * slideWidth;
    slider.style.transform = `translateX(${newPosition}px)`;
}
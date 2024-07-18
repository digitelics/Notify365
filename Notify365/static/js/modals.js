$(document).ready(function () {
    //////////////          DIAL MODAL         ///////////////////////////////


    let btnOpenNumberPad = document.getElementById('btnOpenNumberPad')
    let inputPhoneNumber = document.getElementById('phoneNumber')
    let btnDelete = document.getElementById('btnDelete')


    btnOpenNumberPad.addEventListener('click', (event) => {
        const inputModal = document.getElementById('phoneNumber');
        inputModal.focus();
        $('#modal-dial').modal('show') 
    })


    $('#btnCloseDialModal').bind('click', function () {
        $('#modal-dial').modal('hide')
    });

    $('.btnNumber').bind('click', function () {
        let text = $(this).text()
        inputPhoneNumber.value += text
    });


    btnDelete.addEventListener('click', (event) => {
        console.log('clicked', event)
        var str = inputPhoneNumber.value
        var position = inputPhoneNumber.selectionStart - 1;

        str = str.substr(0, position) + '' + str.substr(position + 1);
        inputPhoneNumber.value = str
    })

    // Variables para almacenar la posición inicial del mouse y del modal


/*------- Move modal into the screen --------*/

// Variables para almacenar la posición inicial del mouse y del modal
let initialMouseX, initialMouseY, initialModalX, initialModalY;

// Elementos del modal y su encabezado
const modal = document.getElementById("modal-dial");
const modalHeader = modal.querySelector(".modal-header");

// Función para manejar el evento de presionar el mouse en el encabezado del modal
function handleMouseDown(event) {
    // Guardar la posición inicial del mouse y del modal
    initialMouseX = event.clientX;
    initialMouseY = event.clientY;
    initialModalX = modal.offsetLeft;
    initialModalY = modal.offsetTop;
    
    // Agregar eventos para el movimiento del mouse y soltar el botón del mouse
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
}

// Función para manejar el evento de mover el mouse mientras se mantiene presionado el botón del mouse
function handleMouseMove(event) {
    // Calcular la nueva posición del modal
    let newModalX = initialModalX + event.clientX - initialMouseX;
    let newModalY = initialModalY + event.clientY - initialMouseY;

    // Establecer la posición del modal
    modal.style.left = newModalX + "px";
    modal.style.top = newModalY + "px";
}

// Función para manejar el evento de soltar el botón del mouse
function handleMouseUp() {
    // Remover los eventos de movimiento del mouse y soltar el botón del mouse
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
}

// Agregar evento de presionar el mouse en el encabezado del modal para iniciar el arrastre
modalHeader.addEventListener("mousedown", handleMouseDown);

/* ------------- definiendo caracteristicas para el input de modal dial pad  ------------ */
const inputModal = document.getElementById('phoneNumber');

inputModal.focus();
// Escuchar el evento input en el input
inputModal.addEventListener('input', function(event) {
  // Obtener el valor actual del input
  let inputValue = inputModal.value;
  
  // Eliminar cualquier carácter que no sea un número
  inputValue = inputValue.replace(/\D/g, '');

  // Limitar la longitud del valor a 10 caracteres
  inputValue = inputValue.slice(0, 10);

  // Establecer el valor limpio en el input
  inputModal.value = inputValue;
});

// Escuchar el evento de cambio de enfoque para truncar el valor si excede los 10 caracteres
inputModal.addEventListener('blur', function(event) {
  // Obtener el valor actual del input
  let inputValue = inputModal.value;

  // Limitar la longitud del valor a 10 caracteres
  inputValue = inputValue.slice(0, 10);

  // Establecer el valor truncado en el input
  inputModal.value = inputValue;
});

// Escuchar el evento focusout en el modal
modal.addEventListener('focusout', function(event) {
  // Verificar si el objetivo del evento es el modal
  if (!modal.contains(event.relatedTarget)) {
    // Establecer el foco en el input si el usuario hace clic fuera del modal
    inputModal.focus();
  }
});

});
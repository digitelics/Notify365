$(document).ready(function() {
    // Evento de clic en el botón Cancelar deal
    $(document).on('click', '.btn-cancel-deal', function() {

        // Obtener los datos del deal del atributo data
        var id = $(this).data('deal-id');  
        var code = $(this).data('code');
        var notes = $(this).data('deal-notes');
        
        $('#cancel-code').val(code);
        $('#cancel-details').val(notes);

        // Usar la URL obtenida desde el HTML y reemplazar el '0' con el ID correcto
        var actionUrl = cancelDealUrl.replace('0', id);
        $('#cancelDealForm').attr('action', actionUrl);

        // Mostrar el modal de edición
        toggleModal("cancel-modal-deal");
    });

    $('#cancel-modal-deal').on('hidden.bs.modal', function () {
        // Resetea los campos del formulario al cerrar el modal
        $('#cancelDealForm').trigger("reset");
        $('#cancel-service').html('');
        $('#cancel-provider').html('');
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('cancelDealForm');
    const cancelAmount = document.getElementById('cancel-dealamount');
    const cancelDetails = document.getElementById('cancel-details');
    

    form.addEventListener('submit', function (event) {

      // Prevent the form from submitting
      event.preventDefault();
      let isValid = true;
      resetErrorMessages();
      
      if (!cancelAmount.value.trim()) {
        setErrorFor(cancelAmount, 'This field cannot be blank.');
        isValid = false;
      } 

      if (isValid) {
        // Show loading indicator
        document.getElementById('loadingIndicator').classList.remove('hidden');
        toggleModal('cancel-modal-deal');
        // Submit the form
        form.submit();
      }
    });

    // Function to reset all error messages
    function resetErrorMessages() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(function (errorMessage) {
            errorMessage.textContent = '';
        });
    }

    // Function to set error message for a field
    function setErrorFor(input, message) {
      const formControl = input.parentElement;
      const errorMessage = formControl.querySelector('.error-message');
      errorMessage.textContent = message;
      input.classList.add('error');
    }
    
});



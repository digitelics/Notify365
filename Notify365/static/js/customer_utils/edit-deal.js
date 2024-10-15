$(document).ready(function() {
    // Evento de clic en el botón Editar deal
    $(document).on('click', '.btn-edit-deal', function() {
        // Obtener los datos del deal del atributo data
        var id = $(this).data('deal-id');  
        var code = $(this).data('code');
        var premium = $(this).data('deal-premium');
        var product = $(this).data('deal-product');
        var provider = $(this).data('deal-provider');
        var type = $(this).data('deal-type');
        var activation = $(this).data('deal-activation');
        var periodo = $(this).data('deal-periodo');
        var notes = $(this).data('deal-notes');

         // Usar la URL obtenida desde el HTML y reemplazar el '0' con el ID correcto
         var actionUrl = updateDealUrl.replace('0', id);
         console.log(activation)
         $('#editDealForm').attr('action', actionUrl);

        // Realizar la solicitud AJAX para obtener los datos completos del deal
        $.ajax({
            url: '/customers/get/services-providers',  // Reemplaza con la URL correcta para obtener los datos del deal
            method: 'GET',
            success: function(data) {
                // Rellenar los campos del formulario con los datos del deal

                // Primero vacía las opciones del select
                $('#edit-service').html('');  
                $('#edit-provider').html('');

                // Asegúrate de que las opciones están cargadas antes de asignar los valores
                data.services.forEach(function(service) {
                    $('#edit-service').append(new Option(service.name, service.id));
                });

                data.providers.forEach(function(provider) {
                    $('#edit-provider').append(new Option(provider.provider, provider.id));
                });

                // Luego asigna el valor seleccionado
                $('#edit-service').val(product).change();
                $('#edit-provider').val(provider).change();

                // Actualiza los demás campos
                $('#edit-code').val(code);
                $('#edit-dealamount').val(premium);
                if (activation) {
                    const formattedDate = new Date(activation).toISOString().split('T')[0];
                    document.getElementById('edit-date').value = formattedDate;
                } else {
                    console.log("Activation date is invalid or null.");
                    $('#edit-date').val('');  // Deja el campo vacío si no hay fecha válida
                }
                if (type == null) {
                    console.log('entro')
                    type = "-- Select -- ";
                }
                $('#edit-type').val(type).change();
                if (periodo == null) {
                    periodo = "-- Select -- ";
                }
                $('#edit-activation_true').val(periodo).change();
                $('#edit-details').val(notes);

                // Mostrar el modal de edición
                toggleModal("update-deal-modal");
            },
            error: function(error) {
                console.log('Error obteniendo los datos del deal:', error);
            }
        });
    });

    $('#update-deal-modal').on('hidden.bs.modal', function () {
        // Resetea los campos del formulario al cerrar el modal
        $('#editDealForm').trigger("reset");
        $('#edit-service').html('');
        $('#edit-provider').html('');
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('editDealForm');
    const cancelAmount = document.getElementById('cancel-dealamount');
    const cancelDetails = document.getElementById('cancel-details');
   
    const editCode = document.getElementById('edit-code');
    const editPremium = document.getElementById('edit-dealamount');
    const editType = document.getElementById('edit-type');
    const editActivation = document.getElementById('edit-activation-date');
    const editPeriodo = document.getElementById('edit-activation_true');
    

    form.addEventListener('submit', function (event) {

      // Prevent the form from submitting
      event.preventDefault();
      let isValid = true;
      resetErrorMessages();
      
      if (!editCode.value.trim()) {
        setErrorFor(editCode, 'This field cannot be blank.');
        isValid = false;
      } 

      if (!editPremium.value.trim()) {
        setErrorFor(editPremium, 'This field cannot be blank.');
        isValid = false;
      } 


      if (editType.value.trim() == '-- Select --' || editType.value.trim() == '' ) {
        setErrorFor(editType, 'This field cannot be blank.');
        isValid = false;
      } 

      if (editPeriodo.value.trim() == '-- Select --' || editPeriodo.value.trim() == '') {
        setErrorFor(editPeriodo, 'This field cannot be blank.');
        isValid = false;
      } 

      if (isValid) {
        // Show loading indicator
        document.getElementById('loadingIndicator').classList.remove('hidden');
        toggleModal('update-deal-modal');
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

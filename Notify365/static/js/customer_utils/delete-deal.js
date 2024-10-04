$(document).ready(function() {
    // Evento de clic en el botón Cancelar deal
    $(document).on('click', '.btn-delete-deal', function() {
        // Obtener los datos del deal del atributo data
        var id = $(this).data('deal-id');

        // Usar la URL obtenida desde el HTML y reemplazar el '0' con el ID correcto
        var actionUrl = deleteDealUrl.replace('0', id);
        $('#deleteDealForm').attr('action', actionUrl);

        // Mostrar el modal de edición
        toggleModal("modal-delete-deal");
    });

    $('#modal-delete-deal').on('hidden.bs.modal', function () {
        // Resetea los campos del formulario al cerrar el modal
        $('#deleteDealForm').trigger("reset");
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('deleteDealForm');

    form.addEventListener('submit', function (event) {
        // Prevent the form from submitting
        event.preventDefault();
        let isValid = true;

        if (isValid) {
            // Mostrar indicador de carga si existe
            var loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.classList.remove('hidden');
            }
            form.submit();
            toggleModal('modal-delete-deal');
            // Submit the form
            
        }
    });
});

// Función para alternar la visibilidad del modal
function toggleModal(modalID) {
    var modal = document.getElementById(modalID);
    if (modal) {
        if (modal.classList.contains("hidden")) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        } else {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
        }
    } else {
        console.log("Modal with ID " + modalID + " not found.");
    }
}

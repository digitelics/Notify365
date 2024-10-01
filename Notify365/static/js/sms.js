document.addEventListener('DOMContentLoaded', function() {
    let page = 1;  // Página inicial
    let loading = false;  // Estado de carga
    let hasNextPage = true;  // Suponemos que hay más páginas al inicio
    let friends = {
        list: document.querySelector('ul.people'),
        all: document.querySelectorAll('.left .person'),
        name: ''
    },
    chat = {
        container: document.querySelector('.chat-container'),
        current: null,
        person: null,
        name: document.querySelector('.container .right .top .name')
    }
  
    // Función para cargar más clientes con AJAX (scroll infinito)
    function loadMoreCustomers() {
        if (loading || !hasNextPage) return;

        loading = true;
        page += 1;  // Incrementamos la página a cargar

        // Mostrar el mensaje de "Cargando"
        document.getElementById('loading').style.display = 'block';

        // Realizamos la solicitud AJAX para cargar más clientes
        $.ajax({
            url: '?page=' + page,
            type: 'GET',
            success: function(response) {
                document.getElementById('loading').style.display = 'none';  // Ocultamos el mensaje de carga

                if (response.html) {
                    // Agregar los nuevos clientes al final de la lista
                    document.getElementById('customerList').insertAdjacentHTML('beforeend', response.html);

                    // Actualizar los elementos de la lista de clientes
                    updateFriendsList();
                }

                // Comprobar si hay más páginas
                hasNextPage = response.has_next;
                loading = false;
            },
            error: function(xhr, status, error) {
                console.error('Error loading more customers:', error);
                document.getElementById('loading').style.display = 'none';
                loading = false;
            }
        });
    }

  
    // Actualizar la lista de "person" después de cargar más clientes
    function updateFriendsList() {
        friends.all = document.querySelectorAll('.left .person');

        friends.all.forEach(f => {
            f.addEventListener('mousedown', () => {
                if (!f.classList.contains('active')) {
                    setActiveChat(f);
                }
            });
        });
    }
  
    // Configurar el chat activo
    function setActiveChat(f) {
        let activeChat = friends.list.querySelector('.active');
        if (activeChat) {
            activeChat.classList.remove('active');
        }
        f.classList.add('active');
  
        if (chat.current) {
            chat.current.classList.remove('active-chat');
        }
  
        chat.person = f.getAttribute('data-chat');
        chat.current = chat.container.querySelector('[data-chat="' + chat.person + '"]');
        chat.current.classList.add('active-chat');
  
        friends.name = f.querySelector('.name').innerText;
        chat.name.innerHTML = friends.name;
  
        // Actualizar el input oculto con el ID del cliente seleccionado
        document.getElementById('customer-id').value = f.getAttribute('data-id');
    }
  
    // Enviar mensajes con AJAX
    document.getElementById('send-message-form').addEventListener('submit', function(e) {
        e.preventDefault();  // Prevenir la acción por defecto del formulario
  
        var messageText = document.getElementById('message-text').value;
        var fileInput = document.getElementById('dropzone-file');
        var errorMessage = document.getElementById('error-message');
        var file = fileInput.files[0];
  
        if (file && file.size > 2 * 1024 * 1024) { // Límite de 2 MB
            errorMessage.textContent = 'Attached file size should not exceed 2 MB';
            errorMessage.style.display = 'block';
            return;
        } else {
            errorMessage.style.display = 'none';
        }
  
        if (messageText.trim() === '') {
            alert('Please enter a message');
            return;
        }
  
        // Enviar el formulario por AJAX
        let formData = new FormData(this);
        $.ajax({
            url: this.action,
            type: this.method,
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Limpiar el campo de texto y el archivo adjunto
                document.getElementById('message-text').value = '';
                document.getElementById('dropzone-file').value = '';
                document.getElementById('file-name').textContent = '';
  
                // Actualizar los mensajes del chat
                let chatContainer = document.querySelector('.chat-container');
                let activeChat = chatContainer.querySelector('.active-chat');
                if (chatContainer && activeChat) {
                  activeChat.innerHTML = response.html;
                }
  
                // Hacer scroll hacia abajo en el chat
                scrollToBottom();
            },
            error: function(xhr, status, error) {
                console.error('Message send failed:', error);
            }
        });
    });
  
    // Mostrar el nombre del archivo seleccionado
    document.getElementById('dropzone-file').addEventListener('change', function() {
        var fileName = this.files[0] ? this.files[0].name : '';
        document.getElementById('file-name').textContent = fileName;
    });
  
    // Función para hacer scroll hacia abajo en el chat
    function scrollToBottom() {
        let activeChat = document.querySelector('.chat-container .active-chat');
        if (activeChat) {
            activeChat.scrollTop = activeChat.scrollHeight;
        }
    }
  
    // Filtrar la lista de amigos al buscar
    document.getElementById('searchInput').addEventListener('keyup', function() {
        let filter = this.value.toLowerCase();
        friends.all.forEach(function(f) {
            let name = f.querySelector('.name').innerText.toLowerCase();
            if (name.includes(filter)) {
                f.style.display = '';
            } else {
                f.style.display = 'none';
            }
        });
    });
  
    document.querySelector('#customer-panel').addEventListener('scroll', function() {
        if (this.scrollTop + this.clientHeight >= this.scrollHeight && !loading) {
            loadMoreCustomers();  // Cargar más clientes si se llega al final
        }
    });

  
    updateFriendsList();  // Inicializar la lista de amigos
  });
  
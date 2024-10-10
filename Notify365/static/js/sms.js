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
    };

    const chats = document.querySelectorAll('.chat');
    chats.forEach(chat => {
        chat.addEventListener('click', function () {
            chats.forEach(c => c.classList.remove('active-chat')); // Remover la clase 'active-chat' de todos los elementos
            this.classList.add('active-chat'); // Agregar la clase 'active-chat' solo al elemento seleccionado
        });
    });

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

                if (response.customers_html) {
                    document.getElementById('customerList').insertAdjacentHTML('beforeend', response.customers_html);
                    updateFriendsList();
                }

                if (response.chats_html) {
                    document.getElementById('chat-container').insertAdjacentHTML('beforeend', response.chats_html);
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
        if (chat.current) {
            chat.current.classList.add('active-chat');
        }
    
        friends.name = f.querySelector('.name').innerText;
        chat.name.innerHTML = friends.name;
    
        document.getElementById('customer-id').value = f.getAttribute('data-id'); // Actualizar el input oculto con el ID del cliente seleccionado
    }
  
    // Función para hacer scroll hacia abajo en el chat
    function scrollToBottom() {
        let activeChat = document.querySelector('.chat-container .active-chat');
        if (activeChat) {
            activeChat.scrollTop = activeChat.scrollHeight;
        }
    }

    // Mostrar el nombre del archivo seleccionado
    document.getElementById('dropzone-file').addEventListener('change', function() {
        var fileName = this.files[0] ? this.files[0].name : '';
        document.getElementById('file-name').textContent = fileName;
    });
  
    // Cargar más clientes cuando se hace scroll al final del panel de clientes
    document.querySelector('#customer-panel').addEventListener('scroll', function() {
        if (this.scrollTop + this.clientHeight >= this.scrollHeight && !loading) {
            loadMoreCustomers();  // Cargar más clientes si se llega al final
        }
    });
  
    updateFriendsList();  // Inicializar la lista de amigos
});

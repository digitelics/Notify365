document.addEventListener('DOMContentLoaded', function() {
  const menulinks = document.getElementsByClassName("sms"); 
  for (let i = 0; i < menulinks.length; i++) {
      menulinks[i].className += " main-menu-selected";
  }

  let friends = {
      list: document.querySelector('ul.people'),
      all: document.querySelectorAll('.left .person'),
      name: ''
  },
  chat = {
      container: document.querySelector('.container .right'),
      current: null,
      person: null,
      name: document.querySelector('.container .right .top .name')
  }

  friends.all.forEach(f => {
      f.addEventListener('mousedown', () => {
          if (!f.classList.contains('active')) {
              setActiveChat(f);
          }
      })
  });

  function setActiveChat(f) {
      let activeChat = friends.list.querySelector('.active');
      if (activeChat) {
          activeChat.classList.remove('active');
      }
      f.classList.add('active');
      
      if (chat.current) {
          chat.current.classList.remove('active-chat');
          chat.current.style.display = 'none';
      }
      
      chat.person = f.getAttribute('data-chat');
      chat.current = chat.container.querySelector('[data-chat="' + chat.person + '"]');
      chat.current.classList.add('active-chat');
      chat.current.style.display = 'flex';
      
      friends.name = f.querySelector('.name').innerText;
      chat.name.innerHTML = friends.name;

      // Update hidden input with selected customer ID
      document.getElementById('customer-id').value = f.getAttribute('data-id');
  }

  document.getElementById('send-message-form').addEventListener('submit', function(e) {
      e.preventDefault(); // Prevent the default form submission

      var messageText = document.getElementById('message-text').value;
      if (messageText.trim() === '') {
          alert('Please enter a message');
          return;
      }

      // If everything is OK, submit the form
      this.submit();
  });

  // Display the name of the selected file
  document.getElementById('dropzone-file').addEventListener('change', function() {
      var fileName = this.files[0] ? this.files[0].name : '';
      document.getElementById('file-name').textContent = fileName;
  });

  // Si hay un cliente seleccionado al cargar la página, activar el chat correspondiente
  var selectedCustomer = document.querySelector('.person.active');
  if (selectedCustomer) {
      selectedCustomer.click();
  }
});

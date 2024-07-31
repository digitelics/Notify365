document.addEventListener('DOMContentLoaded', function() {
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

  friends.all.forEach(f => {
      f.addEventListener('mousedown', () => {
          if (!f.classList.contains('active')) {
              setActiveChat(f);
          }
      });
  });

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
});

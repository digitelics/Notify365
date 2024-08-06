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
        var fileInput = document.getElementById('dropzone-file');
        var errorMessage = document.getElementById('error-message');
        var file = fileInput.files[0];

        if (file && file.size > 2 * 1024 * 1024) { // 2 MB limit
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

      // If everything is OK, submit the form via AJAX
      let formData = new FormData(this);
      $.ajax({
          url: this.action,
          type: this.method,
          data: formData,
          processData: false,
          contentType: false,
          success: function(response) {
              // Clear the input field and file input
              document.getElementById('message-text').value = '';
              document.getElementById('dropzone-file').value = '';
              document.getElementById('file-name').textContent = '';

              // Update the chat messages
              let chatContainer = document.querySelector('.chat-container');
              let activeChat = chatContainer.querySelector('.active-chat');
              if (chatContainer && activeChat) {
                activeChat.innerHTML = response.html;
              }
              

              // Scroll to the bottom of the chat container
              scrollToBottom();
          },
          error: function(xhr, status, error) {
              console.error('Message send failed:', error);
          }
      });
  });

  // Display the name of the selected file
  document.getElementById('dropzone-file').addEventListener('change', function() {
      var fileName = this.files[0] ? this.files[0].name : '';
      document.getElementById('file-name').textContent = fileName;
  });

  function scrollToBottom() {
      let activeChat = document.querySelector('.chat-container .active-chat');
      if (activeChat) {
          activeChat.scrollTop = activeChat.scrollHeight;
      }
  }

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
});

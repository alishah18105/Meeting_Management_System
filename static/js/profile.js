document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById('togglePw');
    const pwField = document.getElementById('pwField');
    if (toggle) {
      toggle.addEventListener('click', function() {
        if (pwField.type === 'password') {
          pwField.type = 'text';
          toggle.textContent = 'Hide';
        } else {
          pwField.type = 'password';
          toggle.textContent = 'Show';
        }
      });
    }
  });
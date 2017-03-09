(function() {
  var notifications = document.querySelectorAll('.notification');
  notifications.forEach(notification => {
    var deleteButton = notification.querySelector('.delete');
    deleteButton.addEventListener('click', function() {
      notification.outerHTML = '';
    });
  });
})();
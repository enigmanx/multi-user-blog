
// NOTIFICATIONS
(function() {
  var notifications = document.querySelectorAll('.notification');
  notifications.forEach(notification => {
    var deleteButton = notification.querySelector('.delete');
    deleteButton.addEventListener('click', function() {
      notification.outerHTML = '';
    });
  });
})();

// INLINE EDITABLE
(function() {
  var inlineEditables = document.querySelectorAll('.inline-editable');
  inlineEditables.forEach(inlineEditable => {
    var editButton = inlineEditable.querySelector('.inline-editable__edit');
    editButton.addEventListener('click', function() {
      inlineEditable.classList.add('is-editing');
    });
    var cancelButton = inlineEditable.querySelector('.inline-editable__cancel');
    cancelButton.addEventListener('click', function() {
      inlineEditable.classList.remove('is-editing');
    });
  });
})();
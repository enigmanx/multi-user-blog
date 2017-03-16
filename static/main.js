
// NOTIFICATIONS
(function() {
  var notifications = document.querySelectorAll('.notification');
  notifications.forEach(notification => {
    var deleteButton = notification.querySelector('.delete');
    deleteButton.addEventListener('click', function() {
      notification.parentNode.outerHTML = '';
    });
    setTimeout(function() {
      notification.parentNode.outerHTML = '';
    }, 5000);
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

// RESTORE SCROLL AFTER POSTS
(function() {

  function getScrollXY() {
    var x = 0, y = 0;
    if( typeof( window.pageYOffset ) == 'number' ) {
      // Netscape
      x = window.pageXOffset;
      y = window.pageYOffset;
    } else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
      // DOM
      x = document.body.scrollLeft;
      y = document.body.scrollTop;
    } else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
      // IE6 standards compliant mode
      x = document.documentElement.scrollLeft;
      y = document.documentElement.scrollTop;
    }
    return { x: x, y: y };
  }

  function restorePosition() {
    try {
      var s = JSON.parse(localStorage.getItem('MultiUserBlog_offset'));
      window.scrollTo(s.x, s.y);
    } catch(e) {};
    localStorage.removeItem('MultiUserBlog_offset');
  }

  function recordPosition() {
    var s = getScrollXY()
    localStorage.setItem('MultiUserBlog_offset', JSON.stringify(s));
  }

  var forms = document.querySelectorAll('form');
  forms.forEach(function(form) {
    form.onsubmit = function() {
      recordPosition();
      form.submit();
    }
  });

  window.addEventListener('DOMContentLoaded', function() {
    restorePosition();
  });

})();
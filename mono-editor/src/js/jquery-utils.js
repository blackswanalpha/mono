// jQuery utility functions for Mono Editor

// Initialize jQuery utilities
const MonoJQueryUtils = {
  // Initialize tooltips
  initTooltips: function() {
    try {
      if (typeof $.fn.tooltip === 'function') {
        $('[title]').tooltip({
          placement: 'bottom',
          trigger: 'hover',
          container: 'body'
        });
      } else {
        console.warn('Bootstrap tooltip plugin not available');
        // Add a simple title attribute handler
        $('[title]').each(function() {
          const $el = $(this);
          const title = $el.attr('title');
          if (title) {
            $el.on('mouseenter', function() {
              console.log('Showing title:', title);
            });
          }
        });
      }
    } catch (error) {
      console.error('Error initializing tooltips:', error);
    }
  },

  // Initialize popovers
  initPopovers: function() {
    try {
      if (typeof $.fn.popover === 'function') {
        $('[data-toggle="popover"]').popover({
          container: 'body',
          trigger: 'hover'
        });
      } else {
        console.warn('Bootstrap popover plugin not available');
      }
    } catch (error) {
      console.error('Error initializing popovers:', error);
    }
  },

  // Show a loading spinner on a button
  showButtonSpinner: function($button, text = 'Loading...') {
    const originalContent = $button.html();
    $button.data('original-content', originalContent);
    $button.html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${text}`);
    $button.prop('disabled', true);
    return originalContent;
  },

  // Restore button content after loading
  restoreButton: function($button) {
    const originalContent = $button.data('original-content');
    if (originalContent) {
      $button.html(originalContent);
    }
    $button.prop('disabled', false);
  },

  // Show a status message
  showStatusMessage: function(message, type = 'info', duration = 5000) {
    const $statusBar = $('.status-left');
    if (!$statusBar.length) return;

    let $statusElement = $('#editor-status-message');
    if (!$statusElement.length) {
      $statusElement = $('<span>', {
        id: 'editor-status-message'
      });
      $statusBar.append($statusElement);
    }

    // Set message and style based on type
    $statusElement.text(message);
    $statusElement.removeClass(); // Clear previous classes
    $statusElement.addClass(`status-message status-${type}`);

    // Set color based on type
    const colors = {
      error: '#F44336',
      warning: '#FFC107',
      success: '#4CAF50',
      info: '#2196F3'
    };

    $statusElement.css('color', colors[type] || colors.info);

    // Remove the status after a delay
    setTimeout(() => {
      $statusElement.fadeOut(300, function() {
        $(this).remove();
      });
    }, duration);
  },

  // Show an error message
  showError: function(message, error, isCritical = false) {
    console.error(message, error);

    // Show in status bar
    const statusMessage = `${message}: ${error.message || 'Unknown error'}`;
    this.showStatusMessage(statusMessage, 'error');

    // Show modal for critical errors
    if (isCritical) {
      if ($('#error-modal').length) {
        $('#error-modal-title').text('Error');
        $('#error-modal-body').text(statusMessage);

        // Check which Bootstrap version is being used
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          // Bootstrap 5
          const modalElement = document.getElementById('error-modal');
          const modalInstance = new bootstrap.Modal(modalElement);
          modalInstance.show();
        } else if (typeof $.fn.modal === 'function') {
          // Bootstrap 4 or 3
          $('#error-modal').modal('show');
        } else {
          // Fallback if modal function is not available
          alert(statusMessage);
        }
      } else {
        alert(statusMessage);
      }
    }
  },

  // Create error modal if it doesn't exist
  createErrorModal: function() {
    if ($('#error-modal').length === 0) {
      const modalHTML = `
        <div class="modal fade" id="error-modal" tabindex="-1" role="dialog" aria-labelledby="error-modal-title" aria-hidden="true">
          <div class="modal-dialog" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="error-modal-title">Error</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body" id="error-modal-body">
                An error occurred.
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
      `;

      $('body').append(modalHTML);
    }
  },

  // Initialize all jQuery utilities
  init: function() {
    try {
      console.log('Initializing jQuery utilities...');

      // Check if jQuery is available
      if (typeof window.jQuery === 'undefined') {
        console.error('jQuery is not available. Cannot initialize utilities.');
        return;
      }

      // Initialize components
      this.initTooltips();
      this.initPopovers();
      this.createErrorModal();

      // Add Bootstrap classes to existing elements
      try {
        $('.dialog').addClass('modal-content');
        $('.dialog-header').addClass('modal-header');
        $('.dialog-content').addClass('modal-body');
        $('.dialog-footer').addClass('modal-footer');
        $('.dialog-btn').addClass('btn');
        $('.dialog-btn-primary').addClass('btn-primary');
      } catch (error) {
        console.error('Error adding Bootstrap classes:', error);
      }

      console.log('jQuery utilities initialized successfully');
    } catch (error) {
      console.error('Error initializing jQuery utilities:', error);
    }
  }
};

// Define a safe initialization function
function initMonoJQueryUtils() {
  try {
    // Check if jQuery is available
    if (typeof window.jQuery !== 'undefined') {
      console.log('jQuery is available, initializing utilities');
      // Initialize when document is ready
      $(document).ready(function() {
        try {
          MonoJQueryUtils.init();
        } catch (error) {
          console.error('Error in MonoJQueryUtils.init():', error);
        }
      });
    } else {
      console.error('jQuery is not available, delaying initialization');
      // Try again after a delay
      setTimeout(initMonoJQueryUtils, 1000);
    }
  } catch (error) {
    console.error('Error in initMonoJQueryUtils:', error);
  }
}

// Start initialization
initMonoJQueryUtils();

// Export the utilities
window.MonoJQueryUtils = MonoJQueryUtils;

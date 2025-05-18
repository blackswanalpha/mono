/**
 * Switch UI Kit JavaScript
 */

// Initialize the UI Kit
(function() {
    // Create the UI Kit namespace
    window.SwitchUIKit = {
        // Toast notifications
        toast: {
            // Create a new toast
            create: function(options) {
                const defaults = {
                    title: '',
                    message: 'This is a toast notification',
                    type: 'info',
                    position: 'top-right',
                    autoClose: true,
                    duration: 5000,
                    showProgress: true,
                    showIcon: true,
                    showCloseButton: true,
                    onClose: null
                };
                
                // Merge options with defaults
                const settings = Object.assign({}, defaults, options);
                
                // Create the toast element
                const toast = document.createElement('div');
                toast.className = `toast toast-${settings.type} toast-${settings.position}`;
                
                // Create the toast content
                let html = '';
                
                // Add icon
                if (settings.showIcon) {
                    let iconClass = '';
                    switch (settings.type) {
                        case 'info':
                            iconClass = 'info-circle';
                            break;
                        case 'success':
                            iconClass = 'check-circle';
                            break;
                        case 'warning':
                            iconClass = 'exclamation-triangle';
                            break;
                        case 'error':
                            iconClass = 'exclamation-circle';
                            break;
                    }
                    html += `<div class="toast-icon"><i class="bi bi-${iconClass}"></i></div>`;
                }
                
                // Add content
                html += `<div class="toast-content">`;
                if (settings.title) {
                    html += `<div class="toast-title">${settings.title}</div>`;
                }
                html += `<div class="toast-message">${settings.message}</div>`;
                html += `</div>`;
                
                // Add close button
                if (settings.showCloseButton) {
                    html += `<button class="toast-close"><i class="bi bi-x"></i></button>`;
                }
                
                // Add progress bar
                if (settings.showProgress && settings.autoClose) {
                    html += `<div class="toast-progress-container">
                        <div class="toast-progress-bar" style="width: 100%"></div>
                    </div>`;
                }
                
                // Set the HTML
                toast.innerHTML = html;
                
                // Add the toast to the document
                document.body.appendChild(toast);
                
                // Get the progress bar
                const progressBar = toast.querySelector('.toast-progress-bar');
                
                // Auto close timer
                let autoCloseTimer = null;
                let progressTimer = null;
                
                // Function to close the toast
                const closeToast = function() {
                    // Add the hidden class
                    toast.classList.add('toast-hidden');
                    
                    // Remove the toast after the animation
                    setTimeout(function() {
                        if (toast.parentNode) {
                            toast.parentNode.removeChild(toast);
                        }
                    }, 300);
                    
                    // Clear timers
                    if (autoCloseTimer) {
                        clearTimeout(autoCloseTimer);
                    }
                    
                    if (progressTimer) {
                        clearInterval(progressTimer);
                    }
                    
                    // Call the onClose callback
                    if (typeof settings.onClose === 'function') {
                        settings.onClose();
                    }
                };
                
                // Add event listener to close button
                const closeButton = toast.querySelector('.toast-close');
                if (closeButton) {
                    closeButton.addEventListener('click', closeToast);
                }
                
                // Auto close
                if (settings.autoClose) {
                    autoCloseTimer = setTimeout(closeToast, settings.duration);
                    
                    // Update progress bar
                    if (settings.showProgress && progressBar) {
                        const startTime = Date.now();
                        const duration = settings.duration;
                        
                        progressTimer = setInterval(function() {
                            const elapsed = Date.now() - startTime;
                            const progress = Math.max(0, 100 - (elapsed / duration) * 100);
                            
                            progressBar.style.width = progress + '%';
                            
                            if (progress <= 0) {
                                clearInterval(progressTimer);
                            }
                        }, 30);
                    }
                }
                
                // Pause auto close on hover
                toast.addEventListener('mouseenter', function() {
                    if (settings.autoClose) {
                        clearTimeout(autoCloseTimer);
                        
                        if (progressTimer) {
                            clearInterval(progressTimer);
                        }
                    }
                });
                
                // Resume auto close on mouse leave
                toast.addEventListener('mouseleave', function() {
                    if (settings.autoClose) {
                        autoCloseTimer = setTimeout(closeToast, settings.duration);
                        
                        if (settings.showProgress && progressBar) {
                            const startTime = Date.now();
                            const duration = settings.duration;
                            const currentWidth = parseFloat(progressBar.style.width) || 100;
                            const remainingTime = (currentWidth / 100) * duration;
                            
                            progressTimer = setInterval(function() {
                                const elapsed = Date.now() - startTime;
                                const progress = Math.max(0, currentWidth - (elapsed / remainingTime) * currentWidth);
                                
                                progressBar.style.width = progress + '%';
                                
                                if (progress <= 0) {
                                    clearInterval(progressTimer);
                                }
                            }, 30);
                        }
                    }
                });
                
                // Return the toast element
                return toast;
            },
            
            // Show an info toast
            info: function(message, title, options) {
                return this.create(Object.assign({}, options, {
                    type: 'info',
                    message: message,
                    title: title || 'Information'
                }));
            },
            
            // Show a success toast
            success: function(message, title, options) {
                return this.create(Object.assign({}, options, {
                    type: 'success',
                    message: message,
                    title: title || 'Success'
                }));
            },
            
            // Show a warning toast
            warning: function(message, title, options) {
                return this.create(Object.assign({}, options, {
                    type: 'warning',
                    message: message,
                    title: title || 'Warning'
                }));
            },
            
            // Show an error toast
            error: function(message, title, options) {
                return this.create(Object.assign({}, options, {
                    type: 'error',
                    message: message,
                    title: title || 'Error'
                }));
            }
        },
        
        // Splash screen
        splashScreen: {
            // Create a splash screen
            create: function(options) {
                const defaults = {
                    logo: '',
                    title: 'My App',
                    subtitle: 'Loading...',
                    duration: 3000,
                    theme: 'light',
                    animation: 'fade',
                    onFinish: null,
                    showProgress: false,
                    progressDuration: 2500
                };
                
                // Merge options with defaults
                const settings = Object.assign({}, defaults, options);
                
                // Create the splash screen element
                const splashScreen = document.createElement('div');
                splashScreen.className = `splash-screen splash-screen-${settings.theme} splash-screen-animation-${settings.animation}`;
                
                // Create the splash screen content
                let html = `<div class="splash-screen-content">`;
                
                // Add logo
                html += `<div class="splash-screen-logo-container">`;
                if (settings.logo) {
                    html += `<img src="${settings.logo}" alt="${settings.title}" class="splash-screen-logo">`;
                } else {
                    html += `<div class="splash-screen-logo-placeholder">
                        <i class="bi bi-code-slash"></i>
                    </div>`;
                }
                html += `</div>`;
                
                // Add title and subtitle
                html += `<h1 class="splash-screen-title">${settings.title}</h1>`;
                html += `<p class="splash-screen-subtitle">${settings.subtitle}</p>`;
                
                // Add progress bar
                if (settings.showProgress) {
                    html += `<div class="splash-screen-progress-container">
                        <div class="splash-screen-progress-bar" style="width: 0%"></div>
                    </div>`;
                }
                
                html += `</div>`;
                
                // Set the HTML
                splashScreen.innerHTML = html;
                
                // Add the splash screen to the document
                document.body.appendChild(splashScreen);
                
                // Get the progress bar
                const progressBar = splashScreen.querySelector('.splash-screen-progress-bar');
                
                // Progress animation
                let progressTimer = null;
                
                if (settings.showProgress && progressBar) {
                    const startTime = Date.now();
                    const duration = settings.progressDuration;
                    
                    progressTimer = setInterval(function() {
                        const elapsed = Date.now() - startTime;
                        const progress = Math.min(100, (elapsed / duration) * 100);
                        
                        progressBar.style.width = progress + '%';
                        
                        if (progress >= 100) {
                            clearInterval(progressTimer);
                        }
                    }, 30);
                }
                
                // Hide the splash screen after the specified duration
                setTimeout(function() {
                    // Add the hidden class
                    splashScreen.classList.add('splash-screen-hidden');
                    
                    // Clear progress timer
                    if (progressTimer) {
                        clearInterval(progressTimer);
                    }
                    
                    // Remove the splash screen after the animation
                    setTimeout(function() {
                        if (splashScreen.parentNode) {
                            splashScreen.parentNode.removeChild(splashScreen);
                        }
                        
                        // Call the onFinish callback
                        if (typeof settings.onFinish === 'function') {
                            settings.onFinish();
                        }
                    }, 500);
                }, settings.duration);
                
                // Return the splash screen element
                return splashScreen;
            }
        }
    };
    
    // Initialize when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Switch UI Kit initialized');
    });
})();

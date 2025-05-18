/**
 * Switch Components Bundle
 *
 * This file bundles all the Switch components for easy inclusion.
 */

// Create the SwitchComponents namespace
window.SwitchComponents = window.SwitchComponents || {};

// Load the components
document.addEventListener('DOMContentLoaded', function() {
    // Basic components
    const buttonScript = document.createElement('script');
    buttonScript.src = '/switch/components/button.js';
    document.head.appendChild(buttonScript);

    const cardScript = document.createElement('script');
    cardScript.src = '/switch/components/card.js';
    document.head.appendChild(cardScript);

    const formScript = document.createElement('script');
    formScript.src = '/switch/components/form.js';
    document.head.appendChild(formScript);

    // New components
    const tableScript = document.createElement('script');
    tableScript.src = '/switch/components/table.js';
    document.head.appendChild(tableScript);

    const modalScript = document.createElement('script');
    modalScript.src = '/switch/components/modal.js';
    document.head.appendChild(modalScript);

    const tabsScript = document.createElement('script');
    tabsScript.src = '/switch/components/tabs.js';
    document.head.appendChild(tabsScript);

    const alertScript = document.createElement('script');
    alertScript.src = '/switch/components/alert.js';
    document.head.appendChild(alertScript);

    const dropdownScript = document.createElement('script');
    dropdownScript.src = '/switch/components/dropdown.js';
    document.head.appendChild(dropdownScript);

    console.log('Switch components loaded');
});

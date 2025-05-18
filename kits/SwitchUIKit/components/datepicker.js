/**
 * Switch UI Kit - DatePicker Component
 * 
 * A customizable date picker component for the Switch UI Kit.
 */

(function(global) {
    'use strict';
    
    // Create the SwitchUIKit namespace if it doesn't exist
    global.SwitchUIKit = global.SwitchUIKit || {};
    
    // Create the Components namespace if it doesn't exist
    global.SwitchUIKit.Components = global.SwitchUIKit.Components || {};
    
    // Create the SwitchComponents namespace for easier access
    global.SwitchComponents = global.SwitchComponents || {};
    
    /**
     * DatePicker Component
     */
    class DatePicker {
        /**
         * Create a new DatePicker
         * @param {Object} options - DatePicker options
         * @returns {DatePicker} - The DatePicker instance
         */
        constructor(options = {}) {
            // Default options
            this.options = Object.assign({
                value: new Date(),
                min: null,
                max: null,
                format: 'yyyy-mm-dd',
                placeholder: 'Select a date',
                disabled: false,
                readonly: false,
                required: false,
                name: '',
                id: `switch-datepicker-${Math.random().toString(36).substr(2, 9)}`,
                onChange: null,
                attributes: {}
            }, options);
            
            // State
            this.isOpen = false;
            this.currentMonth = this.options.value ? new Date(this.options.value) : new Date();
            this.currentMonth.setDate(1); // Set to first day of month
            
            // Create the element
            this.element = this._createElement();
            this.calendarElement = this._createCalendarElement();
            
            // Attach event listeners
            this._attachEventListeners();
            
            return this;
        }
        
        /**
         * Create the date picker element
         * @returns {HTMLElement} - The date picker element
         * @private
         */
        _createElement() {
            // Create the container
            const container = document.createElement('div');
            container.classList.add('switch-datepicker');
            container.setAttribute('id', this.options.id);
            
            // Create the input group
            const inputGroup = document.createElement('div');
            inputGroup.classList.add('switch-datepicker-input-group');
            
            // Create the input
            const input = document.createElement('input');
            input.type = 'text';
            input.classList.add('switch-datepicker-input');
            input.placeholder = this.options.placeholder;
            input.readOnly = true; // Always readonly to prevent direct editing
            input.disabled = this.options.disabled;
            input.required = this.options.required;
            
            if (this.options.name) {
                input.name = this.options.name;
            }
            
            // Set the initial value
            if (this.options.value) {
                input.value = this._formatDate(this.options.value);
            }
            
            // Add custom attributes
            if (this.options.attributes) {
                for (const [key, value] of Object.entries(this.options.attributes)) {
                    input.setAttribute(key, value);
                }
            }
            
            // Create the calendar icon
            const calendarIcon = document.createElement('span');
            calendarIcon.classList.add('switch-datepicker-icon');
            calendarIcon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
            `;
            
            // Add elements to the input group
            inputGroup.appendChild(input);
            inputGroup.appendChild(calendarIcon);
            
            // Add input group to the container
            container.appendChild(inputGroup);
            
            // Store references
            this.container = container;
            this.input = input;
            this.calendarIcon = calendarIcon;
            
            return container;
        }
        
        /**
         * Create the calendar element
         * @returns {HTMLElement} - The calendar element
         * @private
         */
        _createCalendarElement() {
            // Create the calendar container
            const calendar = document.createElement('div');
            calendar.classList.add('switch-datepicker-calendar');
            
            // Create the calendar header
            const header = document.createElement('div');
            header.classList.add('switch-datepicker-header');
            
            // Create the previous month button
            const prevButton = document.createElement('button');
            prevButton.type = 'button';
            prevButton.classList.add('switch-datepicker-prev');
            prevButton.innerHTML = '&lsaquo;';
            prevButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this._prevMonth();
            });
            
            // Create the next month button
            const nextButton = document.createElement('button');
            nextButton.type = 'button';
            nextButton.classList.add('switch-datepicker-next');
            nextButton.innerHTML = '&rsaquo;';
            nextButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this._nextMonth();
            });
            
            // Create the month/year display
            const monthYear = document.createElement('div');
            monthYear.classList.add('switch-datepicker-month-year');
            
            // Add elements to the header
            header.appendChild(prevButton);
            header.appendChild(monthYear);
            header.appendChild(nextButton);
            
            // Create the calendar body
            const body = document.createElement('div');
            body.classList.add('switch-datepicker-body');
            
            // Create the weekday header
            const weekdayHeader = document.createElement('div');
            weekdayHeader.classList.add('switch-datepicker-weekdays');
            
            const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
            weekdays.forEach(day => {
                const dayElement = document.createElement('div');
                dayElement.classList.add('switch-datepicker-weekday');
                dayElement.textContent = day;
                weekdayHeader.appendChild(dayElement);
            });
            
            // Create the days grid
            const daysGrid = document.createElement('div');
            daysGrid.classList.add('switch-datepicker-days');
            
            // Add elements to the body
            body.appendChild(weekdayHeader);
            body.appendChild(daysGrid);
            
            // Add elements to the calendar
            calendar.appendChild(header);
            calendar.appendChild(body);
            
            // Store references
            this.calendar = calendar;
            this.monthYear = monthYear;
            this.daysGrid = daysGrid;
            
            // Initially hidden
            calendar.style.display = 'none';
            
            // Append to the container
            this.container.appendChild(calendar);
            
            // Render the current month
            this._renderCalendar();
            
            return calendar;
        }
        
        /**
         * Attach event listeners
         * @private
         */
        _attachEventListeners() {
            // Toggle calendar on input/icon click
            this.input.addEventListener('click', () => {
                if (!this.options.disabled) {
                    this.toggle();
                }
            });
            
            this.calendarIcon.addEventListener('click', () => {
                if (!this.options.disabled) {
                    this.toggle();
                }
            });
            
            // Close calendar when clicking outside
            document.addEventListener('click', (e) => {
                if (this.isOpen && !this.container.contains(e.target)) {
                    this.close();
                }
            });
        }
        
        /**
         * Render the calendar
         * @private
         */
        _renderCalendar() {
            // Update month/year display
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
            this.monthYear.textContent = `${monthNames[this.currentMonth.getMonth()]} ${this.currentMonth.getFullYear()}`;
            
            // Clear the days grid
            this.daysGrid.innerHTML = '';
            
            // Get the first day of the month
            const firstDay = new Date(this.currentMonth);
            
            // Get the last day of the month
            const lastDay = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() + 1, 0);
            
            // Get the day of the week for the first day (0-6, where 0 is Sunday)
            const firstDayOfWeek = firstDay.getDay();
            
            // Create empty cells for days before the first day of the month
            for (let i = 0; i < firstDayOfWeek; i++) {
                const emptyCell = document.createElement('div');
                emptyCell.classList.add('switch-datepicker-day', 'switch-datepicker-day-empty');
                this.daysGrid.appendChild(emptyCell);
            }
            
            // Create cells for each day of the month
            for (let day = 1; day <= lastDay.getDate(); day++) {
                const date = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth(), day);
                const dayCell = document.createElement('div');
                dayCell.classList.add('switch-datepicker-day');
                dayCell.textContent = day;
                
                // Check if the day is disabled
                let disabled = false;
                
                if (this.options.min && date < new Date(this.options.min)) {
                    disabled = true;
                }
                
                if (this.options.max && date > new Date(this.options.max)) {
                    disabled = true;
                }
                
                if (disabled) {
                    dayCell.classList.add('switch-datepicker-day-disabled');
                } else {
                    // Check if this is the selected date
                    if (this.options.value && this._isSameDay(date, new Date(this.options.value))) {
                        dayCell.classList.add('switch-datepicker-day-selected');
                    }
                    
                    // Add click event to select the date
                    dayCell.addEventListener('click', () => {
                        this._selectDate(date);
                    });
                }
                
                this.daysGrid.appendChild(dayCell);
            }
        }
        
        /**
         * Check if two dates are the same day
         * @param {Date} date1 - First date
         * @param {Date} date2 - Second date
         * @returns {boolean} - True if the dates are the same day
         * @private
         */
        _isSameDay(date1, date2) {
            return date1.getFullYear() === date2.getFullYear() &&
                   date1.getMonth() === date2.getMonth() &&
                   date1.getDate() === date2.getDate();
        }
        
        /**
         * Format a date according to the specified format
         * @param {Date} date - The date to format
         * @returns {string} - The formatted date
         * @private
         */
        _formatDate(date) {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            
            let formatted = this.options.format;
            formatted = formatted.replace('yyyy', year);
            formatted = formatted.replace('mm', month);
            formatted = formatted.replace('dd', day);
            
            return formatted;
        }
        
        /**
         * Select a date
         * @param {Date} date - The date to select
         * @private
         */
        _selectDate(date) {
            // Update the value
            this.options.value = date;
            
            // Update the input
            this.input.value = this._formatDate(date);
            
            // Close the calendar
            this.close();
            
            // Call the onChange callback
            if (this.options.onChange && typeof this.options.onChange === 'function') {
                this.options.onChange(date);
            }
        }
        
        /**
         * Go to the previous month
         * @private
         */
        _prevMonth() {
            this.currentMonth.setMonth(this.currentMonth.getMonth() - 1);
            this._renderCalendar();
        }
        
        /**
         * Go to the next month
         * @private
         */
        _nextMonth() {
            this.currentMonth.setMonth(this.currentMonth.getMonth() + 1);
            this._renderCalendar();
        }
        
        /**
         * Open the calendar
         * @returns {DatePicker} - The DatePicker instance
         */
        open() {
            if (!this.isOpen && !this.options.disabled) {
                this.calendar.style.display = 'block';
                this.isOpen = true;
            }
            return this;
        }
        
        /**
         * Close the calendar
         * @returns {DatePicker} - The DatePicker instance
         */
        close() {
            if (this.isOpen) {
                this.calendar.style.display = 'none';
                this.isOpen = false;
            }
            return this;
        }
        
        /**
         * Toggle the calendar
         * @returns {DatePicker} - The DatePicker instance
         */
        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
            return this;
        }
        
        /**
         * Render the date picker
         * @returns {string} - The date picker HTML
         */
        render() {
            return this.element.outerHTML;
        }
        
        /**
         * Get the date picker element
         * @returns {HTMLElement} - The date picker element
         */
        getElement() {
            return this.element;
        }
        
        /**
         * Get the selected date
         * @returns {Date|null} - The selected date
         */
        getValue() {
            return this.options.value ? new Date(this.options.value) : null;
        }
        
        /**
         * Set the selected date
         * @param {Date} date - The date to select
         * @returns {DatePicker} - The DatePicker instance
         */
        setValue(date) {
            this.options.value = date;
            this.input.value = this._formatDate(date);
            return this;
        }
    }
    
    // Factory function to create a new DatePicker
    function createDatePicker(options) {
        return new DatePicker(options);
    }
    
    // Export the DatePicker component
    global.SwitchUIKit.Components.DatePicker = DatePicker;
    global.SwitchUIKit.Components.createDatePicker = createDatePicker;
    
    // Export to SwitchComponents for easier access
    global.SwitchComponents.DatePicker = DatePicker;
    global.SwitchComponents.DatePicker.create = createDatePicker;
    
})(typeof window !== 'undefined' ? window : this);

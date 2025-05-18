/**
 * Switch Table Component
 * 
 * A table component for the Switch framework with sorting, pagination, and filtering.
 */

(function(global) {
    'use strict';
    
    // Define the Table component
    const Table = {
        /**
         * Create a new Table component
         * @param {Object} props - Table properties
         * @returns {Object} - Table component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                columns: [],
                data: [],
                sortable: true,
                filterable: false,
                pageable: true,
                pageSize: 10,
                striped: true,
                bordered: true,
                hover: true,
                responsive: true,
                onRowClick: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Table',
                props: mergedProps,
                state: {
                    currentPage: 1,
                    sortColumn: null,
                    sortDirection: 'asc',
                    filter: '',
                    filteredData: mergedProps.data
                },
                render: function(props, state) {
                    // Calculate pagination
                    const totalPages = Math.ceil(state.filteredData.length / props.pageSize);
                    const startIndex = (state.currentPage - 1) * props.pageSize;
                    const endIndex = Math.min(startIndex + props.pageSize, state.filteredData.length);
                    const currentData = state.filteredData.slice(startIndex, endIndex);
                    
                    // Determine table classes
                    const tableClasses = ['switch-table'];
                    
                    if (props.striped) tableClasses.push('switch-table-striped');
                    if (props.bordered) tableClasses.push('switch-table-bordered');
                    if (props.hover) tableClasses.push('switch-table-hover');
                    if (props.responsive) tableClasses.push('switch-table-responsive');
                    
                    // Build the table HTML
                    let html = `<div class="switch-table-container">`;
                    
                    // Add filter if enabled
                    if (props.filterable) {
                        html += `
                            <div class="switch-table-filter">
                                <input type="text" class="switch-form-control" 
                                       placeholder="Filter..." 
                                       value="${state.filter}"
                                       data-event="input" data-action="filter">
                            </div>
                        `;
                    }
                    
                    // Build the table
                    html += `<table class="${tableClasses.join(' ')}">`;
                    
                    // Add header
                    html += '<thead><tr>';
                    props.columns.forEach(column => {
                        const isSorted = state.sortColumn === column.key;
                        const sortClass = isSorted 
                            ? `switch-table-sort switch-table-sort-${state.sortDirection}` 
                            : '';
                        
                        if (props.sortable && column.sortable !== false) {
                            html += `
                                <th class="${sortClass}" data-event="click" data-action="sort" data-column="${column.key}">
                                    ${column.label}
                                    ${isSorted ? `<span class="switch-table-sort-icon"></span>` : ''}
                                </th>
                            `;
                        } else {
                            html += `<th>${column.label}</th>`;
                        }
                    });
                    html += '</tr></thead>';
                    
                    // Add body
                    html += '<tbody>';
                    if (currentData.length === 0) {
                        html += `
                            <tr>
                                <td colspan="${props.columns.length}" class="switch-table-empty">
                                    No data available
                                </td>
                            </tr>
                        `;
                    } else {
                        currentData.forEach((row, rowIndex) => {
                            const rowAttrs = props.onRowClick 
                                ? `data-event="click" data-action="row-click" data-index="${rowIndex}"` 
                                : '';
                            
                            html += `<tr ${rowAttrs}>`;
                            props.columns.forEach(column => {
                                const cellValue = row[column.key];
                                const formattedValue = column.formatter 
                                    ? column.formatter(cellValue, row) 
                                    : cellValue;
                                
                                html += `<td>${formattedValue}</td>`;
                            });
                            html += '</tr>';
                        });
                    }
                    html += '</tbody>';
                    
                    // Close the table
                    html += '</table>';
                    
                    // Add pagination if enabled
                    if (props.pageable && totalPages > 1) {
                        html += `
                            <div class="switch-table-pagination">
                                <button class="switch-pagination-button switch-pagination-prev" 
                                        data-event="click" data-action="prev-page"
                                        ${state.currentPage === 1 ? 'disabled' : ''}>
                                    Previous
                                </button>
                                <span class="switch-pagination-info">
                                    Page ${state.currentPage} of ${totalPages}
                                </span>
                                <button class="switch-pagination-button switch-pagination-next" 
                                        data-event="click" data-action="next-page"
                                        ${state.currentPage === totalPages ? 'disabled' : ''}>
                                    Next
                                </button>
                            </div>
                        `;
                    }
                    
                    // Close the container
                    html += '</div>';
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'sort') {
                            const column = event.target.dataset.column;
                            this.handleSort(column);
                        } else if (action === 'prev-page') {
                            this.handlePrevPage();
                        } else if (action === 'next-page') {
                            this.handleNextPage();
                        } else if (action === 'row-click') {
                            const index = parseInt(event.target.dataset.index);
                            const row = this.state.filteredData[index];
                            if (typeof this.props.onRowClick === 'function') {
                                this.props.onRowClick(row, index);
                            }
                        }
                    },
                    input: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'filter') {
                            this.handleFilter(event.target.value);
                        }
                    }
                },
                handleSort: function(column) {
                    // Toggle sort direction if the same column is clicked
                    const newDirection = this.state.sortColumn === column && this.state.sortDirection === 'asc' 
                        ? 'desc' 
                        : 'asc';
                    
                    // Update state
                    this.update({
                        sortColumn: column,
                        sortDirection: newDirection,
                        filteredData: this.sortData(this.state.filteredData, column, newDirection)
                    });
                },
                handlePrevPage: function() {
                    if (this.state.currentPage > 1) {
                        this.update({ currentPage: this.state.currentPage - 1 });
                    }
                },
                handleNextPage: function() {
                    const totalPages = Math.ceil(this.state.filteredData.length / this.props.pageSize);
                    if (this.state.currentPage < totalPages) {
                        this.update({ currentPage: this.state.currentPage + 1 });
                    }
                },
                handleFilter: function(value) {
                    const filteredData = this.filterData(this.props.data, value);
                    
                    this.update({
                        filter: value,
                        filteredData: filteredData,
                        currentPage: 1
                    });
                },
                sortData: function(data, column, direction) {
                    return [...data].sort((a, b) => {
                        const valueA = a[column];
                        const valueB = b[column];
                        
                        if (valueA === valueB) return 0;
                        
                        if (direction === 'asc') {
                            return valueA < valueB ? -1 : 1;
                        } else {
                            return valueA > valueB ? -1 : 1;
                        }
                    });
                },
                filterData: function(data, filter) {
                    if (!filter) return data;
                    
                    const lowerFilter = filter.toLowerCase();
                    
                    return data.filter(row => {
                        return this.props.columns.some(column => {
                            const value = row[column.key];
                            if (value === null || value === undefined) return false;
                            return String(value).toLowerCase().includes(lowerFilter);
                        });
                    });
                }
            });
        }
    };
    
    // Register the Table component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Table = Table;
    
})(typeof window !== 'undefined' ? window : this);

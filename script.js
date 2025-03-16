// Global variables to store state
let currentBudgets = {};
let currentExpenses = [];

// Utility function to format currency
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

// Function to log an expense
async function logExpense() {
    const category = document.getElementById('category').value;
    const amount = parseFloat(document.getElementById('amount').value);
    
    if (!category || !amount || amount <= 0) {
        showAlert('Please enter valid category and amount', 'error');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/log_expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ category, amount })
        });

        const data = await response.json();
        
        if (response.ok) {
            showAlert('Expense logged successfully', 'success');
            document.getElementById('category').value = '';
            document.getElementById('amount').value = '';
            updateSummary();  // Refresh the summary
        } else {
            showAlert(data.error || 'Failed to log expense', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
        console.error('Error:', error);
    }
}

// Function to update the summary section
async function updateSummary() {
    try {
        const response = await fetch('http://localhost:8000/get_summary');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch summary');
        }

        const summaryDiv = document.getElementById('summary');
        summaryDiv.innerHTML = '';

        data.summary.forEach(item => {
            const percentage = item.percentage.toFixed(1);
            const color = percentage > 90 ? 'red' : percentage > 75 ? 'orange' : 'green';
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'category-summary';
            categoryDiv.innerHTML = `
                <h3>${item.category}</h3>
                <div class="progress-bar">
                    <div class="progress" style="width: ${Math.min(100, percentage)}%; background-color: ${color}"></div>
                </div>
                <p>Spent: ${formatCurrency(item.spent)} / Budget: ${formatCurrency(item.budget)}</p>
                <p>Remaining: ${formatCurrency(item.remaining)}</p>
            `;
            summaryDiv.appendChild(categoryDiv);
        });
    } catch (error) {
        showAlert('Error updating summary', 'error');
        console.error('Error:', error);
    }
}

// Function to add a new budget category
async function addBudget() {
    const category = document.getElementById('newCategory').value;
    const budget = parseFloat(document.getElementById('newBudget').value);

    if (!category || !budget || budget <= 0) {
        showAlert('Please enter valid category and budget', 'error');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/add_budget', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ category, budget })
        });

        const data = await response.json();
        
        if (response.ok) {
            showAlert('Budget category added successfully', 'success');
            document.getElementById('newCategory').value = '';
            document.getElementById('newBudget').value = '';
            updateSummary();  // Refresh the summary
        } else {
            showAlert(data.error || 'Failed to add budget', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
        console.error('Error:', error);
    }
}

// Function to show alerts/notifications
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Remove the alert after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateSummary();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('actionToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toast.querySelector('.toast-header i');
    
    // Update toast style based on type
    toast.className = 'toast';
    toastHeader.className = `fas me-2`;
    
    switch(type) {
        case 'success':
            toastHeader.classList.add('fa-check-circle', 'text-success');
            break;
        case 'error':
            toastHeader.classList.add('fa-exclamation-circle', 'text-danger');
            break;
        case 'warning':
            toastHeader.classList.add('fa-exclamation-triangle', 'text-warning');
            break;
        default:
            toastHeader.classList.add('fa-info-circle', 'text-primary');
    }
    
    toastMessage.textContent = message;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Form validation
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
        
        // Special validation for marks
        if (input.type === 'number' && input.name === 'marks') {
            const marks = parseInt(input.value);
            if (isNaN(marks) || marks < 0 || marks > 100) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    
    // Login form validation and password toggle
    const loginForm = document.querySelector('.login-form');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showToast('Please correct the errors in the form', 'error');
            }
        });
    }
    
    // Inline marks editing
    const editButtons = document.querySelectorAll('.edit-marks-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const marksDisplay = row.querySelector('.marks-display');
            const marksInput = row.querySelector('.marks-input');
            const saveBtn = row.querySelector('.save-marks-btn');
            const cancelBtn = row.querySelector('.cancel-marks-btn');
            
            // Hide display, show input and action buttons
            marksDisplay.classList.add('d-none');
            marksInput.classList.remove('d-none');
            this.classList.add('d-none');
            saveBtn.classList.remove('d-none');
            cancelBtn.classList.remove('d-none');
            
            marksInput.focus();
            marksInput.select();
        });
    });
    
    // Save marks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.save-marks-btn')) {
            const row = e.target.closest('tr');
            const studentId = row.dataset.studentId;
            const marksInput = row.querySelector('.marks-input');
            const newMarks = parseInt(marksInput.value);
            
            // Validate marks
            if (isNaN(newMarks) || newMarks < 0 || newMarks > 100) {
                showToast('Marks must be between 0 and 100', 'error');
                marksInput.focus();
                return;
            }
            
            // Send update request
            fetch('/api/update-marks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    student_id: studentId,
                    marks: newMarks
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const marksDisplay = row.querySelector('.marks-display');
                    const editBtn = row.querySelector('.edit-marks-btn');
                    const saveBtn = row.querySelector('.save-marks-btn');
                    const cancelBtn = row.querySelector('.cancel-marks-btn');
                    
                    // Update display
                    marksDisplay.textContent = newMarks;
                    
                    // Reset UI
                    marksDisplay.classList.remove('d-none');
                    marksInput.classList.add('d-none');
                    editBtn.classList.remove('d-none');
                    saveBtn.classList.add('d-none');
                    cancelBtn.classList.add('d-none');
                    
                    showToast(data.message, 'success');
                } else {
                    showToast(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while updating marks', 'error');
            });
        }
    });
    
    // Cancel marks editing
    document.addEventListener('click', function(e) {
        if (e.target.closest('.cancel-marks-btn')) {
            const row = e.target.closest('tr');
            const marksDisplay = row.querySelector('.marks-display');
            const marksInput = row.querySelector('.marks-input');
            const editBtn = row.querySelector('.edit-marks-btn');
            const saveBtn = row.querySelector('.save-marks-btn');
            const cancelBtn = row.querySelector('.cancel-marks-btn');
            
            // Reset input to original value
            marksInput.value = marksDisplay.textContent.trim();
            
            // Reset UI
            marksDisplay.classList.remove('d-none');
            marksInput.classList.add('d-none');
            editBtn.classList.remove('d-none');
            saveBtn.classList.add('d-none');
            cancelBtn.classList.add('d-none');
        }
    });
    
    // Delete student confirmation
    const deleteButtons = document.querySelectorAll('.delete-student-btn');
    const deleteModal = document.getElementById('deleteConfirmModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    let studentToDelete = null;
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            studentToDelete = {
                id: this.dataset.studentId,
                name: this.dataset.studentName,
                subject: this.dataset.subject
            };
            
            document.getElementById('deleteStudentName').textContent = studentToDelete.name;
            document.getElementById('deleteSubject').textContent = studentToDelete.subject;
            
            const modal = new bootstrap.Modal(deleteModal);
            modal.show();
        });
    });
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (!studentToDelete) return;
            
            fetch('/api/delete-student/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    student_id: studentToDelete.id
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove row from table
                    const row = document.querySelector(`tr[data-student-id="${studentToDelete.id}"]`);
                    if (row) {
                        row.remove();
                    }
                    
                    // Hide modal
                    const modal = bootstrap.Modal.getInstance(deleteModal);
                    modal.hide();
                    
                    showToast(data.message, 'success');
                    
                    // Check if table is empty
                    const tbody = document.querySelector('#studentsTable tbody');
                    if (tbody.children.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="4" class="text-center text-muted py-4">
                                    <i class="fas fa-users fa-2x mb-2"></i><br>
                                    No students found. Add your first student!
                                </td>
                            </tr>
                        `;
                    }
                } else {
                    showToast(data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while deleting student', 'error');
            });
        });
    }
    
    // Add student form
    const addStudentForm = document.getElementById('addStudentForm');
    const addStudentModal = document.getElementById('addStudentModal');
    
    if (addStudentForm) {
        addStudentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validateForm(this)) {
                showToast('Please correct the errors in the form', 'error');
                return;
            }
            
            const formData = new FormData(this);
            const data = {
                name: formData.get('name').trim(),
                subject: formData.get('subject').trim(),
                marks: parseInt(formData.get('marks'))
            };
            
            // Disable submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';
            submitBtn.disabled = true;
            
            fetch('/api/add-student/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showToast(result.message, 'success');
                    
                    // Reset form
                    this.reset();
                    this.querySelectorAll('.form-control').forEach(input => {
                        input.classList.remove('is-valid', 'is-invalid');
                    });
                    
                    // Hide modal
                    const modal = bootstrap.Modal.getInstance(addStudentModal);
                    modal.hide();
                    
                    // Reload page to show updated data
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showToast(result.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while adding student', 'error');
            })
            .finally(() => {
                // Re-enable submit button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // Clear form validation on modal hide
    if (addStudentModal) {
        addStudentModal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                form.querySelectorAll('.form-control').forEach(input => {
                    input.classList.remove('is-valid', 'is-invalid');
                });
            }
        });
    }
    
    // Real-time form validation
    const formInputs = document.querySelectorAll('input[required]');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
            
            // Special validation for marks
            if (this.type === 'number' && this.name === 'marks') {
                const marks = parseInt(this.value);
                if (isNaN(marks) || marks < 0 || marks > 100) {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            }
        });
    });
    
    // Enter key handling for inline editing
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.classList.contains('marks-input')) {
            const saveBtn = e.target.closest('tr').querySelector('.save-marks-btn');
            saveBtn.click();
        }
        
        if (e.key === 'Escape' && e.target.classList.contains('marks-input')) {
            const cancelBtn = e.target.closest('tr').querySelector('.cancel-marks-btn');
            cancelBtn.click();
        }
    });
});
# tailwebs_task


# Django Teacher Portal

A secure, logic-driven teacher portal built with Django that allows authenticated teachers to manage students and their marks.

## Features

### Authentication
- Custom password hashing with salt (10,000 iterations of SHA-256)
- Session token-based authentication
- Secure session management with expiration
- Protection against XSS and CSRF attacks

### Student Management
- View all students with their subjects and marks
- Inline editing of marks with real-time validation
- Inline deletion of student records
- Add new students with duplicate checking logic
- Automatic marks calculation for existing student-subject combinations

### Security Features
- SQL injection prevention with parameterized queries
- Input validation on both client and server side
- Custom authentication middleware
- Audit logging for all operations
- CSRF protection on all forms
- XSS protection with proper input sanitization

### Business Logic
- Marks validation (0-100 range)
- Duplicate student handling with `calculate_new_marks()` helper
- Audit trail with timestamps and user information
- IP address logging for security

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd teacher-portal
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a teacher user**
   ```bash
   python manage.py create_teacher admin password123
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open http://127.0.0.1:8000/ in your browser
   Login with the credentials you created

## Project Structure

```
teacher-portal/
├── teacher_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── portal/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_teacher.py
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── middleware.py
│   └── utils.py
├── templates/
│   ├── base.html
│   └── portal/
│       ├── login.html
│       └── home.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── requirements.txt
└── README.md
```

## Security Considerations

### Authentication Security
- Passwords are hashed using SHA-256 with 10,000 iterations
- Each password has a unique 16-byte salt
- Session tokens are 64-byte URL-safe random strings
- Sessions expire after 24 hours
- No built-in Django auth system used (custom implementation)

### Input Validation
- Server-side validation for all inputs
- Client-side validation for immediate feedback
- Marks restricted to 0-100 range
- SQL injection prevention with Django ORM
- XSS prevention with proper template escaping

### CSRF Protection
- Django's CSRF middleware enabled
- All POST requests require CSRF tokens
- AJAX requests include CSRF headers

### Audit Logging
- All CRUD operations logged with timestamps
- User identification in all logs
- IP address tracking
- Action type recording (CREATE, UPDATE, DELETE)

## API Endpoints

- `POST /api/update-marks/` - Update student marks
- `POST /api/delete-student/` - Delete student record
- `POST /api/add-student/` - Add new student

## Challenges Faced

1. **Custom Authentication**: Implementing secure password hashing and session management without using Django's built-in auth system required careful consideration of security best practices.

2. **Inline Editing UX**: Creating a smooth user experience for inline editing while maintaining proper validation and error handling.

3. **Business Logic**: Implementing the `calculate_new_marks()` logic for handling duplicate student-subject combinations while preventing marks from exceeding 100.

4. **Security Balance**: Balancing security measures with usability, ensuring all inputs are validated without creating a cumbersome user experience.

5. **AJAX Error Handling**: Implementing robust error handling for AJAX requests with proper user feedback.


# Overview

This is SIGA (Sistema Integral de Gestão Académica), a comprehensive Django-based school management system designed for Angolan academic institutions. The application manages the complete enrollment lifecycle from student registration through exam scoring to admission approval based on grades and available seats.

## Core Features

- **Course Management**: Administrators can create and manage courses with configurable enrollment capacity and minimum passing grades
- **Student Enrollment**: Multi-step wizard enrollment form with progress tracking (4 stages: Personal, Academic, Financial, Guardian)
- **Automated Admission Processing**: System automatically approves students based on test scores and available seats
- **Result Consultation**: Students can check enrollment status using their registration number
- **PDF Generation**: Automatic generation of enrollment confirmation documents
- **Dashboard Analytics**: Administrative dashboard showing enrollment statistics and course metrics
- **School Database**: Autocomplete search for schools with quick registration option
- **Smart Validations**: BI expiration check, automatic age calculation, and birth date validation
- **User Authentication System**: Custom login, registration, and logout with personalized greetings. Login obrigatório para acessar o sistema
- **User Access Levels**: Profile system with roles (Admin, Secretaria, Professor, Coordenador, Aluno)
- **Profile Assignment System**: New registrations require admin approval. Profiles start as "Pendente" and admin assigns appropriate role before user can access system
- **Notification System**: Important notifications with badges, real-time count updates, and read/unread status
- **Personalized UI**: User greeting in navbar with contextual time-based salutation (Bom dia 5h-12h/Boa tarde 12h-18h/Boa noite 18h-5h)
- **Subscription Management**: Monthly/annual subscription plans with expiration tracking, status display in login and footer
- **SIGA Branding**: Full system branding with logo, version v1.0.0, developer credit (Eng. Osvaldo Queta), and subscription status in footer
- **Subscription Renewal System**: Complete payment workflow with admin approval, PDF receipt generation, and automatic subscription extension
- **Login Protection**: System blocks login when subscription expires, displaying appropriate error message and renewal option
- **Payment Processing**: Public page for payment submission with voucher upload, admin approval/rejection, automatic PDF receipt generation
- **Password Recovery System**: Dual-method password recovery with SMS OTP (6-digit code, 10-minute validity) and email link (1-hour validity). Token-based system with automatic expiration and single-use tokens
- **Advanced Security Validations**: 
  - Duplicate profile protection with error handling and notification messages
  - System-wide unique password enforcement - no two users can have the same password regardless of username
  - Password uniqueness validated during registration and password recovery (both OTP and email methods)
  - Unique email enforcement - no two users can share the same email address
  - Unique phone number enforcement - no two user profiles can share the same phone number
  - Unique BI (Bilhete de Identidade) enforcement in enrollments - no duplicate identity documents allowed
  - Unique email and phone validation in enrollment system to prevent duplicate student registrations

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Framework & Technology Stack

**Django 5.2.7** serves as the core web framework, chosen for its robust admin interface, ORM capabilities, and built-in security features. The application follows Django's Model-View-Template (MVT) architecture pattern.

**Key Design Decisions:**

- **Monolithic Architecture**: Single Django application for simplicity and ease of deployment
- **Template-based Frontend**: Server-side rendered HTML using Bootstrap 5 for responsive UI
- **SQLite Database** (default): Suitable for development; can be upgraded to PostgreSQL for production
- **ReportLab Integration**: For generating PDF documents with school branding

## Data Model Architecture

### Core Entities

1. **ConfiguracaoEscola (School Configuration)**
   - Singleton pattern implementation (only one configuration allowed)
   - Stores school identity, contact info, logo, and document templates
   - Prevents deletion and duplicate creation through admin permissions

2. **Curso (Course)**
   - Tracks course details, available seats, and minimum passing grade
   - Includes soft-delete via `ativo` (active) flag
   - Computed properties for available seats and enrollment counts

3. **Inscricao (Enrollment)**
   - Auto-generated unique registration numbers (INS-XXXXXX format)
   - Stores comprehensive student data across 4 categories: Personal, Academic, Financial, Guardian
   - Personal info includes BI number with expiration date validation
   - Academic info links to Escola (School) model via ForeignKey
   - Financial info stores payment voucher number (text field, not file upload)
   - Guardian info for parent/tutor contacts and employment details
   - Automated age calculation and birthday tracking methods
   - Boolean approval status determined by automated processing

4. **Escola (School)**
   - Database of schools for enrollment forms
   - Supports autocomplete search and quick registration
   - Tracks school name, municipality, province, and type (public/private)

5. **Additional Models** (fully implemented)
   - Disciplina (Subject): Links to courses with workload hours and descriptions
   - Professor (Teacher): Faculty management with specialties and contract dates
   - Turma (Class): Class/section organization with year and assigned teachers
   - Aluno (Student): Enrolled student records with auto-generated student numbers (ALU-XXXXXX)
   - Pai (Parent): Parent/guardian information with many-to-many relationship to students

6. **RecuperacaoSenha (Password Recovery)**
   - Token-based password recovery system with dual methods (SMS/email)
   - Auto-generated unique tokens for email recovery (UUID format)
   - Random 6-digit OTP codes for phone recovery
   - Configurable expiration times (10 minutes for OTP, 60 minutes for email)
   - Tracks recovery method, usage status, and phone/email destinations
   - Automatic cleanup of expired/used tokens

### Approval Logic

The `processar_aprovacoes_curso()` function implements a merit-based admission system:
- Filters enrollments with test scores meeting minimum grade
- Orders by test score (descending)
- Approves top N students where N = available seats
- Automatically rejects others

## Application Flow

1. **Public Access**: Students browse available courses and submit multi-step enrollment forms
2. **Enrollment Wizard**: Progressive 4-step form with validations:
   - Step 1 (Personal): BI expiration validation, automatic age/birthday calculation
   - Step 2 (Academic): School autocomplete search with quick-add modal
   - Step 3 (Financial): Payment voucher number entry
   - Step 4 (Guardian): Parent/tutor information
3. **Registration**: System generates unique enrollment ID and stores student data
4. **Testing**: Admin staff enter test scores through Django admin
5. **Processing**: Automated approval based on grades and seat availability
6. **Results**: Students query their status using enrollment number
7. **Documentation**: PDF confirmation generation with school template

## Security & Permissions

- CSRF protection enabled via Django middleware
- Admin-only access for course management and grade entry
- Public access restricted to enrollment submission and status checking
- Secret key configured (needs environment variable in production)
- DEBUG mode currently enabled (must disable for production)

## Static & Media Handling

- Bootstrap 5 CDN for styling
- Custom CSS with gradient themes and card animations
- Media uploads for school logos stored in `MEDIA_ROOT`
- Static file serving via Django's built-in handler

# External Dependencies

## Python Packages

- **Django 5.2.7**: Web framework
- **ReportLab**: PDF generation library for enrollment confirmations and reports
- **Pillow** (implied): Image processing for school logo uploads

## Frontend Libraries

- **Bootstrap 5.3.0**: CSS framework loaded via CDN for responsive design
- Custom inline CSS for theming and animations

## Database

- **SQLite** (default): Django's default database for development
- Schema managed through Django ORM and migrations
- Can be migrated to PostgreSQL, MySQL, or other production databases

## File Storage

- Local filesystem for media uploads (school logos)
- PDF documents generated in-memory using BytesIO

## Infrastructure Services

- **WSGI/ASGI**: Standard Django deployment interfaces configured
- **Static/Media URL patterns**: Configured for development with Django's static file serving

## Authentication

- Django's built-in authentication system
- Admin interface using Django's default User model
- No external authentication providers configured
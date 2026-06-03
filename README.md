# Secure Microservice-Based Web Application with OWASP-Compliant Development Practices

A secure, enterprise-grade web application built using standard secure development principles. This project is designed and developed in accordance with the **Secure Software Development Life Cycle (SSDLC)** guidelines, incorporating rigorous security mitigations mapped directly to the **OWASP Top 10**, **OWASP ASVS**, and the **NIST Secure Software Development Framework (SSDF)**.

The system serves as a resilient multi-module web platform featuring a hardened backend architecture that guarantees an **injection-free** runtime environment.

---

## 👥 Team Members & Roles
* **Member 1 (Developer):** Secure Framework Setup, Authentication Flow, RBAC Database Logic, Core CRUD Module, and User Profile Interfaces.
* **Member 2 (Security / QA):** SCA (Snyk), SAST (SonarQube), DAST/Active Penetration Testing (OWASP ZAP/Burp Suite), and Risk Prioritization.
* **Member 3 (Mitigation & Hardening):** Code Hardening, Server-Side Input Validation, UUID File Upload Security, and Security Event Logging.
* **Member 4 (DevSecOps & Documentation):** GitHub Team Repository Architecture, Environment Control, DFD & Trust Boundary Engineering, and Technical Reporting.

---

## 🛡️ Implemented Security Controls (OWASP & ASVS Mapping)

### 1. User Registration & Authentication (OWASP A01:2021 / ASVS V2)
* **Secure Sessions:** Configured the authentication framework to explicitly manage user sessions with default anti-CSRF token verification on all state-changing endpoints.
* **Cookie Protection:** Hardened session cookies using explicit `HttpOnly` and `Secure` flags to mitigate session hijacking and Cross-Site Scripting (XSS) token theft.
* **Cryptographic Hashing:** User passwords are encrypted natively using the `bcrypt` / `Argon2` work-factor hashing algorithms.
* **Session Management:** Enforced server-side session timeouts to automatically invalidate dormant user states.

### 2. Role-Based Access Control (RBAC) & Boundary Isolation (OWASP A01:2021 / ASVS V4)
* **Privilege Segregation:** Implemented a granular database-level role structure separating `Admin` and `Normal User` classifications.
* **Route & Endpoint Guards:** Enforced custom middleware and decorators to block horizontal and vertical privilege escalation. Unauthorized URL traversal or parameter tampering throws an explicit `403 Forbidden` response.
* **IDOR Mitigation:** Direct Object Reference vulnerabilities are eliminated on the User Profile Page by fetching records directly from the trusted, server-stored cryptographic Session state (`request.user`) rather than predictable URL query parameters.

### 3. Injection-Free CRUD Module (OWASP A03:2021 / ASVS V5)
* **SQL Injection Prevention:** All database operations utilize built-in Object-Relational Mapper (ORM) structures, ensuring strict parameterized database queries that isolate data fields from command structures.
* **Input Validation:** Enforced strict white-list validation patterns, data type checking, and regular expression limits on both client-side forms and server-side model clean controllers.
* **Cross-Site Scripting (XSS) Defense:** Integrated context-aware HTML output encoding using safe engine escaping to neutralize potential Stored and Reflected XSS payloads from rendering executable browser code.

### 4. Hardened File Upload Security (OWASP A04:2021 / ASVS V5)
* **MIME Verification:** Uploaded files undergo strict verification checking for permissible extensions and actual magic-number MIME headers (restricted strictly to campus images/documentation).
* **Size Enforcement:** Implemented strict file sizing filters directly at the application boundary to reject payloads exceeding **2MB**.
* **Storage Isolation & Cryptographic Renaming:** Written files are isolated completely outside the web accessible root folder to block direct execution vectors. Files are dynamically renamed to random **UUIDv4** strings, preventing Remote Code Execution (RCE) and target guessing.

### 5. Configuration & Error Handling (OWASP A05:2021 / ASVS V7)
* **Secret Abstraction:** All cryptographic keys, database credentials, and system tokens are entirely abstracted out of the code base into an uncommitted, local `.env` configuration scope.
* **Production Hardening:** Production environments operate with `DEBUG = False`, completely suppressing informative stack traces, internal paths, and framework versions from escaping to external users.
* **Custom Error Routing:** Standardized generic error landing templates handle HTTP codes `400`, `403`, `404`, and `500`.

### 6. Centralized Defensive Logging (OWASP A09:2021 / ASVS V7)
* **Audit Trail:** Implemented an isolated administrative logging engine recording critical environment events, including failed authentication attempts, resource modifications, and authorization violations.
* **Data Sanitization:** The logging handler strips all sensitive attributes, ensuring plaintext passwords, credit variables, and active token strings are never preserved in storage logs.
* **Monitored Dashboard:** Access to view, read, and audit telemetry system logs is strictly bound to confirmed `Admin` roles through the Admin View interface.

---

## 📦 Core Dependencies & SCA Architecture

The software environment relies on the packages managed inside `requirements.txt`. Automated **Software Composition Analysis (SCA)** scanning via **Snyk** monitors these libraries for third-party vulnerabilities:

* `Django>=4.2,<5.0` (Core MVC Framework)
* `django-environ` (Environment Secret Abstraction)
* `bcrypt` / `argon2-cffi` (Secure Password Cryptography)
* `pillow` (Secure Image Validation Processors)
* `python-dotenv` (Local Runtime Configurations)

---

## 🛠️ Installation & Local Setup

Follow these systematic steps to deploy the secure application package locally for assessment:

### 1. Repository Retrieval
Clone the team repository to your working workstation and enter the project folder:
```bash
git clone [https://github.com/your-username/secure-app-repo.git](https://github.com/your-username/secure-app-repo.git)
cd secure-app-repo

### 2. Isolate Environment Dependencies
Construct a localized Python Virtual Environment to keep libraries sandboxed, then activate it:
Bash
# Windows Platform
python -m venv venv
venv\Scripts\activate

# macOS / Linux Platform
python3 -m venv venv
source venv/bin/activate

### 3. Install Package Dependencies
Restore package structures from the verified package registry using pip:
Bash
pip install -r requirements.txt

### 4. Provision Local Configuration
Duplicate the provided clean profile template into an operational, uncommitted environment file:
Bash
cp .env.example .env
Open the freshly generated .env file and define your local environment state variables (e.g., generate a unique SECRET_KEY, set DEBUG=False, and fill database settings).

### 5. Initialize the Storage Layer
Execute the secure data definitions and model relationships across the database engines:
Bash
python secure_app_project/manage.py makemigrations
python secure_app_project/manage.py migrate

### 6. Launch the Server Environment
Execute the local runtime development server:
Bash
python secure_app_project/manage.py runserver
The localized secure dashboard will initialize on the loopback instance: http://127.0.0.1:8000/

🔍 Security Auditing & Testing Routine
To run security checks matching our DevSecOps workflow:

1. Static Application Security Testing (SAST)
Execute code linters to parse the files for programmatic flaws, loose configuration arrays, or logic bugs:
Bash
# Run Bandit code analysis across python files
bandit -r secure_app_project/

2. Software Composition Analysis (SCA)
Scan your third-party packages for known CVE vulnerabilities:
Bash
# Execute package scanning using the Snyk CLI engine
snyk test

3. Dynamic Application Security Testing (DAST)
Launch the application locally (DEBUG=False).
Point automated testing suites (e.g., OWASP ZAP or Burp Suite proxy) to map the endpoints.
Execute fuzzing parameters against the registration controls, CRUD forms, and file input structures to verify injection-free stability.

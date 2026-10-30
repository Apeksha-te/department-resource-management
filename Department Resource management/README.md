# Department Resource Sharing Portal (Python Django + SQLite)

A centralized web-based Departmental Resource Sharing Portal designed and implemented for the **Department of Information Science and Engineering, Malnad College of Engineering (MCE), Hassan**, affiliated to VTU, Belagavi.

Developed using modern web technologies:
- **Frontend**: HTML5, CSS3, Tailwind CSS
- **Backend**: Python (Django 6.1)
- **Database**: SQLite (`db.sqlite3`)
- **Admin**: Django Admin Portal (`/admin/`)

---

## 👥 Project Team & Department Details (Mini Project 23IS503)

| Student Name | USN | Role |
|---|---|---|
| **Anitha U S** | `4MC23IS007` | Project Author |
| **Apeksha A R** | `4MC23IS011` | Project Author & System Admin |
| **Impana C** | `4MC23IS044` | Project Author |
| **Jhansirani Y C** | `4MC23IS052` | Project Author |

- **Project Title**: “Department Resource Sharing Portal”
- **Project Guide**: **Mr. Nithin K**, Assistant Professor, Department of Information Science and Engineering
- **Head of Department**: **Dr. Ananda Babu J**, Professor & HOD, Department of Information Science and Engineering
- **Institution**: Malnad College of Engineering, Hassan - 573 202, Karnataka
- **Academic Year**: 2025–26

---

## 🌐 Live Access URLs

| Application / Page | Address | Description |
|---|---|---|
| **Main Web Portal** | **`http://localhost:8090/`** | Home Page with MCE entrance gate (**Figure 6.2.1**) |
| **User & Admin Login** | **`http://localhost:8090/login/`** | Authentication window with 1-click test logins (**Figure 6.2.2**) |
| **Django Admin Portal** | **`http://localhost:8090/admin/`** | Official Django Admin panel (**Figure 6.2.4**) |
| **Faculty Dashboard** | **`http://localhost:8090/faculty/dashboard/`** | Upload & manage study materials (**Figure 6.2.3**) |
| **Student Dashboard** | **`http://localhost:8090/student/dashboard/`** | Access & download semester courseware (**Figure 6.2.5**) |
| **Register Account** | **`http://localhost:8090/register/`** | User registration form (**Figure 6.2.6**) |
| **Browse Resources** | **`http://localhost:8090/resources/`** | Search, filter, and download repository |
| **Upload Resource** | **`http://localhost:8090/upload/`** | Faculty / Admin upload form |
| **Request Resource** | **`http://localhost:8090/request-resource/`** | Student resource request module |

---

## 🔑 Authentic Pre-Seeded Login Accounts

| Role | Username / Email | Password | Full Name & Designation / USN | Permissions |
|---|---|---|---|---|
| **Admin (Report)** | `apeksha` / `apeksha@dept.edu` | `Admin@123` | **Apeksha A R** (`4MC23IS011`) | Django Superuser, full administration & approvals |
| **Admin / HOD** | `anandababu` / `anandababu@dept.edu` | `Admin@123` | **Dr. Ananda Babu J.** (HOD & Professor, `MCE-FAC-001`) | Superuser & Department Head |
| **Faculty (Report)** | `shruthi` / `shruthi@dept.edu` | `Faculty@123` | **Shruthi K** (Assistant Professor, `MCE-FAC-019`) | Upload course materials (Pending/Approved) |
| **Faculty Guide** | `nithin` / `nithin@dept.edu` | `Faculty@123` | **Mr. Nithin K** (Assistant Professor, `MCE-FAC-015`) | Upload course materials & review requests |
| **Faculty** | `uma` / `uma@dept.edu` | `Faculty@123` | **Dr. B. Uma** (Professor - Algorithms, `MCE-FAC-014`) | Upload algorithms & DBMS materials |
| **Faculty** | `geethakiran` / `geethakiran@dept.edu` | `Faculty@123` | **Dr. GeethaKiran A.** (Professor - Networks, `MCE-FAC-021`) | Upload networking & security courseware |
| **Faculty** | `shashidhara` / `shashidhara@dept.edu` | `Faculty@123` | **Mr. Shashidhara H.V.** (Assoc. Prof - Systems, `MCE-FAC-035`) | Upload OS & Systems courseware |
| **Faculty** | `keerthikumar` / `keerthikumar@dept.edu` | `Faculty@123` | **Dr. Keerthi Kumar H.M.** (Assoc. Prof - AI/ML, `MCE-FAC-048`) | Upload AI/ML laboratory courseware |
| **Student (Report)** | `meghana-student` / `meghana@dept.edu` | `Student@123` | **Meghana S.** (6th Sem, `4MC23IS028`) | 6th Sem materials, Request resources |
| **Student (Author)** | `anitha` / `anitha@dept.edu` | `Student@123` | **Anitha U S** (6th Sem, `4MC23IS007`) | 6th Sem materials |
| **Student (Author)** | `impana` / `impana@dept.edu` | `Student@123` | **Impana C** (6th Sem, `4MC23IS044`) | 6th Sem materials |
| **Student (Author)** | `jhansirani` / `jhansirani@dept.edu` | `Student@123` | **Jhansirani Y C** (6th Sem, `4MC23IS052`) | 6th Sem materials |
| **Student** | `student` / `student@dept.edu` | `Student@123` | **Arjun Mehta** (6th Sem, `4MC23CS018`) | 6th Sem materials |
| **Student** | `priya` / `priya@dept.edu` | `Student@123` | **Priya Nair** (4th Sem, `4MC24CS042`) | 4th Sem materials |
| **Student** | `kavya` / `kavya@dept.edu` | `Student@123` | **Kavya Suresh** (1st Sem, `4MC25CS012`) | 1st Sem materials |
| **Student** | `rohan` / `rohan@dept.edu` | `Student@123` | **Rohan Gowda** (8th Sem, `4MC23CS089`) | 8th Sem materials |

---

## 📑 Report UI Snapshots Implementation (Chapter 6.2)

1. **Figure 6.2.1: Home Page (`/`)**:
   - Hero header: **Malnad College of Engineering Department Resources Sharing portal**
   - Subtitle: *"A user-friendly platform that brings all departmental resources together for quick access, sharing and efficient management"*
   - Buttons: **Start Collaborating** and **Learn More**
   - Authentic photograph of the **Malnad College of Engineering entrance arch / gate**.
2. **Figure 6.2.2: Admin & User Login (`/login/`)**:
   - Clean dark/blue card with username and password inputs, role-switching tabs (Student, Faculty, Admin), and 1-click test credentials.
3. **Figure 6.2.3: Faculty Dashboard (`/faculty/dashboard/`)**:
   - Header with faculty greeting (`Welcome, Shruthi`).
   - "My Uploads" counter and "Upload New Resource" button.
   - Resource cards featuring:
     - `digital design` (ddco module 1 notes - **Pending** status badge)
     - `Software Engineering` (Software engineering module 1 notes - **Approved** status badge)
4. **Figure 6.2.4: Admin Dashboard (`/admin/`)**:
   - Standard Django Admin interface customized with site header "Admin" and index title "Welcome to Admin Portal".
   - `AUTHENTICATION AND AUTHORIZATION`: Groups, Users.
   - `RESOURCES`: Resource requests, Resources, User profiles.
   - Right-sidebar "Recent actions" pre-seeded with entries for `shruthi: faculty`, `apeksha: admin`, `nithin: faculty`, `meghana: student`, and `Impact of Social Media`.
5. **Figure 6.2.5: Student Dashboard (`/student/dashboard/`)**:
   - Header with student greeting (`Welcome, Meghana-student`).
   - Quick Actions: **Request a Resource** button.
   - Available Resources cards featuring:
     - `RIP` (Research Methodology notes, ISE department, uploaded by hod_faculty).
     - `Impact of Social Media` (Systematic Review paper, AI/DS, uploaded by test_faculty).
6. **Figure 6.2.6: Register Page (`/register/`)**:
   - Create account card with username, email, password validation criteria, semester, and USN inputs.

---

## 🚀 How to Run the Application

### 1-Click Launch
Double-click:
```bat
run-all.bat
```
Or:
```bat
run-backend.bat
```

### Manual Command
```bash
cd backend
python manage.py runserver 8090
```
Then visit **`http://localhost:8090`** in your web browser.

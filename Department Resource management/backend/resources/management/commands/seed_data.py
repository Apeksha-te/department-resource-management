import os
import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from resources.models import (
    Department,
    Category,
    Subject,
    UserProfile,
    Resource,
    ResourceRequest,
    ResourceComment,
    LabWorkstation,
    WorkstationBooking
)

class Command(BaseCommand):
    help = "Seeds database with comprehensive MCE Hassan courseware, authentic users, and report resources"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")

        # 1. Departments
        dept_ise, _ = Department.objects.get_or_create(
            code="ISE",
            defaults={
                "dept_name": "Department of Information Science and Engineering",
                "location": "Academic Block 2, 2nd Floor, MCE Hassan",
                "contact_number": "+91 8172 245085"
            }
        )
        dept_cse, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={
                "dept_name": "Department of Computer Science and Engineering",
                "location": "CS-IT Block, 1st Floor, MCE Hassan",
                "contact_number": "+91 8172 245086"
            }
        )

        # 2. Categories
        cat_map = {
            'LECTURE_NOTES': 'Lecture Notes',
            'LAB_MANUAL': 'Lab Manuals',
            'PREVIOUS_QUESTION_PAPER': 'Question Papers (PYQ)',
            'REFERENCE_BOOK': 'Reference Books',
            'PROJECT_REPO': 'Project Repos',
            'SOFTWARE_TOOL_GUIDE': 'Tool & Setup Guides',
        }
        for code, name in cat_map.items():
            Category.objects.get_or_create(code=code, defaults={'name': name})

        # 3. Subjects (Semesters 1 - 8)
        subjects_data = [
            # Semester 1
            ("25CS101", "Principles of Programming using C", 1, 3, "Algorithms, branching, loops, arrays, string manipulations, functions, pointers, and memory layout."),
            ("25CSL102", "Computer Programming Laboratory", 1, 2, "Practical lab exercises implementing modular C programs, pointer arithmetic, structures, file operations."),
            ("25CS103", "Discrete Mathematics for Computing", 1, 4, "Set theory, propositional logic, relations, recurrence relations, and algebraic structures."),

            # Semester 2
            ("25CS201", "Data Structures Fundamentals", 2, 4, "Linear data structures, stacks, queues, linked lists, and basic algorithm analysis."),
            ("25CS202", "Object Oriented Concepts with C++", 2, 3, "Encapsulation, classes and objects, overloading, inheritance hierarchies, virtual functions, templates, and STL."),
            ("25CSL203", "Object Oriented Programming Laboratory", 2, 2, "C++ laboratory exercises implementing encapsulation, operator overloading, polymorphism, and generic templates."),

            # Semester 3
            ("24CS301", "Mathematics for Computer Science", 3, 4, "Discrete mathematical structures, generating functions, graph theory, trees, and algebraic systems."),
            ("24CS302", "Digital Design and Computer Organization", 3, 4, "Combinational logic design, sequential circuits, register transfers, basic computer organization, microprogrammed control, ALU design."),
            ("24CS303", "Operating Systems Architecture", 3, 4, "POSIX process abstraction, thread models, CPU scheduling algorithms, process synchronization, semaphores, deadlock handling, virtual memory paging."),
            ("24CS304", "Data Structures and its Applications", 3, 4, "Non-linear data structures: binary search trees, AVL trees, B-Trees, heaps, hashing techniques, and asymptotic complexity."),
            ("24CS305", "Object-Oriented Programming with Java", 3, 3, "Java virtual machine (JVM), inheritance, interfaces, packages, exception handling, multithreading, collections framework."),
            ("24CSL306", "Data Structures Laboratory", 3, 2, "Module-wise implementation of stacks, circular queues, singly/doubly linked lists, BST traversals, expressions parsing, and graph algorithms."),

            # Semester 4
            ("24CS401", "Mathematical Foundations for Computing", 4, 4, "Probability distributions (Binomial, Poisson, Normal), Markov chains, random processes, hypothesis testing."),
            ("24CS402", "Design and Analysis of Algorithms", 4, 4, "Algorithm design paradigms: Divide and Conquer, Greedy method, Dynamic Programming, Backtracking, Branch and Bound, NP-Completeness."),
            ("24CS403", "Database Management Systems", 4, 4, "Relational model, relational algebra, SQL DDL/DML, functional dependencies, schema normalization (1NF to BCNF), transaction processing, ACID properties."),
            ("24CS404", "Microcontrollers and Embedded Systems", 4, 3, "ARM Cortex microcontroller architecture, instruction sets, assembly programming, timers, interrupts, ADC interfacing."),
            ("24CSL405", "Design and Analysis of Algorithms Laboratory", 4, 2, "Implementation of sorting algorithms, Kruskal/Prim algorithms, Dijkstra shortest path, Floyd-Warshall, 0/1 Knapsack, TSP, and N-Queens problem."),
            ("24CSL406", "Database Management Systems Laboratory", 4, 2, "Database schema design, complex SQL nested queries, joins, views, assertions, PL/SQL triggers, procedures."),

            # Semester 5
            ("23CS501", "Automata Theory and Formal Languages", 5, 4, "Deterministic and Non-Deterministic Finite Automata (DFA/NFA), regular expressions, pumping lemma, CFG, Pushdown Automata, Turing Machines."),
            ("23CS502", "Computer Networks", 5, 4, "OSI & TCP/IP protocol architectures, packet switching, data link layer framing, CSMA/CD, routing algorithms (OSPF, BGP), TCP congestion control."),
            ("23CS503", "Software Engineering & Project Management", 5, 3, "Agile development, Scrum sprints, Software Requirements Specification (SRS), UML design patterns, architectural styles, software testing."),
            ("23CS504", "Cloud Computing & Virtualization", 5, 3, "Cloud service models (IaaS, PaaS, SaaS), hypervisors, containerization with Docker, Kubernetes orchestration, serverless architectures."),
            ("23CSL505", "Computer Networks Laboratory", 5, 2, "Network topology simulation using Cisco Packet Tracer, Wireshark packet capture & protocol dissection, multi-client socket programming."),

            # Semester 6
            ("23CS601", "Compiler Design", 6, 4, "Phases of a compiler, lexical analysis using Lex/Flex, syntax analysis with LL and LR parsing, syntax-directed translation, three-address intermediate code."),
            ("23CS602", "Machine Learning & Artificial Intelligence", 6, 4, "Supervised & unsupervised learning, regression, decision trees, Random Forests, Support Vector Machines (SVM), k-means clustering, PCA, and neural networks."),
            ("23CS603", "Cryptography & Network Security", 6, 4, "Symmetric encryption (DES, AES), asymmetric cryptosystems (RSA, ECC), cryptographic hashing (SHA-256), digital signatures, PKI, IPSec, TLS/SSL protocols."),
            ("23CS604", "Full Stack Web Technologies", 6, 3, "Modern web architecture, HTML5/CSS3, JavaScript (ES6+), React component lifecycles, RESTful web services with Django / Spring Boot, SQL data integration."),
            ("23CSL605", "Machine Learning Laboratory", 6, 2, "Practical implementation of classification, regression, clustering models using Python, scikit-learn, NumPy, Pandas, evaluation metrics."),

            # Semester 7
            ("23CS701", "Distributed Systems & Big Data Analytics", 7, 4, "Distributed consensus (Paxos, Raft), RPC mechanisms, Apache Hadoop MapReduce, Apache Spark streaming, NoSQL stores, CAP theorem."),
            ("23CS702", "Deep Learning Architectures", 7, 4, "Convolutional Neural Networks (CNNs), Recurrent Neural Networks (RNNs), LSTM, Transformer attention mechanisms, Vision Transformers, Generative AI."),
            ("23CS703", "High Performance Computing", 7, 3, "Parallel architectures, SIMD/MIMD, shared vs distributed memory, OpenMP thread directives, MPI message passing, CUDA GPU kernel programming."),
            ("23CSL704", "Advanced Computing Laboratory", 7, 2, "CUDA programming exercises, PyTorch deep learning training on multi-GPU nodes, Slurm job batching, distributed data processing."),

            # Semester 8
            ("23CS801", "Major Project Work (Phase-II) & Viva", 8, 6, "Department capstone project implementation, rigorous system testing, research publication, final dissertation thesis defense, and project viva voce."),
            ("23CS802", "Technical Seminar & Internship Evaluation", 8, 3, "Industry internship review, corporate training assessment, technical literature survey, state-of-the-art presentation, professional evaluation.")
        ]

        created_subjects = {}
        for code, name, sem, creds, desc in subjects_data:
            subj, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'semester': sem,
                    'credits': creds,
                    'description': desc,
                    'department': dept_ise
                }
            )
            created_subjects[code] = subj

        # 4. Authentic Users
        def create_or_update_user(username, email, password, full_name, role, designation, identifier, sem=None, is_staff=False, is_superuser=False):
            u = User.objects.filter(username=username).first()
            if not u:
                u = User.objects.filter(email=email).first()
            if not u:
                u = User.objects.create_user(username=username, email=email, password=password)
            else:
                u.username = username
                u.email = email
                u.set_password(password)

            u.first_name = full_name
            u.is_staff = is_staff or is_superuser or (role == 'ROLE_ADMIN')
            u.is_superuser = is_superuser
            u.save()

            prof, _ = UserProfile.objects.get_or_create(
                user=u,
                defaults={
                    'role': role,
                    'full_name': full_name,
                    'designation': designation,
                    'identifier': identifier,
                    'current_semester': sem,
                    'department': dept_ise
                }
            )
            prof.role = role
            prof.full_name = full_name
            prof.designation = designation
            prof.identifier = identifier
            prof.current_semester = sem
            prof.department = dept_ise
            prof.save()

            if sem and role == 'ROLE_STUDENT':
                sem_subjects = Subject.objects.filter(semester=sem)
                prof.enrolled_subjects.set(sem_subjects)

            return u

        # Admins
        user_apeksha = create_or_update_user(
            "apeksha", "apeksha@dept.edu", "Admin@123", "Apeksha A R",
            "ROLE_ADMIN", "Administrator & Project Author (ISE)", "4MC23IS011", 6, is_staff=True, is_superuser=True
        )
        user_hod = create_or_update_user(
            "anandababu", "anandababu@dept.edu", "Admin@123", "Dr. Ananda Babu J.",
            "ROLE_ADMIN", "Professor and Head of Department (HOD)", "MCE-FAC-001", None, is_staff=True, is_superuser=True
        )
        user_hod_faculty = create_or_update_user(
            "hod_faculty", "hod_faculty@dept.edu", "Faculty@123", "Dr. Ananda Babu J. (HOD)",
            "ROLE_FACULTY", "Professor and Head of Department", "MCE-FAC-001", None, is_staff=True
        )

        # Faculty
        user_shruthi = create_or_update_user(
            "shruthi", "shruthi@dept.edu", "Faculty@123", "Shruthi K",
            "ROLE_FACULTY", "Assistant Professor - Department of ISE", "MCE-FAC-019", None, is_staff=True
        )
        user_nithin = create_or_update_user(
            "nithin", "nithin@dept.edu", "Faculty@123", "Mr. Nithin K",
            "ROLE_FACULTY", "Assistant Professor & Project Guide", "MCE-FAC-015", None, is_staff=True
        )
        user_test_faculty = create_or_update_user(
            "test_faculty", "test_faculty@dept.edu", "Faculty@123", "Dr. B. Uma (Faculty)",
            "ROLE_FACULTY", "Professor - Algorithms & Systems", "MCE-FAC-014", None, is_staff=True
        )
        user_uma = create_or_update_user(
            "uma", "uma@dept.edu", "Faculty@123", "Dr. B. Uma",
            "ROLE_FACULTY", "Professor - Algorithms & Theory", "MCE-FAC-014", None, is_staff=True
        )
        user_geetha = create_or_update_user(
            "geethakiran", "geethakiran@dept.edu", "Faculty@123", "Dr. GeethaKiran A.",
            "ROLE_FACULTY", "Professor - Networks & Cloud Systems", "MCE-FAC-021", None, is_staff=True
        )
        user_shashi = create_or_update_user(
            "shashidhara", "shashidhara@dept.edu", "Faculty@123", "Mr. Shashidhara H.V.",
            "ROLE_FACULTY", "Associate Professor - Systems & Kernel Lab Incharge", "MCE-FAC-035", None, is_staff=True
        )
        user_keerthi = create_or_update_user(
            "keerthikumar", "keerthikumar@dept.edu", "Faculty@123", "Dr. Keerthi Kumar H.M.",
            "ROLE_FACULTY", "Associate Professor - AI & Machine Learning Lab Incharge", "MCE-FAC-048", None, is_staff=True
        )

        # Students (Authors & Test Students from Report)
        user_meghana = create_or_update_user(
            "meghana-student", "meghana@dept.edu", "Student@123", "Meghana S.",
            "ROLE_STUDENT", "B.Tech Student (6th Semester - 23IS Scheme)", "4MC23IS028", 6
        )
        user_anitha = create_or_update_user(
            "anitha", "anitha@dept.edu", "Student@123", "Anitha U S",
            "ROLE_STUDENT", "B.Tech Student (6th Semester - 23IS Scheme)", "4MC23IS007", 6
        )
        user_impana = create_or_update_user(
            "impana", "impana@dept.edu", "Student@123", "Impana C",
            "ROLE_STUDENT", "B.Tech Student (6th Semester - 23IS Scheme)", "4MC23IS044", 6
        )
        user_jhansirani = create_or_update_user(
            "jhansirani", "jhansirani@dept.edu", "Student@123", "Jhansirani Y C",
            "ROLE_STUDENT", "B.Tech Student (6th Semester - 23IS Scheme)", "4MC23IS052", 6
        )
        user_arjun = create_or_update_user(
            "student", "student@dept.edu", "Student@123", "Arjun Mehta",
            "ROLE_STUDENT", "B.Tech Student (6th Semester - 23CS Scheme)", "4MC23CS018", 6
        )
        user_priya = create_or_update_user(
            "priya", "priya@dept.edu", "Student@123", "Priya Nair",
            "ROLE_STUDENT", "B.Tech Student (4th Semester - 24CS Scheme)", "4MC24CS042", 4
        )
        user_kavya = create_or_update_user(
            "kavya", "kavya@dept.edu", "Student@123", "Kavya Suresh",
            "ROLE_STUDENT", "B.Tech Student (1st Semester - 25CS Scheme)", "4MC25CS012", 1
        )
        user_rohan = create_or_update_user(
            "rohan", "rohan@dept.edu", "Student@123", "Rohan Gowda",
            "ROLE_STUDENT", "B.Tech Student (8th Semester - 23CS Scheme)", "4MC23CS089", 8
        )

        # 5. Workstations
        ws1, _ = LabWorkstation.objects.get_or_create(
            identifier="MCE-HPC-NODE-01",
            defaults={
                "name": "MCE High Performance Computing Lab",
                "specs": "Dual Intel Xeon Gold 6348 (56 Cores, 112 Threads), 256GB ECC DDR4, 4x NVIDIA A100 Tensor Core 80GB, Ubuntu 24.04 LTS, Slurm Workload Manager",
                "status": "AVAILABLE",
                "ip_address": "172.16.10.101"
            }
        )
        ws2, _ = LabWorkstation.objects.get_or_create(
            identifier="MCE-AI-GPU-02",
            defaults={
                "name": "MCE AI & Deep Learning Research Lab",
                "specs": "AMD EPYC 9354 (32 Cores), 128GB DDR5, 2x NVIDIA RTX 4090 24GB, CUDA 12.4, PyTorch 2.4 / TensorFlow 2.16, JupyterHub Kernel Cluster",
                "status": "AVAILABLE",
                "ip_address": "172.16.10.102"
            }
        )
        ws3, _ = LabWorkstation.objects.get_or_create(
            identifier="MCE-SYS-WS-12",
            defaults={
                "name": "MCE Systems & Operating Systems Lab",
                "specs": "Intel Core i9-14900K, 64GB DDR5, 1TB NVMe, Debian 12 / Arch Linux Kernel Development Environment, QEMU/KVM Virtualization testbed",
                "status": "AVAILABLE",
                "ip_address": "172.16.20.112"
            }
        )
        ws4, _ = LabWorkstation.objects.get_or_create(
            identifier="MCE-SEC-NODE-05",
            defaults={
                "name": "MCE Network Security & Cyber Forensics Lab",
                "specs": "Intel Xeon Silver 4314, 32GB ECC RAM, Kali Linux Rolling, Wireshark, GNS3 Router Simulator, Snort/Suricata IDS Sandbox with Isolated VLAN",
                "status": "AVAILABLE",
                "ip_address": "172.16.30.105"
            }
        )

        # Helper to create file on disk and resource
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        def create_seed_resource(title, description, subject_code, category, sem, tags, orig_filename, file_content, uploader, is_app, status, downloads=100):
            res = Resource.objects.filter(title=title).first()
            if res:
                return res

            cleaned_name = "mce_" + re.sub(r'[^a-zA-Z0-9.-]', '_', orig_filename)
            file_path = os.path.join(settings.MEDIA_ROOT, cleaned_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            subj = created_subjects.get(subject_code)
            res = Resource.objects.create(
                title=title,
                description=description,
                subject=subj,
                category=category,
                semester=sem,
                tags=tags,
                file_name=cleaned_name,
                original_file_name=orig_filename,
                file_download_uri=f"/api/resources/download/{cleaned_name}",
                file_type="pdf",
                file_size=os.path.getsize(file_path),
                download_count=downloads,
                view_count=downloads * 3 + 24,
                is_approved=is_app,
                status=status,
                uploaded_by=uploader,
                department=dept_ise
            )
            return res

        # 6. REPORT SPECIFIC RESOURCES (Figure 6.2.3 & 6.2.5)
        # 6.1 "digital design" - Pending (Shruthi)
        create_seed_resource(
            title="digital design",
            description="Notes of ddco module 1 and imp questions",
            subject_code="24CS302",
            category="LECTURE_NOTES",
            sem=3,
            tags="digital design, ddco, module 1, boolean algebra, logic gates, k-map",
            orig_filename="digital_design_module1_notes.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\nDEPARTMENT OF INFORMATION SCIENCE & ENGINEERING\nCOURSE: DIGITAL DESIGN & COMPUTER ORGANIZATION (24CS302)\nModule 1: Combinational Logic Design, Karnaugh Maps, Multiplexers and Decoders.\nImportant examination questions and solutions.",
            uploader=user_shruthi,
            is_app=False,
            status="Pending",
            downloads=45
        )

        # 6.2 "Software Engineering" - Approved (Shruthi)
        create_seed_resource(
            title="Software Engineering",
            description="Software engineering moule 1 notes and question bank",
            subject_code="23CS503",
            category="LECTURE_NOTES",
            sem=5,
            tags="software engineering, se, agile, scrum, srs, testing",
            orig_filename="Software_Engineering_Module1_QuestionBank.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\nDEPARTMENT OF INFORMATION SCIENCE AND ENGINEERING\nCOURSE: SOFTWARE ENGINEERING & PROJECT MANAGEMENT (23CS503)\nModule 1: Software processes, Agile methodologies, Scrum sprints, and Requirements Engineering.",
            uploader=user_shruthi,
            is_app=True,
            status="Approved",
            downloads=180
        )

        # 6.3 "RIP" - Approved (hod_faculty)
        create_seed_resource(
            title="RIP",
            description="research Methodology",
            subject_code="23CS602",
            category="LECTURE_NOTES",
            sem=6,
            tags="research methodology, data science, literature review, hypothesis",
            orig_filename="Research_Methodology_RIP.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\nDEPARTMENT OF INFORMATION SCIENCE & ENGINEERING\nResearch Methodology & Intellectual Property Rights\nModule 1: Research problem formulation, hypothesis generation, and literature survey.",
            uploader=user_hod_faculty,
            is_app=True,
            status="Approved",
            downloads=320
        )

        # 6.4 "Impact of Social Media" - Approved (test_faculty)
        res_social_media = create_seed_resource(
            title="Impact of Social Media",
            description="The impact of social media on Adolescent Mental Health: A Systematic Review (Health/Psychology)",
            subject_code="23CS602",
            category="REFERENCE_BOOK",
            sem=6,
            tags="social media, systematic review, health psychology, ai ds, data analytics",
            orig_filename="Impact_of_Social_Media_Systematic_Review.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING (Autonomous)\nDEPARTMENT OF INFORMATION SCIENCE & ENGINEERING\nAcademic Literature Study: The Impact of Social Media on Adolescent Mental Health: A Systematic Review.\nAnalysis of statistical correlations, cross-sectional cohort studies, and data modeling.",
            uploader=user_test_faculty,
            is_app=True,
            status="Approved",
            downloads=290
        )

        # 7. CURRICULUM RESOURCES (DataLoader / localhost:5173 series)
        # 7.1 Sem 1: C Programming Lecture Notes
        create_seed_resource(
            title="25CS101: Principles of Programming using C Comprehensive Lecture Notes & Syntax Reference",
            description="Module 1 to Module 5 complete lecture handouts for 25CS Scheme: Flowcharts, modular C architecture, pointers arithmetic, dynamic memory allocation (malloc/calloc).",
            subject_code="25CS101",
            category="LECTURE_NOTES",
            sem=1,
            tags="25cs101, c programming, pointers, memory allocation, arrays",
            orig_filename="25CS101_MCE_C_Programming_Lecture_Notes.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n25CS SCHEME (AUTONOMOUS)\nCourse: 25CS101 - Principles of Programming using C\nModule 1: Flowcharts, control statements, loops, functions, and pointers.\nModule 2: Structures, unions, and low-level file I/O operations.",
            uploader=user_shashi,
            is_app=True,
            status="Approved",
            downloads=410
        )

        # 7.2 Sem 1: Computer Programming Lab Manual
        create_seed_resource(
            title="25CSL102: Computer Programming Laboratory Official Manual & Program Scripts",
            description="Laboratory syllabus guidelines containing 12 prescribed experiments: Matrix multiplication with pointers, student record system with binary file operations.",
            subject_code="25CSL102",
            category="LAB_MANUAL",
            sem=1,
            tags="25csl102, c lab manual, algorithms, linux terminal, gcc compiler",
            orig_filename="25CSL102_MCE_Programming_Lab_Manual.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n25CS SCHEME AUTONOMOUS LABORATORY GUIDE\nCourse: 25CSL102 - Computer Programming Laboratory\nPrescribed syllabus programs with GCC compilation and GDB debugging commands.",
            uploader=user_shashi,
            is_app=True,
            status="Approved",
            downloads=385
        )

        # 7.3 Sem 3: Data Structures Lab Manual
        create_seed_resource(
            title="24CSL306: Data Structures Laboratory Official Manual & Program Solutions",
            description="Complete laboratory guidebook for 24CS Scheme containing step-by-step problem statements, algorithms, and modular implementations for all prescribed syllabus experiments.",
            subject_code="24CSL306",
            category="LAB_MANUAL",
            sem=3,
            tags="24cs304, 24csl306, data structures, stacks, queues, bst, linked list",
            orig_filename="24CSL306_MCE_Data_Structures_Lab_Manual.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n24CS SCHEME LABORATORY MANUAL: 24CSL306 - Data Structures Laboratory\nProgram 1: Array representation of Stack with push/pop.\nProgram 2: Binary Search Tree traversals.\nProgram 3: Graph BFS/DFS.",
            uploader=user_shashi,
            is_app=True,
            status="Approved",
            downloads=342
        )

        # 7.4 Sem 3: Operating Systems Architecture Notes
        create_seed_resource(
            title="24CS303: Operating Systems Architecture Lecture Notes - Process Synchronization & Virtual Memory",
            description="Comprehensive departmental lecture slides and notes for 24CS Scheme covering Module 2 and Module 3: POSIX process fork/exec, IPC shared memory, Peterson's algorithm, Mutex semaphores.",
            subject_code="24CS303",
            category="LECTURE_NOTES",
            sem=3,
            tags="24cs303, operating systems, semaphores, deadlocks, virtual memory, paging",
            orig_filename="24CS303_MCE_Operating_Systems_Lecture_Notes.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n24CS SCHEME: 24CS303 - Operating Systems Architecture\nUnit 2: Process Management and Thread Synchronization\nUnit 3: Deadlock Characterization & Banker's Safety Algorithm\nUnit 4: Memory Management, Multi-level Paging.",
            uploader=user_hod,
            is_app=True,
            status="Approved",
            downloads=298
        )

        # 7.5 Sem 4: Algorithms Lab Manual
        create_seed_resource(
            title="24CSL405: Design and Analysis of Algorithms Laboratory Manual & Benchmark Suite",
            description="Autonomous laboratory manual featuring Java implementations and empirical time complexity benchmarking for Quick Sort, Merge Sort, Dijkstra's Single Source Shortest Path, Kruskal's MST.",
            subject_code="24CSL405",
            category="LAB_MANUAL",
            sem=4,
            tags="24cs402, 24csl405, algorithms, divide and conquer, dynamic programming, dijkstra",
            orig_filename="24CSL405_MCE_Algorithms_Lab_Manual.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING (Autonomous)\n24CS SCHEME COURSE: 24CSL405 - Design and Analysis of Algorithms Laboratory\n1. Quick Sort & Merge Sort with asymptotic timing analysis.\n2. Dijkstra's Algorithm for single source shortest path.\n3. Kruskal's algorithm with Disjoint-Set union-find.\n4. 0/1 Knapsack & Floyd-Warshall.",
            uploader=user_uma,
            is_app=True,
            status="Approved",
            downloads=421
        )

        # 7.6 Sem 4: DBMS Solved Question Paper
        create_seed_resource(
            title="24CS403: Database Management Systems Autonomous End-Semester Question Bank with Solved Keys",
            description="Compilation of previous autonomous end-semester examination papers with detailed solutions: ER diagrams to relational schemas mapping, complex SQL nested queries, BCNF / 3NF decomposition.",
            subject_code="24CS403",
            category="PREVIOUS_QUESTION_PAPER",
            sem=4,
            tags="24cs403, dbms, question paper, sql queries, normalization, bcnf",
            orig_filename="24CS403_MCE_DBMS_Solved_Question_Paper.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n24CS SCHEME End Semester Examination Solved Question Bank\nCourse: 24CS403 - Database Management Systems\nModule 1: ER modeling.\nModule 2: Relational Algebra & SQL subqueries.\nModule 3: Normalization 1NF, 2NF, 3NF, BCNF.\nModule 4: ACID properties and 2PL protocols.",
            uploader=user_uma,
            is_app=True,
            status="Approved",
            downloads=387
        )

        # 7.7 Sem 5: Computer Networks Lab Manual
        create_seed_resource(
            title="23CSL505: Computer Networks Laboratory Manual - Socket Programming & Packet Tracer Topologies",
            description="Department lab manual with complete source code for multi-client TCP iterative/concurrent servers, UDP ping utilities, sliding window protocol simulation.",
            subject_code="23CSL505",
            category="LAB_MANUAL",
            sem=5,
            tags="23cs502, 23csl505, computer networks, socket programming, tcp, udp, packet tracer",
            orig_filename="23CSL505_MCE_Computer_Networks_Lab_Manual.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING\n23CS SCHEME: 23CSL505 - Computer Networks Laboratory\nExperiments:\n1. Multi-threaded TCP client-server echo application.\n2. Simulation of Sliding Window flow control (Go-Back-N).\n3. Cisco Packet Tracer configuration for VLANs.",
            uploader=user_geetha,
            is_app=True,
            status="Approved",
            downloads=264
        )

        # 7.8 Sem 6: Compiler Design Notes
        create_seed_resource(
            title="23CS601: Compiler Design Comprehensive Lecture Notes - Lexical Analysis & LALR Parser Guide",
            description="Module 1 to Module 4 notes detailing Flex lexical specification, predictive LL(1) parsing table construction, LR(0), SLR(1), and LALR(1) item sets.",
            subject_code="23CS601",
            category="LECTURE_NOTES",
            sem=6,
            tags="23cs601, compiler design, flex, bison, ll1, lalr, three address code",
            orig_filename="23CS601_MCE_Compiler_Design_Lecture_Notes.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n23CS SCHEME: 23CS601 - Compiler Design\nInstructor: Dr. Ananda Babu J.\nUnit 1: Lexical Analysis with Regular Expressions.\nUnit 2: Syntax Analysis - Left Recursion removal, FIRST & FOLLOW.\nUnit 3: LR Parsing tables (SLR, Canonical LR, LALR).",
            uploader=user_hod,
            is_app=True,
            status="Approved",
            downloads=319
        )

        # 7.9 Sem 6: Machine Learning Lab Manual
        create_seed_resource(
            title="23CSL605: Machine Learning Laboratory Official Manual with Working Python Scripts",
            description="Prescribed laboratory manual with working Python scripts and Jupyter notebooks: Candidate Elimination algorithm, ID3 Decision Tree induction, Naive Bayes classifier, SVM, and k-Means.",
            subject_code="23CSL605",
            category="LAB_MANUAL",
            sem=6,
            tags="23cs602, 23csl605, machine learning, python, id3, naive bayes, svm, knn",
            orig_filename="23CSL605_MCE_Machine_Learning_Lab_Manual.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN\n23CS SCHEME: 23CSL605 - Machine Learning Laboratory\nInstructor Incharge: Dr. Keerthi Kumar H.M.\nExperiment 1: Candidate Elimination algorithm.\nExperiment 2: ID3 Decision Tree with entropy.\nExperiment 3: Naive Bayes text classifier.\nExperiment 4: Support Vector Machine (SVM) kernels.\nExperiment 5: k-Means clustering.",
            uploader=user_keerthi,
            is_app=True,
            status="Approved",
            downloads=412
        )

        # 7.10 Sem 6: Cryptography & Security Lab Manual
        create_seed_resource(
            title="23CS603: Cryptography & Network Security Protocol Implementation Manual",
            description="Practical laboratory exercises and guidelines for symmetric AES-128 encryption, RSA key generation & digital signatures, Diffie-Hellman Key Exchange, SHA-256 digests.",
            subject_code="23CS603",
            category="SOFTWARE_TOOL_GUIDE",
            sem=6,
            tags="23cs603, cryptography, aes, rsa, diffie hellman, sha256, openssl",
            orig_filename="23CS603_MCE_Cryptography_Lab_Guide.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING\n23CS SCHEME: 23CS603 - Cryptography & Network Security\nLab exercises:\n1. AES symmetric cipher implementation.\n2. RSA public key encryption.\n3. Diffie-Hellman Key Exchange simulation.\n4. SHA-256 and OpenSSL certificates.",
            uploader=user_geetha,
            is_app=True,
            status="Approved",
            downloads=275
        )

        # 7.11 Sem 8: Capstone Project Phase-II Guidelines
        create_seed_resource(
            title="23CS801: Autonomous Major Project Work Phase-II Implementation & Rubrics Guide 2026-27",
            description="Official departmental handbook and rubrics for 8th Semester Capstone Project Work Phase-II (2026-2027 academic year). Includes SRS templates, system architecture diagrams, continuous evaluation rubrics.",
            subject_code="23CS801",
            category="PROJECT_REPO",
            sem=8,
            tags="23cs801, project, capstone, phase 2, dissertation, rubrics, ieee",
            orig_filename="23CS801_MCE_Major_Project_Guidelines.pdf",
            file_content="MALNAD COLLEGE OF ENGINEERING, HASSAN (Autonomous Institution)\nDEPARTMENT RESOURCE REPOSITORY\nCOURSE CODE: 23CS801 - MAJOR PROJECT WORK (PHASE-II) & VIVA\n1. TIMELINE & MILESTONES (EVEN SEMESTER 2026-27)\n2. EVALUATION RUBRICS & IEEE PAPER FORMATTING GUIDELINES.\nCoordinators: Dr. Keerthi Kumar H.M. / HOD: Dr. Ananda Babu J.",
            uploader=user_hod,
            is_app=True,
            status="Approved",
            downloads=189
        )

        # 8. Sample Resource Request (from Meghana)
        ResourceRequest.objects.get_or_create(
            user=user_meghana,
            resource_name="Previous 5 Years Question Papers with Answer Key for 23CS601 Compiler Design",
            defaults={
                "subject": "23CS601 Compiler Design",
                "semester": 6,
                "description": "Requesting solved question papers for internal assessment and semester end examination revision.",
                "status": "PENDING"
            }
        )

        # 9. Create Django Admin Log Entries matching Figure 6.2.4 "Recent actions"
        # In Figure 6.2.4:
        # shruthi (User profile)
        # shruthi: faculty (User profile)
        # apeksha: admin (User)
        # apeksha (User)
        # nithin: faculty (User)
        # nithin: faculty: faculty (User profile)
        # meghana: student (User)
        # meghana: student (User profile)
        # Impact of Social Media (Resource)
        if not LogEntry.objects.filter(user=user_apeksha).exists():
            user_ct = ContentType.objects.get_for_model(User)
            profile_ct = ContentType.objects.get_for_model(UserProfile)
            res_ct = ContentType.objects.get_for_model(Resource)

            actions = [
                (profile_ct, str(user_shruthi.profile.id), "shruthi", ADDITION),
                (profile_ct, str(user_shruthi.profile.id), "shruthi: faculty", CHANGE),
                (user_ct, str(user_apeksha.id), "apeksha: admin", CHANGE),
                (user_ct, str(user_apeksha.id), "apeksha", ADDITION),
                (user_ct, str(user_nithin.id), "nithin: faculty", ADDITION),
                (profile_ct, str(user_nithin.profile.id), "nithin: faculty: faculty", CHANGE),
                (user_ct, str(user_meghana.id), "meghana: student", ADDITION),
                (profile_ct, str(user_meghana.profile.id), "meghana: student", CHANGE),
                (profile_ct, str(user_meghana.profile.id), "meghana: student - student", CHANGE),
                (res_ct, str(res_social_media.id), "Impact of Social Media", ADDITION),
            ]

            for ct, obj_id, repr_str, action in actions:
                LogEntry.objects.create(
                    action_time=timezone.now(),
                    user=user_apeksha,
                    content_type=ct,
                    object_id=obj_id,
                    object_repr=repr_str,
                    action_flag=action,
                    change_message="Created/updated in admin portal"
                )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with authentic MCE Hassan portal data!"))

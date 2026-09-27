# 🚀 DevConnect API – Backend REST Platform

[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-3.18-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/JWT-Authentication-black?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Postman](https://img.shields.io/badge/Postman-Automated_Tests-FF6C37?style=for-the-badge&logo=postman&logoColor=white)](https://www.postman.com/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0_Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://swagger.io/)
[![Tests](https://img.shields.io/badge/Automated_Tests-25_Passed-success?style=for-the-badge&logo=pytest&logoColor=white)]()

A high-performance, stateless backend REST ecosystem engineered for developers to showcase repositories, publish code snippets, network across professional connections, and discover collaborative software projects.

---

## 🌟 Key Architecture & Highlights

- **Secure, Stateless Backend Ecosystem**: Engineered with Django REST Framework and PostgreSQL, structured across modular domain apps (`accounts`, `projects`, `posts`, `notifications`).
- **JWT Authentication & Role-Based Authorization (RBAC)**: Custom JWT payload claims (`username`, `email`, `role`, `headline`), access token rotation, and refresh token blacklisting on logout. Granular permission classes (`IsOwnerOrReadOnly`, `IsDeveloper`, `IsRecruiter`, `IsAdminUserOnly`).
- **Repository Mapping & Social Network**: Rich developer profiles with tech stack skills, repository mapping (`repo_url`, `github_repo_name`, demo link), social follow graph, and two-way developer connection request lifecycle.
- **Advanced Database Optimization & Lookups**: Server-side custom pagination (`StandardResultsSetPagination`), multi-field conditional filtering (`django-filter`), and indexing with full lookup search on titles, descriptions, tags, and skills.
- **Automated API Testing & Postman Workflows**: Comprehensive 25+ automated test suite validating request boundaries, payload schemas, edge cases, object permissions, and HTTP status codes (200, 201, 400, 401, 403, 404).

---

## 📸 Visual Showcase & API Validation

### 🧪 1. Postman Automated Test Suite Runner (100% Passed)
> Automated execution of 27 boundary tests, schema assertions, and HTTP status validations in $<2.3\text{s}$.

![Postman Automated Test Runner](screenshots/DevConnect%20Automated%20Test%20Suite%20Collection%20-%20result.png)

---

### 📖 2. Interactive Swagger UI (OpenAPI 3.0)
> Auto-generated interactive API schema documentation powered by `drf-spectacular`.

![Swagger UI Documentation](screenshots/Interactive%20Swagger%20%20OpenAPI%20Documentation.png)

---

### 🔐 3. JWT Authentication with Custom Claims (200 OK)
> Stateless session initiation issuing `access` and `refresh` tokens with decoded user role metadata.

![JWT Login with Custom Claims](screenshots/JWT%20Login%20with%20Custom%20Claims%20-%20res%20200.png)

---

### ⚡ 4. Server-Side Pagination & Conditional Filtering
> Multi-criteria database query filtering (`min_stars=5&project_type=API`) with nested M2M `tech_stack` relation mapping.

![Server-Side Pagination and Filtering](screenshots/Server-Side%20Pagination%20%26%20Conditional%20Filtering%20-%20res%20json.png)

---

### 🛡️ 5. Object-Level RBAC Permission Boundary (403 Forbidden)
> Enforcing strict ownership rules (`IsOwnerOrReadOnly`) preventing unauthorized edits by non-owners.

![403 Forbidden Permission Boundary](screenshots/RoleOwnership%20Boundary%20Test%20(403%20Forbidden).png)

---

## 🏛️ System Architecture

![System Architecture](screenshots/System%20Architecture%20ASD.png)

---

## 📚 API Endpoints Reference

### 🔐 1. Authentication & Session Management
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register new user & receive initial JWT token pair | No |
| `POST` | `/api/auth/login/` | Obtain JWT token pair (`access`, `refresh`) + custom claims | No |
| `POST` | `/api/auth/token/refresh/` | Refresh expired JWT access token | No |
| `POST` | `/api/auth/logout/` | Blacklist refresh token and terminate session | **Yes (JWT)** |
| `POST` | `/api/auth/change-password/` | Secure password change | **Yes (JWT)** |

### 👨‍💻 2. Developer Profiles & Social Network
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` / `PATCH` | `/api/auth/me/` | Retrieve or update current authenticated profile | **Yes (JWT)** |
| `GET` | `/api/auth/developers/` | List/search developers with skill & location filtering | No |
| `GET` | `/api/auth/developers/<username>/` | Retrieve public profile of a developer | No |
| `POST` | `/api/auth/developers/<username>/follow/` | Follow or unfollow a developer | **Yes (JWT)** |
| `GET` | `/api/auth/developers/<username>/followers/` | List all followers of a developer | No |
| `GET` | `/api/auth/developers/<username>/following/` | List developers followed by user | No |
| `GET` / `POST` | `/api/auth/skills/` | List standard tech skills or create new skill | No / Auth |
| `GET` / `POST` | `/api/auth/connections/` | List connection requests or send new request | **Yes (JWT)** |
| `POST` | `/api/auth/connections/<id>/<accept|reject>/` | Accept or reject a connection request | **Yes (JWT)** |

### 📦 3. Projects & Repository Mapping
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/projects/` | List projects (server-side pagination, search, filters) | No |
| `POST` | `/api/projects/` | Publish new project repository mapping | **Yes (JWT)** |
| `GET` | `/api/projects/trending/` | Get top 10 trending projects by star count | No |
| `GET` | `/api/projects/<slug>/` | Retrieve project detail (increments view count) | No |
| `PATCH` / `DELETE` | `/api/projects/<slug>/` | Update or delete project | **Owner Only** |
| `POST` | `/api/projects/<slug>/star/` | Star or unstar a project | **Yes (JWT)** |
| `GET` / `POST` | `/api/projects/<slug>/comments/` | List or submit comments on a project | No / Auth |
| `DELETE` | `/api/projects/comments/<id>/` | Delete a comment | **Owner Only** |

### 💬 4. Social Feed & Code Discussions
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/posts/` | Global developer feed with code search | No |
| `POST` | `/api/posts/` | Publish new discussion post with code snippet | **Yes (JWT)** |
| `GET` | `/api/posts/feed/` | Personalized feed of followed developers | **Yes (JWT)** |
| `GET` / `DELETE` | `/api/posts/<id>/` | Retrieve or delete discussion post | No / Owner |
| `POST` | `/api/posts/<id>/like/` | Like or unlike a post | **Yes (JWT)** |
| `GET` / `POST` | `/api/posts/<id>/comments/` | List or post comments on discussion | No / Auth |

### 🔔 5. Notifications
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/notifications/` | List notifications for authenticated user | **Yes (JWT)** |
| `GET` | `/api/notifications/unread-count/` | Get unread notification counter | **Yes (JWT)** |
| `PATCH` | `/api/notifications/<id>/read/` | Mark specific notification as read | **Yes (JWT)** |
| `POST` | `/api/notifications/mark-all-read/` | Mark all notifications as read | **Yes (JWT)** |

---

## ⚡ Quickstart & Local Setup

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/PARTTTHH/DevConnect-API.git
cd DevConnect-API

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(By default, if PostgreSQL credentials are not provided, it seamlessly runs on SQLite for instant zero-config testing).*

### 3. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_db
```

### 4. Start Development Server
```bash
python manage.py runserver
```
Navigate to:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc Documentation**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **API Root**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- **Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Automated Testing Suite

### Running Django Automated Tests
```bash
python manage.py test
```
**Output:**
```text
Creating test database for alias 'default'...
.........................
----------------------------------------------------------------------
Ran 25 tests in 8.348s

OK
```

### Running with Postman Automated Workflows
1. Import `DevConnect_API.postman_collection.json` into Postman.
2. Import `DevConnect_API.postman_environment.json`.
3. Select the `DevConnect Local Environment`.
4. Click **Run Collection** to execute all automated test scenarios (validating request boundaries, JWT token rotation, 401/403/400 error handlers, and response schemas).

---

## 📂 Project Structure

```text
DevConnect-API/
├── core/                       # Project settings, URL gateway, pagination & permissions
│   ├── settings.py             # App configuration, JWT lifetimes & DB switcher
│   ├── urls.py                 # Master URL configuration & OpenAPI docs
│   ├── permissions.py          # Custom RBAC (IsOwnerOrReadOnly, IsDeveloper, IsRecruiter)
│   ├── pagination.py           # Standard & Large server-side pagination classes
│   └── exceptions.py           # Standardized JSON error response handler
├── accounts/                   # User model, profiles, skills, follow & connection graph
│   ├── models.py               # User, Skill, Follow, ConnectionRequest models
│   ├── serializers.py          # JWT custom claims serializer & Profile serializers
│   ├── views.py                # Auth, Profile, Follow, Connection endpoints
│   └── tests.py                # Auth & RBAC test suite
├── projects/                   # Repository mapping, project showcase & stars
│   ├── models.py               # Project, ProjectStar, ProjectComment models
│   ├── filters.py              # django-filter multi-attribute filter sets
│   ├── serializers.py          # Project CRUD and nested comment serializers
│   ├── views.py                # Pagination, Search, Trending & Star views
│   └── tests.py                # Project CRUD, filtering & ownership tests
├── posts/                      # Developer social feed, code snippets & discussions
│   ├── models.py               # Post, PostLike, PostComment models
│   ├── serializers.py          # Post & snippet serializers
│   ├── views.py                # Global and personalized feed views
│   └── tests.py                # Feed & Like test suite
├── notifications/              # In-app notification dispatch & tracking
├── DevConnect_API.postman_collection.json    # Automated Postman test collection
├── DevConnect_API.postman_environment.json   # Postman environment variables
├── requirements.txt            # Pinned dependencies
├── manage.py                   # Django management entrypoint
└── README.md                   # Comprehensive project documentation
```

---

## 👤 Author

**PARTH PUNGAONKAR**

- GitHub: [@PARTTTHH](https://github.com/PARTTTHH)
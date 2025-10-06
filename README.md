# 🧩 FFEO Framework

> A lightweight educational web framework inspired by Flask — built entirely with Python’s standard library.

⚠️ **Note:** This project is for **educational purposes only**. It aims to teach the core concepts behind web frameworks like Flask, including routing, templating, and request handling.

---

## 🌐 Core Components

- 🧭 **Routing System** using decorator syntax (`@app.route()`)
- 🧱 **Template Engine** supporting:
  - `{{ variables }}`
  - `{% if %}` and `{% for %}` control structures
- ⚙️ **HTTP Server** built on Python’s `http.server`
- 📦 **Request/Response Objects** for managing HTTP interactions
- 🔗 **URL Parameter Extraction** (e.g., `/user/<username>`)
- 🚫 **Custom Error Handlers** (e.g., 404 pages)

---

## 🗂️ Project Structure

```

your_project/
├── FFEO.py           # The framework
├── app.py            # Your application
└── templates/
     └── index.html

````

---

## ▶️ How to Run

1. Run your application:

```bash
   python app.py
````

2. Open your browser and go to:
   👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ✨ Supported Features

✅ Multiple routes with decorators

✅ Dynamic URL parameters (`/user/<username>`)

✅ Template rendering with variables

✅ Custom error handlers

✅ Support for HTTP methods (`GET`, `POST`, `PUT`, `DELETE`)

✅ Query string parsing

✅ Debug mode




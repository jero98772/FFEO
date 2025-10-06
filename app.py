"""
app.py - Example application using the Feo framework
"""

from FFEO import Feo, render_template

app = Feo(__name__)

@app.route("/")
def home():
    return render_template("index.html", name="Jero")

@app.route("/about")
def about():
    return """
    <html>
        <head><title>About</title></head>
        <body>
            <h1>About Page</h1>
            <p>This is a minimal Flask-like framework built from scratch!</p>
            <a href="/">Go Home</a>
        </body>
    </html>
    """

@app.route("/user/<username>")
def user_profile(username):
    return render_template("user.html", username=username)

@app.route("/api/data")
def api_data():
    return """
    {
        "status": "success",
        "data": {
            "message": "Hello from Feo API!"
        }
    }
    """

@app.errorhandler(404)
def not_found():
    return """
    <html>
        <head><title>404 - Not Found</title></head>
        <body>
            <h1>Page Not Found</h1>
            <p>Sorry, the page you're looking for doesn't exist.</p>
            <a href="/">Go Home</a>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)

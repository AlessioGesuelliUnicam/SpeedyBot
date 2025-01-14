from app import create_app
import sys, os, platform
from flask import jsonify

app = create_app()

@app.route("/api/restart-backend", methods=["POST"])
def restart_backend():
    try:
        # Clear the terminal
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        # Restart the server
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Restarting..."})

if __name__ == "__main__":
    app.run(debug=True)

# Start the application
if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
print(app.url_map)
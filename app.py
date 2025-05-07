from flask import Flask, redirect,render_template
import smartPotDisplay
app = Flask(__name__)

@app.route("/")
def display():
    return render_template("display.html")


if __name__ == "__main__":
    app.run(debug=True)
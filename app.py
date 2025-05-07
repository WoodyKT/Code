from flask import Flask, redirect,render_template
import smartPotDisplay
app = Flask(__name__)

@app.route("/")
def display():
    weather = "cloud"
    humidity = "red"
    moisture = "red"
    waterLevel = "red"
    light = "red"
    temperature = "red"
    return render_template("display.html",weather = weather, humidity = humidity, moisture = moisture, waterLevel = waterLevel, light = light, temperature = temperature)


if __name__ == "__main__":
    app.run(debug=True)
from flask import *
from pickle import load

f=open("model.pkl","rb")
model=load(f)
f.close()


app= Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        glucose = int(request.form.get("PM 1.0"))
        bp = int(request.form.get("PM 2.5"))
        skin = int(request.form.get("PM 10.0"))
        insulin = float(request.form.get("Temperature"))
        bmi = float(request.form.get("Humidity"))
        dpf = float(request.form.get("Gas Resistance"))

        prediction = model.predict([[glucose, bp, skin, insulin, bmi, dpf]])
        msg = f"Predicted AQI: {int(round(prediction[0]))}"
        
        flash(msg, 'success')
        return redirect(url_for('home'))

    return render_template("home.html")


if __name__=="__main__":
    app.run(debug=True,use_reloader=True)
#imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
Scss(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(100), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    created = db.Column(db.DateTime, default = datetime.utcnow)
    newURL = db.Column(db.String(100), nullable = False, unique=True)

    def  __repr__(self) -> str:
        return f"Task {self.id}"


with app.app_context():
    db.create_all()


@app.route("/", methods = ["POST", "GET"])
def index():
    #add a task "POST"
    if request.method == "POST":
        current_task = request.form['content']
        new_task = MyTask(content = current_task, newURL="")
        #store the retrieved data into database
        try:
            db.session.add(new_task)
            db.session.commit()

            new_task.newURL = f"/shorten/{new_task.id}"
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"Error:{e}")
            return f"Error:{e}"

    #retrieve data "GET"
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template("index.html", tasks = tasks)


#delete button
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error:{e}"



#edit button
@app.route("/update/<int:id>", methods=["GET", "POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error:{e}"
    else:
        return render_template('edit.html', task = task)


@app.route("/shorten/<int:id>")
def reroute(id: int):
    # Retrieve the URL by its ID
    url_record = MyTask.query.get_or_404(id)
    original_url = url_record.content

    # Ensure the URL is absolute (starts with "http://" or "https://")
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url + ".com" # Default to HTTPS

    return redirect(original_url)




#runner and debugger
if __name__ == "__main__":
    app.run(debug=True)
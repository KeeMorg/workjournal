
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    entry_date = db.Column(db.String(120), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_entry = Entry(
            user=request.form['user'],
            title=request.form['title'],
            content=request.form['content'],
            entry_date=datetime.now().strftime("%b. %d, %Y, %I:%M %p")
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))

    entries = Entry.query.all()
    return render_template('index.html', entries=entries)

@app.route('/export/pdf')
def export_pdf():
    entries = Entry.query.all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y_position = height - 30
    for entry in entries:
        p.drawString(30, y_position, f"Title: {entry.title}")
        p.drawString(30, y_position - 20, f"User: {entry.user}")
        p.drawString(30, y_position - 40, f"Date: {entry.entry_date}")
        p.drawString(30, y_position - 60, f"Content: {entry.content}")
        y_position -= 100

        if y_position < 100:
            p.showPage()
            y_position = height - 30

    p.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=journal_entries.pdf'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
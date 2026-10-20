import os
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    copies = db.Column(db.Integer, default=1)  # copies currently on the shelf


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    issue_date = db.Column(db.Date, default=date.today)
    return_date = db.Column(db.Date, nullable=True)

    book = db.relationship("Book")
    member = db.relationship("Member")


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///library.db")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    if config:
        app.config.update(config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/")
    def books():
        return render_template("books.html", books=Book.query.order_by(Book.title).all())

    @app.route("/books/add", methods=["POST"])
    def add_book():
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        copies = int(request.form.get("copies", 1))
        if title and author:
            db.session.add(Book(title=title, author=author, copies=copies))
            db.session.commit()
        return redirect(url_for("books"))

    @app.route("/books/<int:book_id>/delete", methods=["POST"])
    def delete_book(book_id):
        db.session.delete(db.get_or_404(Book, book_id))
        db.session.commit()
        return redirect(url_for("books"))

    @app.route("/members", methods=["GET", "POST"])
    def members():
        if request.method == "POST":
            db.session.add(Member(name=request.form["name"].strip(),
                                  email=request.form["email"].strip()))
            db.session.commit()
            return redirect(url_for("members"))
        return render_template("members.html", members=Member.query.all())

    @app.route("/issues", methods=["GET", "POST"])
    def issues():
        if request.method == "POST":
            book = db.get_or_404(Book, int(request.form["book_id"]))
            member = db.get_or_404(Member, int(request.form["member_id"]))
            if book.copies < 1:
                flash("No copies of this book are available.")
            else:
                book.copies -= 1
                db.session.add(Issue(book_id=book.id, member_id=member.id))
                db.session.commit()
            return redirect(url_for("issues"))
        return render_template("issues.html",
                               issues=Issue.query.order_by(Issue.id.desc()).all(),
                               books=Book.query.all(), members=Member.query.all())

    @app.route("/issues/<int:issue_id>/return", methods=["POST"])
    def return_book(issue_id):
        issue = db.get_or_404(Issue, issue_id)
        if issue.return_date is None:
            issue.return_date = date.today()
            issue.book.copies += 1
            db.session.commit()
        return redirect(url_for("issues"))

    return app


app = create_app() if os.getenv("CREATE_APP_ON_IMPORT", "1") == "1" else None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Open")  # Open, In Progress, Resolved
    resolution_notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

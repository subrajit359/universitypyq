from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    papers = db.relationship('Paper', foreign_keys='Paper.uploaded_by_id', backref='uploaded_by', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_stats(self):
        """Get user statistics"""
        paper_list = list(self.papers)
        total_uploads = len(paper_list)
        approved_uploads = len([p for p in paper_list if p.is_approved])
        total_downloads = sum(p.download_count for p in paper_list if p.is_approved)
        bookmark_list = list(self.bookmarks)
        total_bookmarks = len(bookmark_list)
        
        return {
            'total_uploads': total_uploads,
            'approved_uploads': approved_uploads,
            'total_downloads': total_downloads,
            'total_bookmarks': total_bookmarks
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Paper(db.Model):
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    semester = db.Column(db.String(50), nullable=False, index=True)
    exam_type = db.Column(db.String(50), default='Regular', nullable=False)
    college = db.Column(db.String(200))
    course = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_format = db.Column(db.String(10), nullable=False)
    cloudinary_url = db.Column(db.String(500))
    cloudinary_public_id = db.Column(db.String(255))
    
    # Status and metadata
    is_approved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    approval_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    download_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Foreign keys
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    bookmarks = db.relationship('Bookmark', backref='paper', lazy=True, cascade='all, delete-orphan')
    
    def get_file_size_formatted(self):
        """Get formatted file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        db.session.commit()
    
    def approve(self, admin_user):
        """Approve the paper"""
        self.is_approved = True
        self.approval_date = datetime.utcnow()
        self.approved_by_id = admin_user.id
        db.session.commit()
    
    def reject(self, admin_user, reason):
        """Reject the paper"""
        self.rejection_reason = reason
        db.session.commit()
    
    def __repr__(self):
        return f'<Paper {self.title}>'

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate bookmarks
    __table_args__ = (db.UniqueConstraint('user_id', 'paper_id', name='unique_user_paper_bookmark'),)
    
    def __repr__(self):
        return f'<Bookmark User:{self.user_id} Paper:{self.paper_id}>'

def get_unique_subjects():
    """Get list of unique subjects from approved papers"""
    return [subject[0] for subject in db.session.query(Paper.subject.distinct()).filter(Paper.is_approved == True).all()]

def get_unique_years():
    """Get list of unique years from approved papers"""
    return sorted([year[0] for year in db.session.query(Paper.year.distinct()).filter(Paper.is_approved == True).all()], reverse=True)

def get_unique_semesters():
    """Get list of unique semesters from approved papers"""
    return [semester[0] for semester in db.session.query(Paper.semester.distinct()).filter(Paper.is_approved == True).all()]

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 star rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Optional: Link to user if they're logged in
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='feedback_submissions')
    
    def __repr__(self):
        return f'<Feedback {self.subject} by {self.name}>'

def get_admin_stats():
    """Get admin dashboard statistics"""
    total_papers = Paper.query.count()
    approved_papers = Paper.query.filter(Paper.is_approved == True).count()
    pending_papers = Paper.query.filter(Paper.is_approved == False).count()
    total_users = User.query.count()
    total_downloads = db.session.query(db.func.sum(Paper.download_count)).scalar() or 0
    
    return {
        'total_papers': total_papers,
        'approved_papers': approved_papers,
        'pending_papers': pending_papers,
        'total_users': total_users,
        'total_downloads': total_downloads
    }
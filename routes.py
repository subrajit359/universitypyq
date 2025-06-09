import os
import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, abort, send_file, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from app import db
from models import User, Paper, Bookmark, Feedback, get_unique_subjects, get_unique_years, get_unique_semesters, get_admin_stats
import cloudinary
import cloudinary.uploader

# Configure logging
logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=app.config.get('CLOUDINARY_API_KEY'),
        api_secret=app.config.get('CLOUDINARY_API_SECRET')
    )
    
    def admin_required(f):
        """Decorator to require admin access"""
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash('Admin access required.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    @app.route('/')
    def index():
        """Home page with paper search and listing"""
        # Get search parameters
        search_query = request.args.get('search', '').strip()
        subject_filter = request.args.get('subject', 'all')
        year_filter = request.args.get('year', 'all')
        semester_filter = request.args.get('semester', 'all')
        
        # Build query for approved papers only
        query = Paper.query.filter_by(is_approved=True)
        
        # Apply search filters
        if search_query:
            search_terms = or_(
                Paper.title.ilike(f'%{search_query}%'),
                Paper.subject.ilike(f'%{search_query}%'),
                Paper.college.ilike(f'%{search_query}%'),
                Paper.description.ilike(f'%{search_query}%')
            )
            query = query.filter(search_terms)
        
        if subject_filter != 'all':
            query = query.filter_by(subject=subject_filter)
        
        if year_filter != 'all':
            query = query.filter_by(year=int(year_filter))
        
        if semester_filter != 'all':
            query = query.filter_by(semester=semester_filter)
        
        # Get results ordered by upload date
        papers = query.order_by(Paper.upload_date.desc()).all()
        
        # Get filter options
        subjects = get_unique_subjects()
        years = get_unique_years()
        semesters = get_unique_semesters()
        
        # Get user bookmarks if authenticated
        user_bookmarks = []
        if current_user.is_authenticated:
            user_bookmarks = [b.paper_id for b in current_user.bookmarks]
        
        return render_template('index.html',
                             papers=papers,
                             subjects=subjects,
                             years=years,
                             semesters=semesters,
                             search_query=search_query,
                             subject_filter=subject_filter,
                             year_filter=year_filter,
                             semester_filter=semester_filter,
                             user_bookmarks=user_bookmarks)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username_or_email = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username_or_email or not password:
                flash('Please fill in all fields.', 'error')
                return render_template('login.html')
            
            # Find user by username or email
            user = User.query.filter(
                or_(User.username == username_or_email, User.email == username_or_email)
            ).first()
            
            if user and user.check_password(password):
                user.last_login = datetime.utcnow()
                db.session.commit()
                login_user(user)
                flash(f'Welcome back, {user.first_name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid username/email or password.', 'error')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            errors = []
            
            if not all([first_name, last_name, username, email, password]):
                errors.append('All fields are required.')
            
            if len(username) < 3:
                errors.append('Username must be at least 3 characters long.')
            
            if len(password) < 6:
                errors.append('Password must be at least 6 characters long.')
            
            if password != confirm_password:
                errors.append('Passwords do not match.')
            
            # Check for existing users
            if User.query.filter_by(username=username).first():
                errors.append('Username already exists.')
            
            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('register.html')
            
            # Create new user
            try:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email
                )
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                logger.error(f'Registration error: {e}')
                flash('Registration failed. Please try again.', 'error')
                db.session.rollback()
        
        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        stats = current_user.get_stats()
        return render_template('profile.html', user=current_user, stats=stats)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload_paper():
        """Upload a new paper"""
        if request.method == 'POST':
            try:
                # Get form data
                title = request.form.get('title', '').strip()
                subject = request.form.get('subject', '').strip()
                year = request.form.get('year', type=int)
                semester = request.form.get('semester', '').strip()
                exam_type = request.form.get('exam_type', 'Regular').strip()
                college = request.form.get('college', '').strip()
                course = request.form.get('course', '').strip()
                description = request.form.get('description', '').strip()
                
                # Validation
                if not all([title, subject, year, semester]):
                    flash('Title, subject, year, and semester are required.', 'error')
                    return render_template('upload_paper.html')
                
                # Handle file upload
                if 'file' not in request.files:
                    flash('No file selected.', 'error')
                    return render_template('upload_paper.html')
                
                file = request.files['file']
                if file.filename == '':
                    flash('No file selected.', 'error')
                    return render_template('upload_paper.html')
                
                # Check file extension
                allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
                file_ext = os.path.splitext(secure_filename(file.filename or ''))[1].lower()
                
                if file_ext not in allowed_extensions:
                    flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG', 'error')
                    return render_template('upload_paper.html')
                
                # Upload to Cloudinary
                try:
                    # Create a unique filename without extension (Cloudinary adds it automatically)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_name = secure_filename(file.filename or '')
                    name_without_ext = os.path.splitext(original_name)[0]
                    cloudinary_filename = f"{current_user.username}_{timestamp}_{name_without_ext}"
                    
                    # Upload to Cloudinary
                    upload_result = cloudinary.uploader.upload(
                        file,
                        resource_type="raw",  # Use 'raw' for PDF and document files
                        public_id=cloudinary_filename,
                        folder="universitypyq/papers"
                    )
                    
                    # Create paper record with Cloudinary data
                    paper = Paper(
                        title=title,
                        subject=subject,
                        year=year,
                        semester=semester,
                        exam_type=exam_type,
                        college=college or None,
                        course=course or None,
                        description=description or None,
                        filename=secure_filename(file.filename or ''),
                        original_filename=file.filename or '',
                        file_size=upload_result.get('bytes', 0),
                        file_format=file_ext[1:],  # Remove the dot
                        cloudinary_url=upload_result.get('secure_url'),
                        cloudinary_public_id=upload_result.get('public_id'),
                        uploaded_by_id=current_user.id
                    )
                    
                except Exception as upload_error:
                    logger.error(f'Cloudinary upload error: {upload_error}')
                    flash('File upload failed. Please try again.', 'error')
                    return render_template('upload_paper.html')
                
                db.session.add(paper)
                db.session.commit()
                
                flash('Paper uploaded successfully! It will be reviewed by admins.', 'success')
                return redirect(url_for('my_uploads'))
                
            except Exception as e:
                logger.error(f'Upload error: {e}')
                flash('Upload failed. Please try again.', 'error')
                db.session.rollback()
        
        return render_template('upload_paper.html')
    
    @app.route('/my-uploads')
    @login_required
    def my_uploads():
        """User's uploaded papers"""
        papers = Paper.query.filter_by(uploaded_by_id=current_user.id).order_by(Paper.upload_date.desc()).all()
        return render_template('my_uploads.html', papers=papers)
    
    @app.route('/bookmarks')
    @login_required
    def bookmarks():
        """User's bookmarked papers"""
        bookmarked_papers = db.session.query(Paper).join(
            Bookmark, Paper.id == Bookmark.paper_id
        ).filter(
            Bookmark.user_id == current_user.id,
            Paper.is_approved == True
        ).order_by(Bookmark.created_at.desc()).all()
        
        return render_template('bookmarks.html', papers=bookmarked_papers)
    
    @app.route('/bookmark/<int:paper_id>', methods=['POST'])
    @login_required
    def toggle_bookmark(paper_id):
        """Toggle bookmark for a paper"""
        paper = Paper.query.get_or_404(paper_id)
        
        if not paper.is_approved:
            return jsonify({'error': 'Cannot bookmark unapproved paper'}), 400
        
        # Check if bookmark exists
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id,
            paper_id=paper_id
        ).first()
        
        try:
            if bookmark:
                # Remove bookmark
                db.session.delete(bookmark)
                db.session.commit()
                return jsonify({
                    'status': 'removed',
                    'message': 'Bookmark removed'
                })
            else:
                # Add bookmark
                bookmark = Bookmark(
                    user_id=current_user.id,
                    paper_id=paper_id
                )
                db.session.add(bookmark)
                db.session.commit()
                return jsonify({
                    'status': 'added',
                    'message': 'Paper bookmarked'
                })
        except Exception as e:
            logger.error(f'Bookmark error: {e}')
            db.session.rollback()
            return jsonify({'error': 'Failed to update bookmark'}), 500
    
    @app.route('/download/<int:paper_id>')
    @login_required
    def download_paper(paper_id):
        """Download a paper"""
        paper = Paper.query.get_or_404(paper_id)
        
        if not paper.is_approved:
            flash('This paper is not available for download.', 'error')
            return redirect(url_for('index'))
        
        # Increment download count
        try:
            paper.increment_download_count()
            db.session.commit()
        except Exception as e:
            logger.error(f'Error updating download count: {e}')
            # Continue with download even if count update fails
        
        # Return a page that handles the download with better user feedback
        if paper.cloudinary_url:
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Downloading {paper.title}</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body text-center">
                                    <div class="spinner-border text-primary mb-3" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <h5 class="card-title">Downloading: {paper.title}</h5>
                                    <p class="card-text">Your download should start automatically...</p>
                                    <a href="{paper.cloudinary_url}" class="btn btn-primary" target="_blank">
                                        Click here if download doesn't start
                                    </a>
                                    <br><br>
                                    <a href="{url_for('index')}" class="btn btn-secondary">
                                        Return to Home
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <script>
                    // Auto-start download and redirect after delay
                    setTimeout(function() {{
                        window.open('{paper.cloudinary_url}', '_blank');
                        setTimeout(function() {{
                            window.location.href = '{url_for("index")}';
                        }}, 2000);
                    }}, 1000);
                </script>
            </body>
            </html>
            '''
        else:
            flash('File not available for download.', 'error')
            return redirect(url_for('index'))
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        """Admin dashboard"""
        stats = get_admin_stats()
        pending_papers = Paper.query.filter_by(is_approved=False).order_by(Paper.upload_date.desc()).all()
        recent_papers = Paper.query.filter_by(is_approved=True).order_by(Paper.approval_date.desc()).limit(10).all()
        
        return render_template('admin_dashboard.html',
                             stats=stats,
                             pending_papers=pending_papers,
                             recent_papers=recent_papers)
    
    @app.route('/admin/approve/<int:paper_id>', methods=['POST'])
    @login_required
    @admin_required
    def approve_paper(paper_id):
        """Approve a paper"""
        paper = Paper.query.get_or_404(paper_id)
        
        try:
            paper.approve(current_user)
            flash(f'Paper "{paper.title}" approved successfully.', 'success')
        except Exception as e:
            logger.error(f'Approval error: {e}')
            flash('Failed to approve paper.', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/reject/<int:paper_id>', methods=['POST'])
    @login_required
    @admin_required
    def reject_paper(paper_id):
        """Reject a paper"""
        paper = Paper.query.get_or_404(paper_id)
        reason = request.form.get('reason', 'No reason provided')
        
        try:
            paper.reject(current_user, reason)
            flash(f'Paper "{paper.title}" rejected.', 'warning')
        except Exception as e:
            logger.error(f'Rejection error: {e}')
            flash('Failed to reject paper.', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/delete/<int:paper_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_paper(paper_id):
        """Delete a paper permanently"""
        paper = Paper.query.get_or_404(paper_id)
        
        try:
            db.session.delete(paper)
            db.session.commit()
            flash(f'Paper "{paper.title}" deleted permanently.', 'warning')
        except Exception as e:
            logger.error(f'Deletion error: {e}')
            flash('Failed to delete paper.', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/feedback', methods=['GET', 'POST'])
    def feedback():
        """Feedback form"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            rating = request.form.get('rating')
            
            # Validation
            if not all([name, email, subject, message]):
                flash('All fields are required!', 'error')
                return render_template('feedback.html')
            
            try:
                new_feedback = Feedback(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    rating=int(rating) if rating else None,
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                
                db.session.add(new_feedback)
                db.session.commit()
                
                flash('Thank you for your feedback! We appreciate your input.', 'success')
                return redirect(url_for('feedback'))
                
            except Exception as e:
                db.session.rollback()
                flash('Error submitting feedback. Please try again.', 'error')
                return render_template('feedback.html')
        
        return render_template('feedback.html')
    
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}
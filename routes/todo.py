from flask import Blueprint,render_template,session,flash,redirect,url_for,request
from functools import wraps
from models import db,Todo
from routes.dashboard import get_dashboard
from utilis.auth import login_required

todo_bp=Blueprint("todo", __name__ ,template_folder="../templates")

#DASHBOARD INFO
@todo_bp.route("/dashboard")
@login_required
def dashboard():
    dashboard_data = get_dashboard()  
    return render_template("menu.html", **dashboard_data)

#ADD A TASK
@todo_bp.route("/todo/add", methods=["POST"])
@login_required
def add_todo():
    user_id=session.get("user_id")
    title=request.form.get("task")
    if not title:
        flash("Please enter a task!","warning")
        return redirect(url_for("todo.dashboard"))
    new_todo=Todo(title=title,created_by=user_id)
    db.session.add(new_todo)
    db.session.commit()
    flash("Task added successfully!","success")
    return redirect(url_for("todo.dashboard"))

#DELETE A TASK
@todo_bp.route("/todo/delete/<int:todo_id>", methods=["POST"])
@login_required
def delete_todo(todo_id):
    todo=Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash("Task deleted successfully!","success")
    return redirect(url_for("todo.dashboard"))

#MARK TASK AS DONE
@todo_bp.route("/todo/complete/<int:todo_id>", methods=["POST"])
@login_required
def complete_todo(todo_id):
    todo=Todo.query.get_or_404(todo_id)
    todo.status="completed"
    db.session.commit()
    flash("Task marked as completed!","info")
    return redirect(url_for("todo.dashboard"))

#CLEAR ALL TASKS
@todo_bp.route("/todo/clear", methods=["POST"])
@login_required
def clear_todos():
    user_id=session.get("user_id")
    Todo.query.filter_by(created_by=user_id).delete()
    db.session.commit()
    flash("All tasks cleared!","info")
    return redirect(url_for("todo.dashboard"))

    
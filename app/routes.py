from flask import render_template, redirect, request
from app import app
from bson.objectid import ObjectId
import pymongo
from os import environ

DB_NAME = environ.get("DB_NAME")
DB_PASSWORD = environ.get("DB_PASSWORD")

client = pymongo.MongoClient("mongodb+srv://root:" + DB_PASSWORD + "@bugtracker-kcina.mongodb.net/" + DB_NAME + "?retryWrites=true&w=majority")
db = client.BugTracker
print(db.list_collection_names())
collection = db["issues"]


class Issue:
    def __init__(self, name, description, resolved=False, tags=[]):
        self.name = name
        self.description = description
        self.resolved = resolved
        self.tags = tags

    def get_issue(self):
        return {
            "name": self.name,
            "description": self.description,
            "resolved": self.resolved,
            "tags": self.tags
        }

# Landing page
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.j2', title="Bug Tracker")


# Form to create issue and presents all current issues
@app.route('/issues', methods=['GET', 'POST'])
def issues():
    issues = list(collection.find())
    if request.method == 'POST':
        if request.form['name'] != "" or request.form['description'] != "":
            new_issue = Issue(request.form['name'], request.form['description'], tags=request.form['tags'].split(","))
            collection.insert(new_issue.get_issue())
            return redirect('/issues')
    else:
        return render_template('issues.j2', title="Issues", issues=issues)


# Same as /issues but only displays with specified tags
@app.route('/issues/<tag>', methods=['GET', 'POST'])
def issues_with_tag(tag):
    issues = list(collection.find())
    if request.method == 'POST':
        if request.form['name'] != "" or request.form['description'] != "":
            new_issue = Issue(request.form['name'], request.form['description'], tags=request.form['tags'].split(","))
            collection.insert(new_issue.get_issue())
            return redirect('/issues')
    else:
        return render_template('issues.j2', title="Issues", issues=issues, tag=tag)

# Sets issue with the specified id to resolved.
@app.route('/set_resolved/<id>')
def resolve_issue(id):
    print(id)
    # collection.delete_one( {"_id": ObjectId(str(id)) } )
    collection.update_one({"_id": ObjectId(str(id))}, {
        "$set": {
            "resolved": True
        }
    })
    return redirect('/resolved') 


# Sets a resolved issue back to unresolved
@app.route('/return_issue/<id>')
def unresolve_issue(id):
    collection.update_one({"_id": ObjectId(str(id))}, {
        "$set": {
            "resolved": False
        }
    })
    return redirect('/resolved')

# Deletes issues once resolved
@app.route('/delete/<id>')
def delete(id):
    collection.delete_one({ "_id": ObjectId(id) })
    return redirect("/resolved")

# Presents all resolved issues
@app.route('/resolved')
def resolved():
    issues = list(collection.find())
    return render_template('resolved.j2', title="Resolved", issues=issues)
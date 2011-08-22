'''
Created on Aug 5, 2011

@author: BogdanC
'''
from google.appengine.ext import db


class Employee(db.Model):
    name = db.StringProperty(required = True )
    user = db.UserProperty(required=True)
    position = db.StringProperty()
    years = db.StringProperty()
    assigned = db.BooleanProperty()

class Project(db.Model):
    name = db.StringProperty(required = True)
    type = db.StringProperty()
    description = db.StringProperty(multiline = True)
    startdate = db.DateProperty(auto_now_add=True)
    enddate = db.DateProperty(auto_now_add=True)
    pmid = db.IntegerProperty()

class EmployeeOnProject(db.Model):
    empl = db.ReferenceProperty(Employee)
    proj = db.ReferenceProperty(Project)
    idemplskill = db.IntegerProperty()
    startdate = db.DateProperty()
    enddate = db.DateProperty()

class Skill(db.Model):
    name = db.StringProperty()

class EmployeeSkills(db.Model):
    skill = db.ReferenceProperty(Skill)
    empl = db.ReferenceProperty(Employee)
    yearsxper = db.StringProperty()
    
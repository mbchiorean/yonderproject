from google.appengine.api import users
from webapp2 import webapp2
from webapp2_extras import jinja2
from google.appengine.ext.webapp.util import run_wsgi_app
from models.model import Employee,EmployeeOnProject,Skill,EmployeeSkills
from models.model import Project 
from datetime import date
from google.appengine.api.users import User
from util.util import Anon
from util.sessions import Session


            
class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)
        
        
class MainPage(webapp2.RequestHandler):
'''will store info about the user in the session '''
'''usrtype : 1=Pm , 2=HR ,3=Developer or what else 4=sysadmin and 5=noauth employee '''    
    def get(self):
        
        session = Session()
        empl = currentUser().get_employee()
        session["url"] = users.create_logout_url(self.request.uri)
        if users.is_current_user_admin():
            session["pos"] = 4
            self.redirect("/projects")
        elif empl:
            if empl.position == "Project Manager":
                session["pos"] = 1
                session["empl"] = empl
                self.redirect("/projects")
            elif empl.position == "HR":
                session["pos"] = 2
                session["empl"] = empl
                self.redirect("/employees")
            else:
                session["pos"] = 3
                session["empl"] = empl
                link = "/profilepage?emplid=" + str(empl.key().id())
                self.redirect(link)
        else:
            session["pos"] = 5
            self.redirect("/nouser")
                
                
class currentUser():
    
    def get_employee(self):
        
        empl = Employee.gql("WHERE user = :u", u=users.get_current_user()).get()
        if empl:
            return empl


class ProjectsList(BaseHandler):
    
    def get(self):
        
        session = Session()        
        if session["pos"] == 1 or session["pos"] == 4:
            projects = Project.all()
            noprojects = projects.count()
            values = {'projects' : projects,
                      'noprojects' : noprojects,
                      'url' : session["url"]
                      }
            self.render_response("projects.html", **values)
        else:
            self.redirect("/nouser")


class DelProject(webapp2.RequestHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            raw_id = self.request.get('id')
            id = int(raw_id)
            proj = Project.get_by_id(id)
            emplonp = proj.employeeonproject_set
            for eop in emplonp:
                eop.empl.assigned = False
                eop.empl.save()
                eop.delete()
            proj.delete()
            self.redirect('/projects')
        else:
            self.redirect("/nouser")
            
            
class NewProjectPage(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            vals = {'url':session["url"]}
            self.render_response("newproj.html", **vals)
        else:
            self.redirect("/nouser")
    
            
class NewProject(webapp2.RequestHandler):
    
    def post(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            start = self.request.get('projStartD')
            end = self.request.get('projEndD')
            start_date = date(int(start.split('-')[0]),int(start.split('-')[1]),int(start.split('-')[2]))
            end_date = date(int(end.split('-')[0]),int(end.split('-')[1]),int(end.split('-')[2]))
            project = Project(name=self.request.get('projName'),
                              type=self.request.get('projType'),
                              description = self.request.get('projDescription'),
                              startdate = start_date,
                              enddate = end_date,
                              pmid = int(self.request.get('projPmId'))
                              )
            project.put()
            self.redirect("/projects")
        else:
            self.redirect("/nouser")
        
        
class EmployeeList(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            employees = Employee.all()
            noemployees = employees.count()
            vals = {'employees' : employees,
                    'noemployees' : noemployees,
                    'url' : session["url"]
                    }
            self.render_response("employeeList.html",**vals)
        else:
            self.redirect("/nouser")
            
            
class EditProjectPage(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            raw_id = self.request.get('id')
            id = int(raw_id)
            project = Project.get_by_id(id)
            vals={'id' : id,
                  'project' : project,
                  'url' : session["url"]}
            self.render_response("editproj.html", **vals)
        else:
            self.redirect("/nouser")


class EditProject(webapp2.RequestHandler):
    
    def post(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            raw_id = self.request.get('projId')
            id=int(raw_id)
            project = Project.get_by_id(id)
            project.name = self.request.get('projName')
            project.type = self.request.get('projType')
            project.description = self.request.get('projDescription')
            project.pmid = int(self.request.get('projPmId'))
        
            start = self.request.get('projStartD')
            end = self.request.get('projEndD')
            start_date = date(int(start.split('-')[0]),int(start.split('-')[1]),int(start.split('-')[2]))
            end_date = date(int(end.split('-')[0]),int(end.split('-')[1]),int(end.split('-')[2]))
            
            project.startdate = start_date
            project.enddate = end_date
            
            project.save()
        
            self.redirect('/projects')
        else:
            self.redirect("/nouser")
        
            
class EmployeeAlocPage(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            raw_id = self.request.get('id')
            id = int(raw_id)
            employee_list = Employee.gql("WHERE assigned = False and position != :1", "Project Manager")
            noempl = employee_list.count()
            project = Project.get_by_id(id)
            employeesonthisproject = [angaj.empl for angaj in project.employeeonproject_set]
            noemplonthis = len(employeesonthisproject)
            vals = { 'noempl' : noempl,
                     'employees' : employee_list,
                     'project' : project,
                     'employeesonthis' : employeesonthisproject,
                     'noemplonthis' : noemplonthis,
                     'url' : session["url"]
                    }
            self.render_response("employeealoc.html", **vals)
        else:
            self.redirect("/nouser")
        
            
class EmployeeAloc(webapp2.RequestHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            project =Project.get_by_id(int(self.request.get('projid')))
            employee= Employee.get_by_id(int(self.request.get('emplid')))
            emplon = EmployeeOnProject(proj=project, empl=employee)
            emplon.put()
            employee.assigned = True
            employee.save()
            link = "/emplalocpage?id=" + str(self.request.get('projid'))
            self.redirect(link)
        else:
            self.redirect("/nouser")
            
            
class EmployeeDealoc(webapp2.RequestHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 1 or session["pos"] == 4:
            employee = Employee.get_by_id(int(self.request.get('emplid')))
            employee.assigned = False
            employee.save()
            assign = employee.employeeonproject_set.get()
            assign.delete()
            link="/emplalocpage?id=" + str(self.request.get('projid'))
            self.redirect(link)
        else:
            self.redirect("/nouser")
            
            
class ProfilePage(BaseHandler):
    
    def get(self):
        
        session = Session()
        employee = Employee.get_by_id(int(self.request.get('emplid')))
        skills = [Anon(skill=es.skill,exp=es.yearsxper) for es in employee.employeeskills_set]
        noskills = len(skills)
        allskills = Skill.all()
        viewer = session["empl"]
        if viewer.key().id == employee.key().id:
            owner = True
        else:
            owner = False
        vals = {'employee' : employee,
                'skills' : skills,
                'noskills' : noskills,
                'allskills' : allskills,
                'owner' : owner,
                'url' : session["url"]}
        self.render_response("profilePage.html", **vals)
        
        
class NewEmployeePage(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            vals={'url' : session["url"]}
            self.render_response("newEmployeePage.html", **vals)
        else:
            self.redirect("/nouser")
            
            
class NewEmployee(webapp2.RequestHandler):
    
    def post(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            empl = Employee(name=self.request.get('emplName'),
                            user=User(self.request.get('user')),
                            position = self.request.get('emplPosition'),
                            years = self.request.get('emplExp'),
                            assigned = False
                            )
            empl.put()
            self.redirect("/employees")
        else:
            self.redirect("/nouser")
        
            
class NewEmployeeSkill(webapp2.RequestHandler):
    
    def post(self):
        
        session = Session()
        employee = Employee.get_by_id(int(self.request.get('employeeId')))
        viewer = session["empl"]
        if viewer.key().id == employee.key().id:
            owner = True
        else:
            owner = False
        if owner:
            skilll = Skill.get_by_id(int(self.request.get('skillId')))
            years = str(self.request.get('skillExperience'))
            emplskill = EmployeeSkills(skill=skilll,
                                       empl=employee,
                                       yearsxper=years)
            emplskill.put()
            link = "/profilepage?emplid=" + str(self.request.get('employeeId'))
            self.redirect(link)
        else:
            self.redirect("/nouser")
            
            
class RemoveEmployeeSkill(webapp2.RequestHandler):
    
    def get(self):
        
        session = Session()
        viewer = session["empl"]
        emplid = self.request.get('emplid')
        employee = Employee.get_by_id(int(emplid))
        if viewer.key().id == employee.key().id:
            skill = Skill.get_by_id(int(self.request.get('skillid')))
            skillempl = employee.employeeskills_set.filter('skill = ', 
                                                           skill.key()).get()
            skillempl.delete()
            link = "/profilepage?emplid=" + emplid
            self.redirect(link)
        else:
            self.redirect("/nouser")
            
            
class DeleteEmployee(webapp2.RequestHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            empl = Employee.get_by_id(int(self.request.get('emplid')))
            emplskills = empl.employeeskills_set
            emplonproj = empl.employeeonproject_set
            for es in emplskills:
                es.delete()
            for ep in emplonproj:
                ep.delete()
            empl.delete()
            self.redirect('/employees')
        else:
            self.redirect("/nouser")
            
            
class EditEmployeePage(BaseHandler):
    
    def get(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            employee = Employee.get_by_id(int(self.request.get('emplid')))
            vals = {'employee' : employee,
                    'position' : employee.position,
                    'url' : session["url"]}
            self.render_response("editemployeepage.html", **vals)
        else:
            self.redirect("/nouser")
            
            
class EditEmployee(webapp2.RequestHandler):
    
    def post(self):
        
        session = Session()
        if session["pos"] == 2 or session["pos"] == 4:
            employee = Employee.get_by_id(int(self.request.get('emplId')))
            employee.name = self.request.get('emplName')
            employee.user = User(self.request.get('emplUser'))
            employee.position = self.request.get('emplPosition')
            employee.years = self.request.get('emplExp')
            
            employee.save()
            self.redirect('/employees')
        else:
            self.redirect("/nouser")
            
            
class NoUser(BaseHandler):
    
    def get(self):
        
        vals = {'user' : users.get_current_user(),
                'url' : users.create_logout_url(self.request.uri)}
        self.render_response("nouser.html", **vals)


# Register the URL with the responsible classes
application = webapp2.WSGIApplication([('/', MainPage),
                                      ('/projects',ProjectsList),
                                      ('/delproj',DelProject),
                                      ('/newprojpage',NewProjectPage),
                                      ('/newproj',NewProject),
                                      ('/editprojpage',EditProjectPage),
                                      ('/editproj',EditProject),
                                      ('/employees',EmployeeList),
                                      ('/emplalocpage',EmployeeAlocPage),
                                      ('/emplaloc',EmployeeAloc),
                                      ('/empldealoc',EmployeeDealoc),
                                      ('/profilepage',ProfilePage),
                                      ('/newemployee',NewEmployeePage),
                                      ('/newempl',NewEmployee),
                                      ('/delempl',DeleteEmployee),
                                      ('/newskill',NewEmployeeSkill),
                                      ('/editempl',EditEmployeePage),
                                      ('/editemployee',EditEmployee),
                                      ('/removeskill',RemoveEmployeeSkill),
                                      ('/nouser',NoUser)
                                      ],
                                      debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()

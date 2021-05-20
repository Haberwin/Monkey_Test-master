from redminelib import Redmine


class CreateRedmine(object):
    _name_to_id_dict = {
        "liucheng": "699",
        "zhanghuiliang": "737",
        "liuwenhua": "811"}
    _priority_dict = {
        'Low': 1,
        'Normal': 24,
        'High': 3,
        'Urgent': 4}
    _tracker_dict = {
        'Project': 2,
        'Upperstream': 3,
        'Mechanical': 4,
        'Hardware': 5,
        'Software': 12,
        'Production': 8,
        'Quality': 7,
        'Aftersales': 9,
        'Product': 17,
        'UX': 18,
    }
    _bug_level_dict = {
        'level A': 'A (FMEA得分 >1000)',
        'level B': 'B (1000>= FMEA得分 >600)',
        'level C': 'C (600 >= FMEA得分 >300)',
        'level D': 'D (300 >= FMEA得分 >100)',
        'level E': 'E (100 >= FMEA得分)'
    }

    # def __init__(self,
    #              username='SRtest',
    #              password='123456',
    #              redmine_url='http://192.168.3.78:8078'
    #              ):
    #     self.redmine = Redmine(
    #         url=redmine_url,
    #         username=username,
    #         password=password,
    #         requests={'verify': False})
    #     self.set_default()
        
    def __init__(self,redmine_url='http://192.168.3.78:8078',api_key="b1dd2a3a56cfc68049c00678d4aa24968a5d3d7c",requests={'verify': False}):
        self.redmine=Redmine(url=redmine_url,key=api_key)
        self.set_default()

    def set_default(self):
        self.project_id = 627
        self.subject = '[bug](monkey)monkey test'
        self.description = 'no description'
        self.bug_level = 'level B'
        self.tracker = 12
        self.priority = 24 # 优先级 Normal
        self.assigned_to_id = 419
        # self.redmine.priority.id=2
        

    def set_parameter(self, subject, description, assigned, tracker='Software', priority='Normal', bug_level='level B'):
        # self.project_id = self._project_dict[project]
        self.priority = self._priority_dict[priority]
        self.assigned_to_id = assigned
        self.subject = subject
        self.description = description
        self.tracker = self._tracker_dict[tracker]
        self.bug_level = bug_level

    def creat_isses(self):
        self.redmine.issue.create(
            project_id=self.project_id,
            subject=self.subject,
            description=self.description,
            tracker_id=self.tracker,
            priority_id=self.priority,

            assigned_to_id=self.assigned_to_id,
            custom_fields=[
                # {'id': 7, 'name': 'BUG缺陷等级', 'value': '5--轻微缺陷（Enhancement）'},
                # {'id': 12, 'name': 'BUG可见性', 'value': '10--必现(Always)'},
                # {'id': 16, 'name': 'BUG复现概率', 'value': '10--必现(Always)'},
                {'id': 17, 'name': 'BUG等级',
                 'value': self._bug_level_dict[self.bug_level]},
                # {'name': 'BUG_FMEA得分（BUG缺陷等级x复现概率x可见性）', 'value': '', 'id': 18}
                # {'name': 'BUG等级', 'id': 17, 'value': 'C (600 >= FMEA得分 >300)'}
                # {'id': 19, 'name': 'BUG_FMEA得分（BUG缺陷等级x复现概率x可见性）', 'value': '500', },
                {'id': 4, 'name': '问题或任务类别', 'value': '问题反馈Issue'},
                {'id': 1, 'name': '软件平台', 'value': 'Android8.0'},
                {'id': 35, 'name': 'bug版本', 'value': 'MP'},
                {'id': 3, 'name': '问题涉及模块', 'multiple': True,
                 'value': ['Monkey test']},
                {'id': 2, 'name': ' 问题修改涉及范围', 'value': '本项目'}]
            # {'id': 38, 'name': 'BUG难易度', 'value': '1'}]
        )

    def set_project_id(self, project_id):
        issue = self.redmine.issue.get(int(project_id))
        self.project_id = issue.project.id

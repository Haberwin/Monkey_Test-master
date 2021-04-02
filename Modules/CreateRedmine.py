from redminelib import Redmine


class CreateRedmine(object):
    _name_to_id_dict = {
        "liucheng": "699",
        "zhanghuiliang": "737",
        "liuwenhua": "811"}
    _priority_dict = {
        'Low': 1,
        'Normal': 2,
        'High': 3,
        'Urgent': 4}
    _tracker_dict = {
        'Project': 2,
        'Upperstream': 3,
        'Mechanical': 4,
        'Hardware': 5,
        'Software': 6,
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

    def __init__(self,
                 username='SRtest',
                 password='123456',
                 redmine_url='http://192.168.3.78:8006/redmine'
                 ):
        self.redmine = Redmine(
            url=redmine_url,
            username=username,
            password=password,
            requests={'verify': False})
        self.project_id = 1434
        self.subject = '[bug](monkey)monkey test'
        self.description = 'no description'
        self.bug_level = 'level B'
        self.tracker_id = 6
        self.priority_id = 2  # 优先级 Normal
        self.assigned_to_id = 906

    def set_parameter(self, subject, description, assigned, tracker='Software', priority='Normal', bug_level='level B'):
        # self.project_id = self._project_dict[project]
        self.priority_id = self._priority_dict[priority]
        self.assigned_to_id = assigned
        self.subject = subject
        self.description = description
        self.tracker_id = self._tracker_dict[tracker]
        self.bug_level = bug_level

    def creat_isses(self):
        self.redmine.issue.create(
            project_id=self.project_id,
            subject=self.subject,
            description=self.description,
            tracker_id=self.tracker_id,
            priority_id=self.priority_id,

            assigned_to_id=self.assigned_to_id,
            custom_fields=[
                # {'id': 15, 'name': 'BUG缺陷等级', 'value': '5--轻微缺陷（Enhancement）'},
                # {'id': 16, 'name': 'BUG可见性', 'value': '10--必现(Always)'},
                # {'id': 17, 'name': 'BUG复现概率', 'value': '10--必现(Always)'},
                {'id': 20, 'name': 'BUG等级',
                 'value': self._bug_level_dict[self.bug_level]},
                # {'name': 'BUG_FMEA得分（BUG缺陷等级x复现概率x可见性）', 'value': '', 'id': 19}
                # {'name': 'BUG等级', 'id': 20, 'value': 'C (600 >= FMEA得分 >300)'}
                # {'id': 19, 'name': 'BUG_FMEA得分（BUG缺陷等级x复现概率x可见性）', 'value': '500', },
                {'id': 21, 'name': '问题或任务类别', 'value': '问题反馈Issue'},
                {'id': 25, 'name': '软件平台', 'value': 'Android8.0'},
                {'id': 26, 'name': '问题涉及模块', 'multiple': True,
                 'value': ['Monkey test']},
                {'id': 27, 'name': ' 问题修改涉及范围', 'value': '本项目'}]
            # {'id': 38, 'name': 'BUG难易度', 'value': '1'}]
        )

    def set_project_id(self, project_id):
        issue = self.redmine.issue.get(int(project_id))
        self.project_id = issue.project.id

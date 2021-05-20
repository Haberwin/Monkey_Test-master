from Modules.CreateRedmine import CreateRedmine

if __name__ == '__main__':
    myRedmine=CreateRedmine()

    # issues=myRedmine.redmine.issue.get(76097)
    myRedmine.set_project_id("76097")
    myRedmine.set_parameter(subject="[Test](Monkey)sdshsdhsh", description="monkey test",
                                     assigned=405)
    myRedmine.creat_isses()
    # print(issues)

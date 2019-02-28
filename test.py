import xml.etree.ElementTree as eTree
from src.manage_engine import ManageEngine
from run import init_services, task_execute


if __name__ == "__main__":
    config = eTree.parse('test.xml')
    meta = config.getroot()
    settings = meta.find('settings')
    services = init_services(settings)
    tasks = meta.find('tasks')
    for task in tasks:
        task_execute(task)


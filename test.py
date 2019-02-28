import xml.etree.ElementTree as eTree
from src.manage_engine import ManageEngine


if __name__ == "__main__":
    config = eTree.parse('mapping.xml')
    meta = config.getroot()
    settings = meta.find('settings')
    me = ManageEngine(settings.find('manage_engine'))
    print(me)

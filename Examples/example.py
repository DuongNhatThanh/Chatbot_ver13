import yaml
def get_exapmle():
    with open('./Examples/example.yml', encoding='utf-8') as cfgFile:
        example = yaml.safe_load(cfgFile)
        cfgFile.close()
    return example


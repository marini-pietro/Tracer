class YDKHandler:
    def __init__(self):
        pass

    def read_ydk(self, ydk_file): # TODO fix
        with open(ydk_file, "r") as f:
            ydk = f.readlines()
        return ydk
    
    def write_ydk(self, ydk_file, ydk): # TODO fix
        with open(ydk_file, "w") as f:
            f.writelines(ydk)


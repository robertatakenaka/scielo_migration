def fix_windows_path(path):
    new_path = path.replace("\\", "/")
    new_path = new_path.replace("\0", "/0")
    new_path = new_path.replace("\1", "/1")
    new_path = new_path.replace("\2", "/2")
    new_path = new_path.replace("\3", "/3")
    new_path = new_path.replace("\4", "/4")
    new_path = new_path.replace("\5", "/5")
    new_path = new_path.replace("\6", "/6")
    new_path = new_path.replace("\7", "/7")
    # new_path = new_path.replace("\8", "/8")
    # new_path = new_path.replace("\9", "/9")
    # new_path = new_path.replace("\x", "/x")
    new_path = new_path.replace("\n", "/n")
    new_path = new_path.replace("\t", "/t")
    new_path = new_path.replace("\r", "/r")
    new_path = new_path.replace("\b", "/b")
    new_path = new_path.replace("\f", "/f")
    new_path = new_path.replace("\v", "/v")
    new_path = new_path.replace("\a", "/a")
    return new_path
def get_class_var_name(class_, var):
    a = class_.__dict__  # type: dict
    for k, v in a.items():
        if id(getattr(class_, k)) == id(var) and v == var:
            return k
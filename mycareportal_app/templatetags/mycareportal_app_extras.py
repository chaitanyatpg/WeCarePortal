from django import template

register = template.Library()

@register.filter
def addstr(x,y):
    return str(x) + str(y)

@register.filter
def addstr_space(x,y):
    return str(x) + " " + str(y)

@register.filter
def num_loop(x):
    return range(x)

@register.filter
def append_datetime(x,y):
    #out_str = x
    if y != "":
        out_str = "{0}T{1}Z".format(str(x),str(y))
    else:
        out_str = x
    return out_str

@register.filter
def trunc_path(x):
    split_string = str(x).split('/')
    out_string = split_string[-1]
    return out_string

from django import template
from datetime import datetime

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
def convert_time_24_to_12(x):
    output_time = ""
    if x:
        output_hour = x.split(":")[0]
        output_minute = x.split(":")[1]
        new_x = "{0}:{1}".format(output_hour,output_minute)
        new_time = datetime.strptime(new_x,"%H:%M")
        output_time = new_time.strftime("%I:%M %p")
    return output_time


@register.filter
def trunc_path(x):
    split_string = str(x).split('/')
    out_string = split_string[-1]
    return out_string

@register.filter
def to_yes_no(x):
    if (str(x)=="True"):
        return "Yes"
    elif (str(x)=="False"):
        return "No"
    else:
        return x

@register.filter
def round_2(x):
    return round(x,2)

@register.filter
def to_currency(x):
    return "${:,}".format(round(x,2))

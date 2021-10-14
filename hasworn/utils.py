from django.contrib.humanize.templatetags.humanize \
    import ordinal as humanize_ordinal


def ordinal(int):
    if int == 1:
        return 'first'
    elif int == 2:
        return 'second'
    elif int == 3:
        return 'third'
    elif int == 4:
        return 'fourth'
    elif int == 5:
        return 'fifth'
    elif int == 6:
        return 'sixth'
    elif int == 7:
        return 'seventh'
    elif int == 8:
        return 'eighth'
    elif int == 9:
        return 'ninth'
    elif int == 10:
        return 'tenth'
    else:
        return humanize_ordinal(int)

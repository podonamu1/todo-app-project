def avg_progress(detail_set):

    c = 0.0
    for x in detail_set:
        c += x.progress

    if len(detail_set) == 0:
        return '0'
    else:
        avg = c / len(detail_set)
        return "{:.2f}".format(avg)

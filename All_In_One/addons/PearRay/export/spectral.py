def write_spectral_color(exporter, spec_name, color):
    new_name = exporter.register_unique_name('SPEC', spec_name)

    exporter.w.write("(spectrum")
    exporter.w.goIn()

    exporter.w.write(":name '%s'" % spec_name)
    exporter.w.write(":data (rgb %f %f %f)" % color[:])

    exporter.w.goOut()
    exporter.w.write(")")

    return new_name


def write_spectral_temp(exporter, spec_name, temp, type, factor):
    new_name = exporter.register_unique_name('SPEC', spec_name)

    exporter.w.write("(spectrum")
    exporter.w.goIn()

    exporter.w.write(":name '%s'" % spec_name)
    if type == 'LUM':
        exporter.w.write(":data (temperature %f %f)" % (temp, factor))
    elif type == 'RAD':
        exporter.w.write(":data (temperature_raw %f %f)" % (temp, factor))
    elif type == 'LUM_NORM':
        exporter.w.write(":data (temperature_norm %f %f)" % (temp, factor))
    elif type == 'RAD_NORM':
        exporter.w.write(":data (temperature_raw_norm %f %f)" % (temp, factor))

    exporter.w.goOut()
    exporter.w.write(")")

    return new_name
from core.models import Awb


def generate_awb():
    PREFIX = '800'

    a = Awb.objects.all()[0]

    # add left padding zeroes 
    serial_number = a.last_serial_number

    # TODO awb bakal cepet habis
    a.last_serial_number = a.last_serial_number + 1
    a.save()
    
    # modulo 7
    remainder = serial_number % 7

    awb = PREFIX + str(serial_number).zfill(7) + str(remainder)

    return awb

from onecode import Logger, slider


def xx():
    x = slider('My slider"1', 0.5, max=6)
    Logger.info(type(x))
    Logger.info(f'x = {x * 10}')

    yy(x)

def yy(x: int):
    y = slider('My slider 2', 0.2, optional='$my_slider_1"$ * 2 < 3')

    if y is not None:
        Logger.info(f'y = {y * x}')

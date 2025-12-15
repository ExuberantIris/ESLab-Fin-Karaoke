

class Scaler:
    """ Class that helps to scale the object to correct position/length

    Attributes:
        x_
    info: {
        "offset"
    }
    """
    def __init__(self, info: dict):
        """Initialize the instance based on info.
        
        The info should have following properties:
            offset: tuple[int, int] = (offsetX, offsetY)
                the offset for every objects
            base_range: tuple[int, int] = (baseWidth, baseHeight)
                the width and height of the screen before scaling
            scaled_range: tuple[int, int] = (scaledWidth, scaledHeight)
                the width and height of the screen after scaling
        """
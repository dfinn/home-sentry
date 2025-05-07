MULTIPLIER = 10000


class Point:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x:0.3f}, {self.y:0.3f})'

    def to_tuple(self):
        return self.x, self.y

    @staticmethod
    def from_dict(data: dict) -> 'Point':
        return Point(data['x'], data['y'])

    def relative_coords_to_abs(self, image):
        """
        Returns a new Point representing the absolute coordinates corresponding to this Point's relative coordinates
        for the image specified.
        """
        height = image.shape[0]
        width = image.shape[1]
        return Point(int(self.x * width), int(self.y * height))

    def abs_coors_to_relative(self, image):
        """
        Returns a new Point representing the relative coordinates (between 0.0 and 1.0) corresponding to this Point's
        absolute coordinates for the image specified.
        """
        height = image.shape[0]
        width = image.shape[1]
        return Point(self.x / width, self.y / height)

    def is_near_point(self, other_point: 'Point', threshold: float):
        """
        Return True if other_point's x/y coordinates are within threshold of this point's x/y coordinates.
        Convert float values to int first to work around float rounding errors (constraining to significant digits
        specified by MULTIPLIER).
        """
        int_threshold = int(threshold * MULTIPLIER)
        int_this_x = int(self.x * MULTIPLIER)
        int_this_y = int(self.y * MULTIPLIER)
        int_other_x = int(other_point.x * MULTIPLIER)
        int_other_y = int(other_point.y * MULTIPLIER)
        x_within_threshold = int_this_x - int_threshold <= int_other_x <= int_this_x + int_threshold
        y_within_threshold = int_this_y - int_threshold <= int_other_y <= int_this_y + int_threshold
        return x_within_threshold and y_within_threshold

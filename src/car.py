def get_object_distance(
    f,
    focal_length,
    object_size_in_image,
    object_size_in_real_world,
    ratio=1,
):
    """
    from : https://stackoverflow.com/questions/14038002/opencv-how-to-calculate-distance-between-camera-and-object-using-image
    - object_real_world in "mm"
    - object_size_in_image in "px"
    - object_size_in_real_world in "mm"
    """
    pixels_per_mm = f / focal_length
    pixels_per_mm = round(pixels_per_mm / ratio)
    object_image_sensor = object_size_in_image / pixels_per_mm
    distance = object_size_in_real_world * focal_length / object_image_sensor
    return distance  # in "mm"


class CarDetector:
    CAR_MIN_DISTANCE = 2
    AVG_CAR_WIDTH = 2.5

    def __init__(self, f, focal_length, ratio=1) -> None:
        self.f = f
        self.focal_length = focal_length
        self.ratio = ratio

    def is_car_in_front_close(self, distance):
        return distance < self.CAR_MIN_DISTANCE * 1000

    def detect_cars_in_front(self, img):
        return []

    def is_car_in_front(self, car):
        x, y, w, h = car
        return False

    def calculate_distance(self, car):
        x, y, w, h = car
        return get_object_distance(self.f, self.focal_length, w, self.AVG_CAR_WIDTH*1000, self.ratio)

    def is_car_safe(self, img):
        for car in self.detect_cars_in_front(img):
            if self.is_car_in_front(car):
                distance = self.calculate_distance(car)
                if self.is_car_in_front_close(distance):
                    return False
        return True

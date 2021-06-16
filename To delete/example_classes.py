class Car():
    def __init__(self, year: int, color: str, num_wheels=4):
        self.color = color
        self.num_wheels = num_wheels
        # self.year = year

    def make_car_older(self, num_years):
        self.year = self.year - num_years
        return self.year

    def check_if_old_car(self):
        if self.year < 1950:
            return True
        else:
            return False


KathCar = Car(year=1989, color='red')
while True:
    year_rn = KathCar.make_car_older(10)
    old_car_error = KathCar.check_if_old_car()
    print(year_rn)
    if old_car_error:
        print('ahhh too old')
        break

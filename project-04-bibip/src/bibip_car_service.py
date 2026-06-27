import os
from decimal import Decimal
from datetime import datetime
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        os.makedirs(root_directory_path, exist_ok=True)

        self.models_file = os.path.join(root_directory_path, "models.txt")
        self.models_index_file = os.path.join(root_directory_path, "models_index.txt")

        self.cars_file = os.path.join(root_directory_path, "cars.txt")
        self.cars_index_file = os.path.join(root_directory_path, "cars_index.txt")

        self.sales_file = os.path.join(root_directory_path, "sales.txt")
        self.sales_index_file = os.path.join(root_directory_path, "sales_index.txt")

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        index = []
        if os.path.exists(self.models_index_file):
            with open(self.models_index_file, "r", encoding="utf-8") as f:
                for line in f:
                    key, pos = line.strip().split(";")
                    index.append((key, int(pos)))
        with open(self.models_file, "a", encoding="utf-8") as f:
            f.write(f"{model.id};{model.brand};{model.name}\n")

        index.append((str(model.id), len(index)))
        index.sort(key=lambda x: x[0])

        with open(self.models_index_file, "w", encoding="utf-8") as f:
            for key, position in index:
                f.write(f"{key};{position}\n")

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        index = []
        if os.path.exists(self.cars_index_file):
            with open(self.cars_index_file, "r", encoding="utf-8") as f:
                for line in f:
                    key, pos = line.strip().split(";")
                    index.append((key, int(pos)))

        with open(self.cars_file, "a", encoding="utf-8") as f:
            f.write(f"{car.vin};{car.model};{car.price};{car.date_start};{car.status}\n")

        index.append((car.vin, len(index)))
        index.sort(key=lambda x: x[0])

        with open(self.cars_index_file, "w", encoding="utf-8") as f:
            for key, pos in index:
                f.write(f"{key};{pos}\n")

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sales_index = []
        if os.path.exists(self.sales_index_file):
            with open(self.sales_index_file, "r", encoding="utf-8") as f:
                for line in f:
                    key, pos = line.strip().split(";")
                    sales_index.append((key, int(pos)))

        with open(self.sales_file, "a", encoding="utf-8") as f:
            f.write(f"{sale.sales_number};{sale.car_vin};{sale.cost};{sale.sales_date}\n")

        sales_index.append((sale.sales_number, len(sales_index)))
        sales_index.sort(key=lambda x: x[0])
        with open(self.sales_index_file, "w", encoding="utf-8") as f:
            for key, pos in sales_index:
                f.write(f"{key};{pos}\n")

        with open(self.cars_index_file, "r", encoding="utf-8") as f:
            car_index = {k: int(v) for k, v in (line.strip().split(";") for line in f)}

        if sale.car_vin not in car_index:
            raise ValueError(f"Car with VIN {sale.car_vin} not found")

        car_line_num = car_index[sale.car_vin]
        with open(self.cars_file, "r", encoding="utf-8") as f:
            cars = f.readlines()

        vin, model, price, date_start, status = cars[car_line_num].strip().split(";")
        cars[car_line_num] = f"{vin};{model};{price};{date_start};sold\n"

        with open(self.cars_file, "w", encoding="utf-8") as f:
            f.writelines(cars)

        return Car(vin=vin, model=int(model), price=float(price),
                   date_start=date_start, status=CarStatus.sold)

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        if not os.path.exists(self.cars_file):
            return []

        cars = []
        with open(self.cars_file, "r", encoding="utf-8") as f:
            for line in f:
                vin, model_id_str, price_str, date_start_str, car_status = line.strip().split(";")
                if car_status == status.value:
                    cars.append(Car(
                        vin=vin,
                        model=int(model_id_str),
                        price=Decimal(price_str),
                        date_start=date_start_str,
                        status=CarStatus(car_status)
                    ))
        return cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        if not os.path.exists(self.cars_index_file):
            return None

        car_line_num = None
        with open(self.cars_index_file, "r", encoding="utf-8") as f:
            for line in f:
                key, pos = line.strip().split(";")
                if key == vin:
                    car_line_num = int(pos)
                    break

        if car_line_num is None:
            return None

        with open(self.cars_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        vin, model_id_str, price_str, date_start_str, status_str = lines[car_line_num].strip().split(";")
        model_id = int(model_id_str)
        price = Decimal(price_str)
        date_start = datetime.fromisoformat(date_start_str)
        status = CarStatus(status_str)

        model_line_num = None
        with open(self.models_index_file, "r", encoding="utf-8") as f:
            for line in f:
                key, pos = line.strip().split(";")
                if key == str(model_id):
                    model_line_num = int(pos)
                    break

        if model_line_num is None:
            return None

        with open(self.models_file, "r", encoding="utf-8") as f:
            models = f.readlines()

        _, brand, name = models[model_line_num].strip().split(";")

        sales_date = sales_cost = None
        if os.path.exists(self.sales_file):
            with open(self.sales_file, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) >= 4 and parts[1] == vin:
                        _, _, cost_str, date_str = parts
                        sales_date = datetime.fromisoformat(date_str)
                        sales_cost = Decimal(cost_str)
                        break

        return CarFullInfo(
            vin=vin,
            car_model_name=name,
            car_model_brand=brand,
            price=price,
            date_start=date_start,
            status=status,
            sales_date=sales_date,
            sales_cost=sales_cost,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        if not os.path.exists(self.cars_index_file):
            raise ValueError("Index file not found")

        index = []
        car_line_num = None
        with open(self.cars_index_file, "r", encoding="utf-8") as f:
            for line in f:
                key, pos = line.strip().split(";")
                index.append((key, int(pos)))
                if key == vin:
                    car_line_num = int(pos)

        if car_line_num is None:
            raise ValueError(f"Car with VIN {vin} not found")

        with open(self.cars_file, "r", encoding="utf-8") as f:
            cars = f.readlines()

        parts = cars[car_line_num].strip().split(";")
        parts[0] = new_vin
        cars[car_line_num] = ";".join(parts) + "\n"

        with open(self.cars_file, "w", encoding="utf-8") as f:
            f.writelines(cars)

        for i, (key, pos) in enumerate(index):
            if key == vin:
                index[i] = (new_vin, pos)
        index.sort(key=lambda x: x[0])

        with open(self.cars_index_file, "w", encoding="utf-8") as f:
            for key, pos in index:
                f.write(f"{key};{pos}\n")

        return Car(vin=new_vin, model=int(parts[1]), price=float(parts[2]),
                   date_start=parts[3], status=CarStatus(parts[4]))

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        if not os.path.exists(self.sales_file):
            raise ValueError("Файл с продажами не найден")

        sale_vin = None
        updated_sales = []
        with open(self.sales_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(";")
                if parts[0] == sales_number:
                    sale_vin = parts[1]
                else:
                    updated_sales.append(line)

        if sale_vin is None:
            raise ValueError(f"Продажа {sales_number} не найдена")

        with open(self.sales_file, "w", encoding="utf-8") as f:
            f.writelines(updated_sales)

        with open(self.cars_index_file, "r", encoding="utf-8") as f:
            for line in f:
                vin, pos = line.strip().split(";")
                if vin == sale_vin:
                    car_line_num = int(pos)
                    break

        with open(self.cars_file, "r", encoding="utf-8") as f:
            cars = f.readlines()

        parts = cars[car_line_num].strip().split(";")
        parts[4] = "available"
        cars[car_line_num] = ";".join(parts) + "\n"

        with open(self.cars_file, "w", encoding="utf-8") as f:
            f.writelines(cars)

        return Car(vin=parts[0], model=int(parts[1]), price=float(parts[2]),
                   date_start=parts[3], status=CarStatus(parts[4]))

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        if not os.path.exists(self.sales_file):
            return []

        sold_vins = []
        with open(self.sales_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 2:
                    sold_vins.append(parts[1])

        vin_to_model = {}
        with open(self.cars_file, "r", encoding="utf-8") as f:
            for line in f:
                vin, model_id_str, *_ = line.strip().split(";")
                vin_to_model[vin] = int(model_id_str)

        model_sales = {}
        for vin in sold_vins:
            model_id = vin_to_model.get(vin)
            if model_id is not None:
                model_sales[model_id] = model_sales.get(model_id, 0) + 1

        models_info = {}
        with open(self.models_file, "r", encoding="utf-8") as f:
            for line in f:
                model_id_str, brand, name = line.strip().split(";")
                models_info[int(model_id_str)] = (name, brand)

        stats = [
            ModelSaleStats(car_model_name=models_info[mid][0], brand=models_info[mid][1], sales_number=count)
            for mid, count in model_sales.items()
        ]

        stats.sort(key=lambda x: x.sales_number, reverse=True)
        return stats[:3]

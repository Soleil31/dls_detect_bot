from ultralytics import YOLO

model = YOLO("best.pt")


def generate_result(image_path):
    result = model.predict(source=image_path, conf=0.5, save=True)
    file_name = image_path.split('/')[1]
    save_path = result[0].save_dir + f'/{file_name}'
    return save_path

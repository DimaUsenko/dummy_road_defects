import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pycocotools.coco import COCO
from pycocotools import mask as maskUtils

# Путь к файлу с аннотациями COCO и папке с изображениями
annotation_file = 'data/annotations/instances_default.json'
images_folder = 'data/images'
output_folder = 'data/label_draw'

# Создание папки для сохранения результатов, если она не существует
os.makedirs(output_folder, exist_ok=True)

# Загрузка аннотаций COCO
with open(annotation_file, 'r') as f:
    coco_data = json.load(f)

coco = COCO(annotation_file)

# Получение всех идентификаторов изображений
image_ids = coco.getImgIds()

# Обработка каждого изображения
for image_id in image_ids:
    # Загрузка информации об изображении
    image_info = coco.loadImgs(image_id)[0]
    image_path = os.path.join(images_folder, image_info['file_name'])
    image = Image.open(image_path)
    image_array = np.array(image)

    # Получение аннотаций для изображения
    annotations_ids = coco.getAnnIds(imgIds=image_info['id'])
    annotations = coco.loadAnns(annotations_ids)

    # Отрисовка изображения и аннотаций
    fig, ax = plt.subplots(1, figsize=(12, 9))
    ax.imshow(image_array)

    for ann in annotations:
        bbox = ann['bbox']
        category_id = ann['category_id']
        category_name = coco.loadCats(category_id)[0]['name']

        # Рисуем баундинг-боксы
        rect = patches.Rectangle(
            (bbox[0], bbox[1]), bbox[2], bbox[3],
            linewidth=2, edgecolor='r', facecolor='none', alpha=0.5
        )
        ax.add_patch(rect)

        # Рисуем маски
        if 'segmentation' in ann:
            segmentation = ann['segmentation']
            if isinstance(segmentation, list):
                for seg in segmentation:
                    poly = np.array(seg).reshape((len(seg) // 2, 2))
                    polygon = patches.Polygon(poly, linewidth=1, edgecolor='b', facecolor='b', alpha=0.3)
                    ax.add_patch(polygon)
            elif isinstance(segmentation, dict):
                rle = maskUtils.frPyObjects(segmentation, image_info['height'], image_info['width'])
                m = maskUtils.decode(rle)
                img = np.ones((m.shape[0], m.shape[1], 3))
                color_mask = np.random.random((1, 3)).tolist()[0]
                for i in range(3):
                    img[:, :, i] = color_mask[i]
                ax.imshow(np.dstack((img, m * 0.5)))

        # Подписываем классы
        plt.text(
            bbox[0], bbox[1] - 10,
            category_name,
            color='white', fontsize=12, bbox=dict(facecolor='red', alpha=0.5)
        )

    plt.axis('off')

    # Сохранение результата
    output_path = os.path.join(output_folder, image_info['file_name'])
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

print("Процесс завершен!")

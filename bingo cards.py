import cv2
import numpy as np
import random
import os
from not_my_functions import overlay_image, image_resize

def bingo_card(
    rows,
    columns,
    random_list,
    background = None,
    line_color = (0,0,0),
    line_thickness = 2,
    font_type = cv2.FONT_HERSHEY_PLAIN,
    font_scale = 1,
    font_thickness = 3,
    font_color = (0,0,0),
    max_image_size = 50,
    ):

    if len(random_list) < rows * columns:
        raise(Exception(f"Not enough random choices (at least {str(rows * columns)})! You have more boxes than random choices."))
    card_values = random.sample(random_list, rows * columns) # take random values from the list using the number of boxes
    random.shuffle(card_values)

    if type(background) != np.ndarray:
        background = np.zeros(shape=[500,500,3], dtype=np.uint8)
        background.fill(255)

    table_height, table_width = background.shape[:2]
    box_width, box_height = int(table_width / rows), int(table_height / columns)

    for x in range(1, table_width, box_width):
        background = cv2.line(
            background, 
            (x, 1),
            (x, table_height), 
            line_color, 
            thickness=line_thickness
        )

    for y in range(1, table_height, box_height):
        background = cv2.line(
            background, 
            (1, y), 
            (table_width, y), 
            line_color, 
            thickness=line_thickness
        )

    # draw lines on right and bottom of table (where they would be skipped in the for loops)
    background = cv2.line(
        background, 
        (table_width-line_thickness, 1), 
        (table_width-line_thickness, table_height-line_thickness), 
        line_color, 
        thickness=line_thickness
        )
    background = cv2.line(
        background, 
        (1, table_height-line_thickness), 
        (table_width-line_thickness, table_height-line_thickness), 
        line_color, 
        thickness=line_thickness
        )

    for x in range(1, rows + 1):
        for y in range(1, columns + 1):
            box_x, box_y = int(x * box_width - box_width / 2), int(y * box_height - box_height / 2)
            object = card_values[0] # take the first value in the list and delete it
            card_values.pop(0)
             
            if type(object) is str: # if object is text
                (text_width, text_height), baseline = cv2.getTextSize(object, font_type, font_scale, font_thickness)
                #text_height += baseline / 2 # add baseline to text height (it's necessary for accuracy)
                
                cv2.putText(
                    background,
                    object, 
                    (int(box_x - text_width / 2), int(box_y + text_height / 2)), 
                    font_type, 
                    font_scale, 
                    font_color,
                    font_thickness
                )
            elif type(object) is np.ndarray: # if object is an image
                img_h, img_w = object.shape[:2]
                
                if img_h > max_image_size:
                    object = image_resize(object, height=max_image_size)
                    img_h, img_w = object.shape[:2]
                if img_w > max_image_size:
                    object = image_resize(object, width=max_image_size)
                    img_h, img_w = object.shape[:2]
                
                try:
                    background = overlay_image(
                        object,
                        background,
                        (int(box_x - img_w / 2), int(box_y - img_h / 2))
                    )
                except:
                    raise(Exception("Image object is too big!"))
    return background

cards = 3
choices_list = ["1","2","3","4","5","6","7","8","9"]
images_folder = os.getcwd() + "\\images\\"

for f in os.listdir(images_folder):
    try:
        image = cv2.imread(images_folder + f, cv2.IMREAD_UNCHANGED)

        if type(image) is np.ndarray:
            choices_list.append(image)
    except:
        pass

for card_number in range(1, cards + 1):
    template = cv2.imread("cards and templates\\template.png")
    x_offset, y_offset = 50, 200
    width, height = 400,400
    cutout = template[y_offset:y_offset + height, x_offset:x_offset + width]
    
    bingo_cutout = bingo_card(
        rows = 3,
        columns = 3,
        line_color = [255, 255, 255],
        line_thickness = 2,
        font_type = cv2.FONT_HERSHEY_DUPLEX,
        font_scale = 4,
        font_thickness = 4,
        font_color = [255, 255, 255],
        max_image_size = 120, # maximum image width and height in pixels
        random_list = choices_list,
        background = cutout
    )

    template[y_offset:y_offset + height, x_offset:x_offset + width] = bingo_cutout
    cv2.imwrite("cards and templates\\Table " + str(card_number) + ".jpg", template)

cv2.destroyAllWindows()
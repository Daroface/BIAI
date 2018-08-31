def resize_csv_images(input_csvfile, output_csvfile):
    import csv
    import sys
    import os
    from PIL import Image
    amount = 0
    number = 0
    path_to_images = r"/home/daroface/BIAI/images/"
    path_to_new_images = r"/home/daroface/BIAI/images/new/"
    directory = os.path.dirname(path_to_new_images)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory) 
    with open(output_csvfile, "w", encoding="utf8", newline='') as output_csv, \
         open(input_csvfile, "r", encoding="utf8") as input_csv:
            reading_file = csv.reader(input_csv, delimiter=',') 
            writing_file = csv.writer(output_csv, delimiter=',')
            for line in reading_file:
                amount = amount + 1
            input_csv.seek(0)
            for line in reading_file:
                number = number + 1
                sys.stdout.write("\r%s/%s" % (number, amount))
                sys.stdout.flush()
                row = []
                if number != 1:
                    height = int(line[2])
                    width = int(line[3])
                    scale = 1
                    if height >= 350 and height > width:
                        scale = 300 / height
                    elif width >= 350 and width > height:
                        scale = 300 / width
                    elif height <= 250 and  height > width:
                        scale = 300 / height
                    elif width <= 250 and width > height:
                        scale = 300 / width
                    else:
                        scale = 1
                    height = int(height * scale)
                    width = int(width * scale)                    
                    row.append(line[0])
                    row.append(line[1])
                    row.append(height)
                    row.append(width)
                    row.append(line[4])
                    row.append(line[5])
                    row.append(line[6])
                    row.append(line[7])
                    """
                    if scale != 1:
                        im = Image.open(path_to_images + line[1])
                        size = int(width), int(height)
                        im_resized = im.resize(size, Image.ANTIALIAS)
                        im_resized.save(path_to_new_images + line[1], "JPEG")
                    """
                    writing_file.writerow(row)
                else:
                    writing_file.writerow(line)
                

def main():
    train_csv = r"/home/daroface/BIAI/data/train/train.csv"
    new_train_csv = r"/home/daroface/BIAI/data/train/train2.csv"
    valid_csv = r"/home/daroface/BIAI/data/valid/valid.csv"
    new_valid_csv = r"/home/daroface/BIAI/data/valid/valid2.csv"
    resize_csv_images(train_csv, new_train_csv)
    resize_csv_images(valid_csv, new_valid_csv)

main()
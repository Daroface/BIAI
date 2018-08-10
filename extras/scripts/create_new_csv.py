def getImageLabelsAndBBoxes(oid_bbox_file, my_bbox_file, oid_label_file, my_label_file):
    import csv
    global classes
    confidence = "1"

    with open(oid_bbox_file, "r", encoding="utf8") as bboxes_read, \
        open(my_bbox_file, "w", encoding="utf8", newline='') as bboxes_write, \
        open(oid_label_file, "r", encoding="utf8") as labels_read, \
        open(my_label_file, "w", encoding="utf8", newline='') as labels_write:
        reading_file = csv.reader(bboxes_read, delimiter=',')
        writing_file = csv.writer(bboxes_write, delimiter=',')
        for i in range(0, 2):
            for line in reading_file:
                for index in range(8):
                    if classes[index][0] in line[2] and confidence in line[3]:
                            writing_file.writerow(line)
                            if i == 0:
                                classes[index][2] = classes[index][2] + 1 
                            break                        
            if i == 0:
                print("BBoxes finished")
                reading_file = csv.reader(labels_read, delimiter=',')
                writing_file = csv.writer(labels_write, delimiter=',')
            else:
                print("Labels finished")
                for i in range(8):
                    print(f'{classes[i][1]}: {classes[i][2]}')
                    classes[i][2] = 1

def getImageIDS(oid_ids_file, my_labels_file, my_ids_file):    
    import csv
    import sys
    with open(oid_ids_file, "r", encoding="utf8") as ids_read, \
        open(my_labels_file, "r", encoding="utf8") as labels_read, \
        open(my_ids_file, "w", encoding="utf8", newline='') as ide_write:
        reading_ids_file = csv.reader(ids_read, delimiter=',')
        reading_labels_file = csv.reader(labels_read, delimiter=',')
        writing_ids_file = csv.writer(ide_write, delimiter=',')
        amount = 0
        number = 0
        prior = ""
        done = False
        for row in reading_labels_file:
            if row:
                amount = amount + 1
        labels_read.seek(0)
        for row in reading_labels_file:
            if row:
                number = number + 1
                sys.stdout.write("\r%s/%s " % (number, amount))
                sys.stdout.flush()
                ids_read.seek(1)   
                if number == 1:
                    prior = row[0]
                elif prior in row[0]:
                    continue
                else:          
                    for line in reading_ids_file:
                        if line:
                            if line[0] in row[0]:
                                writing_ids_file.writerow(line)                            
                                done = True
                        if done == True:
                            done = False
                            break

def add_filename(i, file_id, writer, prefix):
    name = prefix + classes[i][1]
    if classes[i][2] < 10:
        name = name + "0000" 
    elif classes[i][2] < 100:
        name = name + "000"
    elif classes[i][2] < 1000:
        name = name + "00"
    elif classes[i][2] < 10000:
        name = name + "0"
    name = name + str(classes[i][2]) + ".jpg"
    classes[i][2] = classes[i][2] + 1
    record = []
    record.append(file_id)
    record.append(name)
    writer.writerow(record)

def create_csv_with_filenames(ids_file, labels_file, filenames_file, prefix):
    import csv
    import sys
    global classes
    amount = 0
    number = 0
    with open(filenames_file, "w", encoding="utf8", newline='') as output, \
         open(labels_file, "r", encoding="utf8") as labels, \
         open(ids_file, "r", encoding="utf8") as ids:
        writing_file = csv.writer(output, delimiter=',')
        reading_ids_file = csv.reader(ids, delimiter=',')
        reading_labels_file = csv.reader(labels, delimiter=',')
        for row in reading_ids_file:
            if row:
                amount = amount + 1
        ids.seek(0)
        for row in reading_ids_file:
            number = number + 1
            sys.stdout.write("\r%s/%s" % (number, amount))
            sys.stdout.flush()
            labels.seek(0)
            for line in reading_labels_file:                    
                if line[0] in row[0]:
                    for i in range(len(classes)):
                        if classes[i][0] in line[2]:
                            if classes[i][2] <= limit:
                                add_filename(i, line[0], writing_file, prefix)
                                break

def download_images(filenames_file, ids_file, path):
    import requests
    import os
    import csv
    import sys
    url = ""
    name = ""
    amount = 0
    number = 0
    with open(filenames_file, "r", encoding="utf8") as filenames, \
         open(ids_file, "r", encoding="utf8") as ids:
        reading_ids_file = csv.reader(ids, delimiter=',')
        reading_filenames_file = csv.reader(filenames, delimiter=',')
        for row in reading_filenames_file:
            amount = amount + 1
        filenames.seek(0)
        for row in reading_filenames_file:
            name = row[1]
            number = number + 1
            sys.stdout.write("\r%s/%s" % (number, amount))
            sys.stdout.flush()
            ids.seek(0)
            for line in reading_ids_file:
                if row[0] in line[0]:
                    url = line[2]
                    break
            directory = os.path.dirname(path)
            try:
                os.stat(directory)
            except:
                os.mkdir(directory) 
            with open(path + name, 'wb') as handle:
                response = requests.get(url, stream=True)

                if not response.ok:
                    print(response)

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

def create_record(line, i, reading_ids_file, reading_filenames_file, writing_file, path):
    import cv2
    record = []
    record.append(classes[i][1])
    for row in reading_filenames_file:
        if line[0] in row[0]:
            filename = row[1]           
            im = cv2.imread(path + filename, cv2.IMREAD_UNCHANGED)
            width = im.shape[1]
            height = im.shape[0]
            record.append(filename)
            record.append(str(height))
            record.append(str(width))
            record.append(line[5])
            record.append(line[4])
            record.append(line[7])
            record.append(line[6])    
            writing_file.writerow(record)         
            break
        
def create_new_csv(output_csvfile, bboxes_file, ids_file, filenames_file, path):
    import csv
    import sys
    amount = 0
    number = 0
    with open(output_csvfile, "w", encoding="utf8", newline='') as output, \
         open(bboxes_file, "r", encoding="utf8") as bboxes, \
         open(filenames_file, "r", encoding="utf8") as filenames, \
         open(ids_file, "r", encoding="utf8") as ids:
            reading_bboxes_file = csv.reader(bboxes, delimiter=',')
            reading_ids_file = csv.reader(ids, delimiter=',')
            reading_filenames_file = csv.reader(filenames, delimiter=',') 
            writing_file = csv.writer(output, delimiter=',')
            for line in reading_bboxes_file:
                amount = amount + 1
            bboxes.seek(0)
            for line in reading_bboxes_file:
                number = number + 1
                sys.stdout.write("\r%s/%s" % (number, amount))
                sys.stdout.flush()
                filenames.seek(0)
                ids.seek(0)
                for i in range(len(classes)):
                    if classes[i][0] in line[2]:
                        create_record(line, i, reading_ids_file, reading_filenames_file, writing_file, path)

def run(output, bboxes, ids, labels, filenames, path, prefix):
    """
    print("Create file with filenames...")
    create_csv_with_filenames(ids, labels, filenames, prefix)    
    print("\nFile with filenames: DONE!\n")
    """
    print("Downloading images...")
    download_images(filenames, ids, path) 
    print("\nDownloading images: DONE!\n")
    
    """
    print("Create new csv...")
    create_new_csv(output, bboxes, ids, filenames, path)
    print("\nCreating new csv: DONE!")
    """


limit = 200

classes = [["/m/01lsmm", "scissors", 1], \
           ["/m/02jvh9", "mug", 1],                                                                                                                             
           ["/m/01c648", "laptop", 1], \
           ["/m/0bt_c3", "notebook", 1], \
           ["/m/0k1tl", "pen", 1], \
           ["/m/024d2", "calculator", 1], \
           ["/m/0hdln", "ruler", 1], \
           ["/m/0dtln", "lamp", 1]]

def main():

    train_prefix = "oid_train_"
    valid_prefix = "oid_valid_"
    test_prefix = "oid_test_"

    ######### TODO ######################
    #####################################
    #####################################
    #Ustaw sieżkę u siebie lokalnie do repo###
    file_path = r"sciezka/do/repo/extras/"

    train_path = r"sciezka/do/repo/images/"
    valid_path = r"sciezka/do/repo/images/"
    test_path = r"sciezka/do/repo/images/"

    oid_train_bboxes_file = file_path + r"oid/train-annotations-bbox.csv"
    oid_train_labels_file = file_path + r"oid/labels/train-annotations-human-imagelabels-boxable.csv"
    oid_train_ids_file = file_path + r"oid/ids/train-images-boxable-with-rotation.csv"

    oid_valid_bboxes_file = file_path + r"oid/validation-annotations-bbox.csv"
    oid_valid_labels_file = file_path + r"oid/labels/validation-annotations-human-imagelabels-boxable.csv"
    oid_valid_ids_file = file_path + r"oid/ids/validation-images-with-rotation.csv"

    oid_test_bboxes_file = file_path + r"oid/test-annotations-bbox.csv"
    oid_test_labels_file = file_path + r"oid/labels/test-annotations-human-imagelabels-boxable.csv"
    oid_test_ids_file = file_path + r"oid/ids/test-images-with-rotation.csv"
        
    train_output_csvfile = file_path + r"train/train.csv"
    train_bboxes_file = file_path + r"train/train-image-bboxes.csv"
    train_ids_file = file_path + r"train/train-image-ids.csv"
    train_labels_file = file_path + r"train/train-image-labels.csv"
    train_filenames_file = file_path + r"train/train-image-filenames.csv" 

    valid_output_csvfile = file_path + r"valid/valid.csv"
    valid_bboxes_file = file_path + r"valid/valid-image-bboxes.csv"
    valid_ids_file = file_path + r"valid/valid-image-ids.csv"
    valid_labels_file = file_path + r"valid/valid-image-labels.csv"
    valid_filenames_file = file_path + r"valid/valid-image-filenames.csv"

    test_output_csvfile = file_path + r"test/test.csv"
    test_bboxes_file = file_path + r"test/test-image-bboxes.csv"
    test_ids_file = file_path + r"test/test-image-ids.csv"
    test_labels_file = file_path + r"test/test-image-labels.csv"
    test_filenames_file = file_path + r"test/test-image-filenames.csv"
    """
    print("Making train image bboxes and labels")
    getImageLabelsAndBBoxes(oid_train_bboxes_file, train_bboxes_file, oid_train_labels_file, train_labels_file)
    print("Making train image bboxes and labels: COMPETED!\n")
    print("Making valid image bboxes and labels")
    getImageLabelsAndBBoxes(oid_valid_bboxes_file, valid_bboxes_file, oid_valid_labels_file, valid_labels_file)
    print("Making valid image bboxes and labels: COMPETED!\n")
    print("Making test image bboxes and labels")
    getImageLabelsAndBBoxes(oid_test_bboxes_file, test_bboxes_file, oid_test_labels_file, test_labels_file)
    print("Making test image bboxes and labels: COMPETED!\n")
    
    print("Making train image ids")
    getImageIDS(oid_train_ids_file, train_labels_file, train_ids_file)
    print("Making train image ids: COMPETED!\n")
    print("Making valid image ids")
    getImageIDS(oid_valid_ids_file, valid_labels_file, valid_ids_file)
    print("Making valid image ids: COMPETED!\n")
    print("Making test image ids")
    getImageIDS(oid_test_ids_file, test_labels_file, test_ids_file)
    print("Making test image ids: COMPETED!\n")  
    """
    print("\nFor train: 1\nFor valid: 2\nFor test: 3\nFor all: 4\nFor end: 5")
    choice = input()
    while True:
        if choice in "1":
            run(train_output_csvfile, train_bboxes_file, train_ids_file, train_labels_file, train_filenames_file, train_path, train_prefix)
            print("\nFor train: 1\nFor valid: 2\nFor test: 3\nFor all: 4\nFor end: 5")
            choice = input()
        elif choice in "2":
            run(valid_output_csvfile, valid_bboxes_file, valid_ids_file, valid_labels_file, valid_filenames_file, valid_path, valid_prefix)
            print("\nFor train: 1\nFor valid: 2\nFor test: 3\nFor all: 4\nFor end: 5")
            choice = input()
        elif choice in "3":
            run(test_output_csvfile, test_bboxes_file, test_ids_file, test_labels_file, test_filenames_file, test_path, test_prefix)
            print("\nFor train: 1\nFor valid: 2\nFor test: 3\nFor all: 4\nFor end: 5")
            choice = input()
        elif choice in "4":
            run(valid_output_csvfile, valid_bboxes_file, valid_ids_file, valid_labels_file, valid_filenames_file, valid_path, valid_prefix)
            run(test_output_csvfile, test_bboxes_file, test_ids_file, test_labels_file, test_filenames_file, test_path, test_prefix)
            run(train_output_csvfile, train_bboxes_file, train_ids_file, train_labels_file, train_filenames_file, train_path, train_prefix)
            print("\nFor train: 1\nFor valid: 2\nFor test: 3\nFor all: 4\nFor end: 5")
            choice = input()
        elif choice in "5":
            break
    print("Program finished.")

main()

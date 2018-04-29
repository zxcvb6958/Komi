import os
import os.path as osp


def generate_list(root_dir, save_as):
    file = open(save_as, 'w')

    person_name = os.listdir(root_dir)
    count = 1

    for person in person_name:
        person = osp.join(root_dir, person)
        person_images = os.listdir(person)

        for person_image in person_images:
            person_image = osp.join(person, person_image)
            file.write(person_image + '\t' + str(count) + '\n')
    
        count += 1

    file.close()


if __name__ == '__main__':
    root_dir = 'data/lfw'
    save_as = 'data/test/images.txt'
    generate_list(root_dir, save_as)

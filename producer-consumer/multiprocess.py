
from multiprocessing import Process, Queue, Value, Array
import requests
import time
import os
import ctypes 

number_of_processes = 4

def get_image_name_from_url(image_url):
    return image_url[image_url.rindex('/')+1:len(image_url)]

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Unable to download image:{image_url}")

def return_image_urls_queue():
    image_urls = [
        "https://www.kasandbox.org/programming-images/avatars/spunky-sam.png",
        "https://www.kasandbox.org/programming-images/avatars/spunky-sam-green.png",
        "https://www.kasandbox.org/programming-images/avatars/purple-pi.png",
        "https://www.kasandbox.org/programming-images/avatars/purple-pi-teal.png",
        "https://www.kasandbox.org/programming-images/avatars/purple-pi-pink.png",
        "https://www.kasandbox.org/programming-images/avatars/primosaur-ultimate.png",
        "https://www.kasandbox.org/programming-images/avatars/primosaur-tree.png",
        "https://www.kasandbox.org/programming-images/avatars/primosaur-sapling.png",
        "https://www.kasandbox.org/programming-images/avatars/orange-juice-squid.png",
        "https://www.kasandbox.org/programming-images/avatars/old-spice-man.png",
        "https://www.kasandbox.org/programming-images/avatars/old-spice-man-blue.png",
        "https://www.kasandbox.org/programming-images/avatars/mr-pants.png",
        "https://www.kasandbox.org/programming-images/avatars/mr-pants-purple.png",
        "https://www.kasandbox.org/programming-images/avatars/mr-pants-green.png",
        "https://www.kasandbox.org/programming-images/avatars/marcimus.png",
        "https://www.kasandbox.org/programming-images/avatars/marcimus-red.png",
        "https://www.kasandbox.org/programming-images/avatars/marcimus-purple.png",
        "https://www.kasandbox.org/programming-images/avatars/marcimus-orange.png",
        "https://www.kasandbox.org/programming-images/avatars/duskpin-ultimate.png",
        "https://www.kasandbox.org/programming-images/avatars/duskpin-tree.png",
        "https://www.kasandbox.org/programming-images/avatars/duskpin-seedling.png",
        "https://www.kasandbox.org/programming-images/avatars/duskpin-seed.png",
        "https://www.kasandbox.org/programming-images/avatars/duskpin-sapling.png",
    ]

    image_urls_to_download = Queue()

    for image in image_urls:
        image_urls_to_download.put(image)
    return image_urls_to_download

def producer_job(id: int,image_urls_queue: Queue, image_content_queue: Queue, exceptions_queue):
    exceptions_queue.put('korami')
    print(f"Started producer job {id}")
    while image_urls_queue.empty() != True:
        image_url = image_urls_queue.get()
        image_content = download_image(image_url)
        image_name = get_image_name_from_url(image_url)
        image_content_queue.put({image_name:image_content})
        print(f'Process {str(id)} produced {image_name} image.')
    print(f"Ended producer job {id}")
        
def consumer_job(id: int,image_content_queue: Queue, num, exceptions_queue):
    print(f"Started consumer job {id}")
    while image_content_queue.empty() != True:
        image_info: dict = image_content_queue.get()
        image_name = list(image_info.keys())[0]
        image_content = list(image_info.values())[0]
        if not os.path.exists('images'):
            os.mkdir('images')
        with open(f'images/{image_name}',mode='wb') as f:
            f.write(image_content)
            
        with num.get_lock():
            num.value += 1
        
        print(f'Process {str(id)} consumed {image_name} image.')    
       
def main():
    image_content_queue = Queue()
    image_urls_queue = return_image_urls_queue()
    processed_images_count = Value(ctypes.c_int, 0)

    producers = []
    consumers = []

    for id in range(number_of_processes):
        pp = Process(target=producer_job,args=(id,image_urls_queue,image_content_queue))
        cp = Process(target=consumer_job,args=(id,image_content_queue, processed_images_count))
        producers.append(pp)
        consumers.append(cp)

    for producer in producers:
        producer.start()
    time.sleep(10)
    for consumer in consumers:
        consumer.start()

    for producer in producers:
        producer.join()
      
    print(f"Successfully processed images: {str(processed_images_count.value)}")

if __name__ == '__main__':
    main()
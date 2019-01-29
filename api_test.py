# importing the requests library
import requests
import json
import csv
import time

import ipdb

from  PIL import Image


def save_images(submissions, file_count):
    print(file_count)
    print(len(submissions['data']))

    for x in range(500):
        if x % 50 == 0:
            time.sleep(30)
        curr_submission = submissions['data'][x]
        image_url = curr_submission['url']
        author = curr_submission['author']
        # only take when the file is jpg and not nested in a site
        if '.jpg' in image_url:
            try:
                # get the list of comments
                submission_id = curr_submission['id']

                comment_id_url = "https://api.pushshift.io/reddit/submission/comment_ids/" + submission_id
                time.sleep(10)
                comment_ids = requests.get(url=comment_id_url).json()['data']

                if comment_ids:
                    # loop through the comment ids and find the comment where op said solved
                    # then find the first level comment of that comment
                    comment_api_url = "https://api.pushshift.io/reddit/comment/search/"
                    comment_api_params = {"ids": ','.join(map(str, comment_ids))}
                    time.sleep(10)
                    comment_list = requests.get(url=comment_api_url, params=comment_api_params).json()['data']

                    comment_body = ""
                    for comment in comment_list:
                        curr_author = comment['author']
                        if curr_author ==  author and "solved" in comment['body'].lower():
                            parent_id = comment['parent_id']
                            print(parent_id)
                            time.sleep(10)
                            parent_api_params = {"ids": parent_id}
                            ipdb.set_trace()
                            parent_comment = requests.get(url=comment_api_url, params=parent_api_params).json()['data']
                            comment_body = parent_comment[0]['body']

                    deleted_message = "*I am a bot, and this action was performed automatically"
                    if not comment_body and deleted_message not in comment_body:
                        # store the images
                        full_file_name = str(file_count) + '.jpg'
                        time.sleep(10)
                        im = requests.get(image_url)
                        with open('images/' + full_file_name, 'wb') as f:
                            f.write(im.content)

                        img = Image.open('images/' + full_file_name)  # open the image file
                        img.verify()  # verify that it is, in fact an image

                        # make a csv file with image name, title, comment, id, permalink
                        permalink = curr_submission['permalink']
                        title = curr_submission['title']
                        with open('info.csv', mode='a') as info:
                            csv_writer = csv.writer(info)
                            csv_writer.writerow([full_file_name, title, comment_body, submission_id, permalink])
                        file_count = file_count + 1
            except (IOError, SyntaxError) as e:
                print('Bad file')
    return file_count


# api-endpoint
URL = "https://api.pushshift.io/reddit/search/submission"

with open('info.csv', mode='w') as info:
    fieldnames = ['image_name', 'title', 'permalink']
    writer = csv.DictWriter(info, fieldnames=fieldnames)
    writer.writeheader()

count = 0
before = 7
while count < 10000:
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'subreddit': "whatisthisthing", 'after': str(before+3)+"d", 'before': str(before)+"d", 'size': "500"}
    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)
    before += 3

    # extracting data in json format
    data = r.json()
    count = save_images(data, count)

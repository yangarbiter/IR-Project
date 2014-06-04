#!/bin/python3

import httplib, json, time

API_KEY=''

def main():
    conn = httplib.HTTPConnection("api.ted.com")
    for vid in range(511,2007):
        print vid
        f = open(str(vid), "w")

        time.sleep(1)
        conn.request("GET", "/v1/talks/" + str(vid) + ".json?api-key=" + API_KEY)
        res = conn.getresponse()
        if res.status == 404:
            conn.close()
            continue
        res = res.read().encode('utf-8')
        res = json.loads(res)

        f.write("title: ")
        f.write(res['talk']['name'].encode('utf-8') + '\n')

        f.write("speaker: ")
        for speaker in res['talk']["speakers"][:-1]:
            f.write(speaker['speaker']['name'].encode('utf-8') + ', ')
        f.write(res['talk']['speakers'][-1]['speaker']['name'].encode('utf-8') + '\n')

        f.write("description: ")
        f.write(res['talk']['description'].encode('utf-8') + '\n')

        f.write("biography: ")
        for speaker in res['talk']["speakers"]:
            time.sleep(1)
            conn.request("GET", "/v1/speakers/" + str(speaker['speaker']['id']) + ".json?api-key=" + API_KEY)
            tres = conn.getresponse().read().encode('utf-8')
            conn.close()
            tres = json.loads(tres)
            f.write(tres['speaker']['description'].encode('utf-8') + ' ')
            f.write(tres['speaker']['whotheyare'].encode('utf-8') + ' ')
            f.write(tres['speaker']['whylisten'].encode('utf-8') + ' ')
        f.write('\n')

        f.write("tags: ")
        for tag in res['talk']['tags'][:-1]:
            f.write(tag['tag'] + ', ')
        if len(res['talk']['tags']) >= 1:
            f.write(res['talk']['tags'][-1]['tag'].encode('utf-8') + '\n')

        f.close()


if __name__ == '__main__':
    main()

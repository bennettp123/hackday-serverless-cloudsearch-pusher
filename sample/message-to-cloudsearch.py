#!/usr/bin/env

import sys
import json

#original_doc = json.load(sys.stdin)

#with open('an-actual-message.json', 'r') as f:
#    original_doc = json.load(f)

with open('event.json', 'r') as f:
    event = json.load(f)

import pdb; pdb.set_trace()

content = original_doc['message']['content']
ident = original_doc['message']['identifier']
status = content['status']
kind = content['kind']
assets = content['assets']
topics = list(set(content['secondaryTopics'] + [content['primaryTopic']]))
product = content['product']
source = content['source']
items = content['items']

heading = [x for x in items if x['kind'] == 'heading']
head_kicker = [x for x in items if x['kind'] == 'head-kicker']
homepage_head = [x for x in items if x['kind'] == 'homepage-head']
homepage_teaser = [x for x in items if x['kind'] == 'homepage-teaser']
canonical_url = [x for x in items if x['kind'] == 'canonical-url']
canonical_title = [x for x in items if x['kind'] == 'canonical-title']
keywords = [x for x in items if x['kind'] == 'keywords']
main_image = [x for x in items if x['kind'] == 'main-image']
actual_content = [x for x in items if x['kind'] == 'content']

#import pdb; pdb.set_trace()

flatten = lambda l: [item for sublist in l for item in sublist]

search_doc = {
    "type": "add",
    "id": ident,
    "fields": {
        "heading": ' '.join(x['text'] for x in heading),
        "head_kicker": ' '.join(x['text'] for x in head_kicker),
        "homepage_head": ' '.join(x['text'] for x in homepage_head),
        "homepage_teaser": ' '.join(x['text'] for x in homepage_teaser),
        "canonical_url": [x['canonicalUrl'] for x in canonical_url],
        "canonical_title": ' '.join(x['text'] for x in canonical_title),
        "keywords": flatten([x['keywords'] for x in keywords]),
        "main_image": [x['name'] for x in main_image],
        "content": ' '.join([y['text'] for y in flatten([x['blocks'] for x in actual_content])]),
        "status": status,
        "kind": kind,
        "topics": topics,
        "product": product,
        "source": source,
    },
}

#import pdb; pdb.set_trace()
#print('cool.')

#print(json.dumps(search_doc['fields']))
print(json.dumps([search_doc]))


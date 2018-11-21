import json
import logging
import boto3

logger = logging.getLogger()

def hello(event, context):
    #body = {
    #    "message": "Go Serverless v1.0! Your function executed successfully!",
    #    "input": event
    #}

    #response = {
    #    "statusCode": 200,
    #    "body": json.dumps(body)
    #}

    #return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    #"""
    #return {
    #    "message": "Go Serverless v1.0! Your function executed successfully!",
    #    "event": event
    #}
    #"""

    #logger.info(json.dumps({"event": event, "context": context}))
    logger.setLevel(logging.INFO)
    logger.debug(json.dumps({"event": event}))
    
    docs = []

    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            original_doc = json.loads(body['Message'])

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
            
            if len(main_image) > 1:
                logger.warning('More than one main_image found! Ignoring all but the first.')

            if len(canonical_url) > 1:
                logger.warning('More than one canonical_url found! Ignoring all but the first.')

            #import pdb; pdb.set_trace()
            
            flatten = lambda l: [item for sublist in l for item in sublist]
            
            def first_or_none(l):
                for item in l:
                    return item
                return None
            
            search_doc = {
                "type": "add",
                "id": ident,
                "fields": {
                    "heading": ' '.join(x['text'] for x in heading),
                    "head_kicker": ' '.join(x['text'] for x in head_kicker),
                    "homepage_head": ' '.join(x['text'] for x in homepage_head),
                    "homepage_teaser": ' '.join(x['text'] for x in homepage_teaser),
                    "canonical_url": first_or_none([x['canonicalUrl'] for x in canonical_url]),
                    "canonical_title": ' '.join(x['text'] for x in canonical_title),
                    "keywords": flatten([x['keywords'] for x in keywords]),
                    "main_image": first_or_none([x['name'] for x in main_image]),
                    "content": ' '.join([y.get('text', '') for y in flatten([x['blocks'] for x in actual_content])]),
                    "status": status,
                    "kind": kind,
                    "topics": topics,
                    "product": product,
                    "source": source,
                },
            }

            for k,v in search_doc['fields'].items():
                if v is None:
                    del search_doc['fields'][k]

            logging.info(search_doc)
            docs += [search_doc]

        except Exception as e:
            logging.exception(e)
            logging.info(event)

        if docs:
            try:
                client = boto3.client('cloudsearchdomain', endpoint_url='https://doc-swm-content-search-dev-xnjr4k4s4lqv6dxyuss5boi34a.ap-southeast-2.cloudsearch.amazonaws.com')
                response = client.upload_documents(
                        documents=json.dumps(docs),
                        contentType='application/json')

                logging.info(response)
            except Exception as e:
                logging.exception(e)
                logging.info(event)
                logging.info(docs)


import argparse
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
  import Features, EntitiesOptions, KeywordsOptions

def run(username, password, version, text, keywords):
    natural_language_understanding = NaturalLanguageUnderstandingV1(
      username=username,
      password=password,
      version=version)
    response = natural_language_understanding.analyze(
      text=text,
      features=Features(
        keywords=KeywordsOptions(
          limit=keywords))).get_result()
    return response['keywords']

def main():
    parser = argparse.ArgumentParser(description='Keyword Extraction from Text')
    parser.add_argument('-u', '--username', default='52a2b5a9-bbc9-41c8-abe8-de887e961ae5', type=str, help='username')
    parser.add_argument('-p', '--password', default='HXlpN5EGcrXr', type=str, help='password')
    parser.add_argument('-v', '--version', default='2018-03-16', type=str, help='api version')
    parser.add_argument('-t', '--text', type=str, help='text to analyze')
    parser.add_argument('-k', '--keywords', default=2, type=int, help='number of keywords')
    args = parser.parse_args()
    res = run(args.username, args.password, args.version, args.text, args.keywords)
    print(res)

if __name__ == '__main__':
    main()
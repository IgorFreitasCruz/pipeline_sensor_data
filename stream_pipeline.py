from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import pubsub_v1
from google.cloud import bigquery
import apache_beam as beam
import os
import argparse
import logging
import re

service_account_key = r"soulcode-331512-8fe205b6b6f8.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key

PROJECT_ID = 'soulcode-331512'
schema = """timelocal:TIMESTAMP,
            sensor_reading:FLOAT"""
TOPIC = 'projects/soulcode-331512/topics/sensor_topic'

def clean_logs(data):

	PATTERNS = [r'\d{4}.\d{2}.\d{2}\s\d+:\d{2}:\d{2}', r'[^:\s]\d+\.\d$']

	result = []
	for match in PATTERNS:
			try:
					reg_match = re.search(match, data).group()
					if reg_match:
							result.append(reg_match)
					else:
							result.append(" ")
			except:
					print("There was as error with the regex search")

	result = [x.strip() for x in result]
	res = ','.join(result)

	return res

class Split(beam.DoFn):

	def process(self, element):
			element = element.split(',')
			return [{
					'timelocal': element[0],
					'sensor_reading': element[1]
					}]

def main():

	# parser = argparse.ArgumentParser()
	# parser.add_argument("--input_topic")
	# parser.add_argument("--output")
	# known_args = parser.parse_known_args(argv)

	pipeline_options = {
    'project': 'soulcode-331512' ,
    'runner': 'DataflowRunner',
    'region': 'southamerica-east1',
    'staging_location': 'gs://data_ingestion_soulcode/staging',
    'temp_location': 'gs://data_ingestion_soulcode/temp',
    # 'template_location': 'gs://data-lake-soul-gcp/template/stream_voos',
    # 'save_main_session': True ,
    'streaming' : True }

	pipeline_options = PipelineOptions.from_dictionary(pipeline_options)

	p = beam.Pipeline(options=pipeline_options)

	(p
		| 'ReadData' >> beam.io.ReadFromPubSub(topic=TOPIC).with_output_types(bytes)
		| "Decode" >> beam.Map(lambda x: x.decode('utf-8'))
		| "Clean Data" >> beam.Map(clean_logs)
		| 'ParseCSV' >> beam.ParDo(Split())
		| 'WriteToBigQuery' >> beam.io.WriteToBigQuery('{0}:userlogs.sensordata'.format(PROJECT_ID),
																									schema=schema,
																									create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
																									write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
		)

	result = p.run()
	result.wait_until_finish()


if __name__ == '__main__':
    logger = logging.getLogger().setLevel(logging.INFO)
    main()

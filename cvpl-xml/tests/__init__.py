#   coding utf-8
'''
Unit tests.
'''

import canvas as cv
import canvas.tests as cvt

from canvas.plugins import xml

nasty_xml = '<x>۩</x>'
nasty_xml_bytes = nasty_xml.encode()

client = cvt.create_client()

@cvt.test('Basic utilities')
def test_utils():
	cvt.assertion(
		'Vanilla round-tripping unicode is identity',
		xml.serialize(xml.deserialize(nasty_xml)) == nasty_xml
	)

	cvt.assertion(
		'Bytes round-tripping unicode is identity',
		xml.serialize(xml.deserialize(nasty_xml_bytes), as_bytes=True) == nasty_xml_bytes
	)

@cvt.test('Endpoint integration')
def test_endpoint_integration():
	@cv.endpoint('/api/xml_test', expects='xml')
	class XMLTestEndpoint:

		def on_post(self, context):
			if not isinstance(context.request, xml.element_t):
				cvt.fail('XML request body not deserialized')
			return context.request.tag

	cvt.reset_controllers()

	is_xml_response = lambda r: (
		r.data.startswith(b'<response>') and 
		'xml' in r.headers['Content-Type']
	)

	response = client.post('/api/xml_test', content_type='text/xml', data=nasty_xml)
	cvt.assertion(
		'Endpoint receives XML',
		response.data == b'x'
	)

	response = client.post('/api/xml_test', content_type='application/json')
	cvt.assertion(
		'Endpoint 415s illegal content type',
		response.status_code == 415
	)

	response = client.get('/api/xml_test')
	cvt.assertion(
		'On XML endpoint error returns XML',
		is_xml_response(response)
	)

	response = client.get('/api/not_xml_test')
	cvt.assertion(
		'JSON still default',
		not is_xml_response(response)
	)

	xml.plugin_config.prefer_xml = True
	response = client.get('/api/not_xml_test')
	cvt.assertion(
		'XML default overrides',
		is_xml_response(response)
	)

@cvt.test('JSON hooks')
def test_json_hooks():
	json_input = {
		'element': xml.element('x')
	}

	json_data = cv.serialize_json(json_input)
	cvt.assertion(
		'XML values serialized',
		'<x/>' in json_data
	)

	json_output = cv.deserialize_json(json_data)
	cvt.assertion(
		'XML values deserialized',
		isinstance(json_output['element'], xml.element_t)
	)

@cvt.test('Model integration')
def test_model_integration():
	#	Mostly a crash test...

	@cv.model('xml_test', {
		'id': cv.Column('serial', primary_key=True),
		'xml': cv.Column('xml')
	})
	class XMLTestModel: pass

	cvt.reset_model()
	session = cv.create_session()
	
	instance = XMLTestModel()
	instance.xml = xml.deserialize(nasty_xml)

	session.save(instance).commit().reset()

	reloaded = XMLTestModel.get(instance.id, session)

	cvt.assertion(
		'XML selection deserialized with encoding',
		(
			isinstance(reloaded.xml, xml.element_t) and
			reloaded.xml.text == '۩'
		)
	)

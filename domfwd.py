
def app(env, start_response):
	status = '200 OK'
	response_headers = [
		('Content-type', 'text/plain'),
		('Content-Length', '0')
	]
	start_response(status, response_headers)
	return iter([])

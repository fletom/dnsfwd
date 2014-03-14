import socket
import dns.exception
import dns.resolver
import pymemcache.client
from werkzeug.wrappers import Request

resolver = dns.resolver.Resolver()
resolver.lifetime = 0.500

# Try a local memcached, but do without if we can't connect
cache = pymemcache.client.Client(('localhost', 11211))
try:
	cache.get('test')
except socket.error:
	cache = None


def lookup_fwd(domain, rdepth = 1):
	"""Look up the forwarding address for a domain."""
	
	if cache:
		cached = cache.get(domain)
		if cached is not None:
			return cached
	
	try:
		answer = resolver.query(domain, 'CNAME', tcp = True)
	except (
		dns.resolver.NXDOMAIN,
		dns.resolver.NoAnswer,
		dns.resolver.NoNameservers,
		dns.exception.Timeout
	):
		return None
	
	cname = answer[0].to_text().rstrip('.')
	
	ending = '.domfwd.com'
	
	if not cname.endswith(ending):
		# It could be an intermediary CNAME that points to our CNAME, which should work but not get stuck in a loop
		
		rdepth += 1
		if rdepth > 3:
			return None
		
		return lookup_fwd(cname, rdepth)
	
	fwd_to = cname[:-len(ending)]
	
	if fwd_to == 'unwww' and domain.startswith('www.'):
		fwd_to = domain[4:]
	
	if cache:
		cache.set(domain, fwd_to, answer.rrset.ttl)
	
	return fwd_to


def app(environ, start_response):
	request = Request(environ)
	
	domain, _, port = request.host.partition(':')
	
	fwd_to = lookup_fwd(domain)
	
	status = '301 Moved Permanently'
	if fwd_to is not None:
		location = 'http://' + fwd_to + (':' + port if port else '') + request.path
	else:
		location = 'http://domfwd.com/#improperly_configured'
	
	response_headers = [
		('Location', location),
	]
	start_response(status, response_headers)
	return ()

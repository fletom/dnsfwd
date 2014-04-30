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


def dns_lookup(domain, type):
	try:
		answers = resolver.query(domain, type, tcp = True)
	except (
		dns.resolver.NXDOMAIN,
		dns.resolver.NoAnswer,
		dns.resolver.NoNameservers,
		dns.exception.Timeout
	):
		return [], None
	else:
		return [a.to_text() for a in answers], answers.rrset.ttl


def lookup_cname(domain):
	cnames, ttl = dns_lookup(domain, 'CNAME')
	return cnames[0].rstrip('.') if cnames else None, ttl


def lookup_txts(domain):
	txts, ttl = dns_lookup(domain, 'TXT')
	return [txt.strip('"') for txt in txts], ttl


def lookup_fwd(domain, rdepth = 1):
	"""Look up the forwarding address for a domain."""
	dnsfwd_record_ending = '.dnsfwd.com'
	
	if cache:
		cached = cache.get(domain)
		if cached is not None:
			return cached
	
	cname, ttl = lookup_cname(domain)
	
	if cname is None:
		txts, ttl = lookup_txts(domain)
		for txt in txts:
			# DNSFwd TXT format
			dnsfwd_txt_prefix = 'dnsfwd '
			if txt.lower().startswith(dnsfwd_txt_prefix):
				cname = txt[len(dnsfwd_txt_prefix):] + dnsfwd_record_ending
				break
			
			# DNSimple ALIAS format
			dnsimple_alias_prefix = 'alias for '
			if txt.lower().startswith(dnsimple_alias_prefix):
				cname = txt[len(dnsimple_alias_prefix):]
				break
	
	if cname is None:
		return None
	
	if not cname.endswith(dnsfwd_record_ending):
		# It could be an intermediary CNAME that points to our CNAME, which should work but not get stuck in a loop.
		
		rdepth += 1
		if rdepth > 3:
			return None
		
		return lookup_fwd(cname, rdepth)
	
	fwd_to = cname[:-len(dnsfwd_record_ending)]
	
	if cache:
		cache.set(domain, fwd_to, ttl)
	
	return fwd_to


def app(environ, start_response):
	request = Request(environ)
	
	domain, _, port = request.host.partition(':')
	
	fwd_to = lookup_fwd(domain)
	
	if fwd_to == 'unwww' and domain.startswith('www.'):
		fwd_to = domain[4:]
	
	status = '301 Moved Permanently'
	if fwd_to is not None:
		location = 'http://' + fwd_to + (':' + port if port else '') + request.path
	else:
		location = 'http://dnsfwd.com/#improperly_configured'
	
	response_headers = [
		('Content-Length', '0'),
		('Location', location),
	]
	start_response(status, response_headers)
	return ()

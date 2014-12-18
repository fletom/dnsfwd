import dns.exception
import dns.resolver


resolver = dns.resolver.Resolver()
resolver.lifetime = 0.500


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

import sh
import sys

if __name__ == '__main__':
	docker = sh.docker.bake(_long_sep = ' ', _out = sys.stdout)
	curl = sh.curl.bake(_long_sep = ' ', _out = sys.stdout)
	try:
		docker.network.create('dnsfwd_test', driver = 'bridge')
		docker.run.bake(rm = True, detach = True, network = 'dnsfwd_test', name = 'memcached_test')('memcached:alpine')
		docker.build('.', t = 'fletom/dnsfwd')
		docker.run.bake(
			rm = True,
			detach = True,
			network = 'dnsfwd_test',
			name = 'dnsfwd_test',
			publish = '8000:8000',
			e = 'MEMCACHE_HOST=memcached_test',
		)('fletom/dnsfwd')
		while 'Listening at: http://0.0.0.0:8000' not in docker.logs('dnsfwd_test').stderr.decode():
			print('waiting for server...')
		c = curl('-I', 'localhost:8000', H = 'Host: www.fletom.com', _out = None)
		assert 'HTTP/1.1 301 Moved Permanently' in c
		assert 'Location: http://fletom.com/' in c
		c = curl('-I', 'localhost:8000', H = 'Host: tomalty.com', _out = None)
		assert 'HTTP/1.1 301 Moved Permanently' in c
		assert 'Location: http://fletom.com/' in c
	finally:
		docker = docker.bake(_ok_code = [0, 1])
		docker.stop('memcached_test')
		docker.stop('dnsfwd_test')
		docker.network.rm('dnsfwd_test')

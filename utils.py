def cut_prefix(s, prefix):
	if not s.startswith(prefix):
		return None
	return s[len(prefix):]


def cut_suffix(s, suffix):
	if not s.endswith(suffix):
		return None
	return s[:-len(suffix)]

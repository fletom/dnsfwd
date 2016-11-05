$(function() {
	var $using_cname_in = $('#using_cname_in');
	var $using_cname_out = $('#using_cname_out');
	var $using_txt_in = $('#using_txt_in');
	var $using_txt_out = $('#using_txt_out');
	
	$using_cname_in.on('input', function() {
		if (!$using_cname_in.val()) {
			$using_cname_out.val('');
		}
		else {
			$using_cname_out.val($using_cname_in.val() + '.dnsfwd.com');
		}
	});
	
	$using_txt_in.on('input', function() {
		if (!$using_txt_in.val()) {
			$using_txt_out.val('');
		}
		else {
			$using_txt_out.val('DNSfwd ' + $using_txt_in.val());
		}
	});
	
	$('input[type=text]').on('click', function() {
		this.setSelectionRange(0, this.value.length);
	});
});

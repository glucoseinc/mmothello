function redirect () {
    window.top.location.href = {{ url }};
}

$(document).ready(function() {
	redirect();
    });
function create_login() {
	$('.form form').animate({height: "toggle"});
}

function open_close_login(element) {
	if (element == 'login') {
		$('.body-login').animate({opacity: "toggle", animation: "fadeIn both 1s;"});
		$('body').toggleClass('open');
	} else {
		$('.body-login').animate({opacity: "toggle", animation: "fadeIn reverse both 1.5s"});
		$('body').toggleClass('open');
	}
}

function menu_open() {
    $('.menu-button').toggleClass('open');
    $('.menu').toggleClass('open');
    $('header').toggleClass('open');
    $('.link').toggleClass('open');
    $('.head-menu').toggleClass('open');
    $('.left-head-menu').toggleClass('open');
    $('main').toggleClass('open');
    $('body').toggleClass('open');
}

function clipAvatars() {
    $('.modal-window').toggle("clip")
}

let selectedAvatar = null;

function selectAvatar(element) {
    if (selectedAvatar) {
        selectedAvatar.classList.remove('selected');
    }
    element.classList.add('selected');
    selectedAvatar = element;
    document.getElementById('selected-avatar-url').value = element.src;
}

$(document).ready(function() {
    $(".img-more").click(function() {
        var $container = $(this).closest(".card");
        $container.find(".img-record").toggle("clip");
        $container.find(".card-desc").toggle("clip");
        $container.find(".more").toggle("clip");
    });
});

$(document).ready(function(){
    $(".owl-carousel").each(function() {
        const $carousel = $(this);
        if ($carousel.children().length >= 1) {
            $carousel.owlCarousel({
                items: 6,
                margin: 0,
                responsiveBaseElement: $carousel[0],
                responsive: {
                    0: { items: 1 },
                    650: { items: 2 },
                    990: { items: 3 },
                    1330: { items: 4 },
                    1670: { items: 5 }
                }
            });
        }
    });
});

$(document).ready(function() {
    var leftMenu = $('.left-head-menu');
    var bodyDiv = $('.body');

    var initialOffset = leftMenu.offset().top;

    $(window).scroll(function() {
        var scrollTop = $(window).scrollTop();

        if (scrollTop >= initialOffset) {
            leftMenu.addClass('scroll');
            bodyDiv.addClass('scroll');
        } else {
            leftMenu.removeClass('scroll');
            bodyDiv.removeClass('scroll');
        }
    });
});



/**
 * Created by Dimas Ciputra <dimas@kartoza.com> on 15/07/16.
 */

$(".pop-image").on("click", function() {
    $('#imagepreview').attr('src', $(this).children().attr('id'));
    $('#image-url').attr('href', $(this).children().attr('id'));
    $('#imagemodal').addClass('is-active');
    return false;
});

$(".pop-gif").on("click", function() {
    $('#imagepreview').attr('src', $(this).siblings().attr('id'));
    $('#image-url').attr('href', $(this).siblings().attr('id'));
    $('#imagemodal').addClass('is-active');
    return false;
});

function closeImageModal() {
    $('#imagemodal').removeClass('is-active')
}

$(document).ready(function() {
  // form function to request server
  $(function() {
    $('a#calculate').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/addfeed', {
        url: $('input[name="url"]').val(),
      }, function(data) {
        appendImages(data, removeSmall)
      });
      return false;
    });
  });

  function removeSmall() {
    $('.grid-item').each(function() {
      $(this).find('img').on('load', function() {
        var h = ($(this)[0].naturalHeight);
        var w = ($(this)[0].naturalWidth);
        if ((h * w) < 2500) {
          $(this).closest('div').remove();
        }
      })
    })
  }
  
  function appendImages(arrayImages, callback) {
    for (i = 0; i < arrayImages.length; i++){
      var $item = $('<div data-date="' + arrayImages[i].date + '" class="grid-item"><a href="' + arrayImages[i].source + '"><img src="' + arrayImages[i].url + '" /></a></div>')
      $('.grid').append( $item )
      .isotope('appended', $item );
    }
    $('.grid').imagesLoaded().progress(function() {
      $('.grid').isotope('layout');
    });
    callback();
  }

  // initialize isotope
  $('.grid').isotope({
    itemSelector: '.grid-item',
  })
  $('.grid').imagesLoaded().progress(function() {
    $('.grid').isotope('layout');
    removeSmall()
  })
})

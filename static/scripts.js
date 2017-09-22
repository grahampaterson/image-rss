
$(document).ready(function() {
  // function to add feed subscription
  $(function() {
    $('a#addfeed').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/addfeed', {
        url: $('input[name="url"]').val(),
      }, function(data) {
        appendImages(data, removeSmall)
        // TODO and subscription information to page
      });
      return false;
    });
  });

  // function to remove subscription
  // on clicking a remove button sends the subscription id to the server
  // if the subscription is succesfully removed from server remove the sub contents
  // from the page
  $(function() {
    $('.sub').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + '/removefeed', {
        subid: $(this).data('id'),// TODO get feed id
      }, function(data) {
        if (data.feedid > 0) {
          //TODO removeImages(data.feedid);
          console.log(data.feedid);
        };
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

      // var $item = $('<div data-feedid="' + arrayImages[i].feed_id + '" data-date="' + arrayImages[i].date + '" class="grid-item"><a href="' + arrayImages[i].source + '"><img src="' + arrayImages[i].url + '" /></a></div>')
      var $item = $(`<div data-feedid=${ arrayImages[i].feed_id } data-date=${ arrayImages[i].date } class="grid-item">
                      <a href="${ arrayImages[i].source }">
                        <img src="${ arrayImages[i].url }" />
                      </a></div>`)
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

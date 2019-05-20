$(function() {
  $('#gacha-button').on('click',function(e) {
    let form = $('#gacha-form').get()[0];
    let formData = new FormData(form);

    $.ajax({
      url: '/gacha',
      method: 'post',
      dataType: 'json',
      data: formData,
      processData: false,
      contentType: false
    }).done(function(res) {
      console.log(res);
    }).fail(function(jqXHR, textStatus,errorThrown) {
      console.log('ERROR', jqXHR, textStatus, errorThrown);
    });

    return false;
  });
});

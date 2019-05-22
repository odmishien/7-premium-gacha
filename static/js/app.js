$(function() {
  $('#gacha-button').on('click',function(e) {
    let total = $('#gacha-form #total').val();
    let genre = $('input[name="genre[]"]:checked').map(function(){ return $(this).val(); }).get();
    var json = {
      total: total,
      genre: genre
    };

    $.ajax({
      url: '/gacha',
      method: 'post',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(json),
    }).done(function(res) {
      products = res["products"];
      total = res["total"];
      total_with_tax = res["total_with_tax"];

      $('#result-products').empty();
      for(let product of products) {
        $('#result-products').append(`<tr><td>${product.ProductName}</td><td>${product.Price}</td><td>${product.PriceWithTax}</td></tr>`);
      }
      $('#result-total').html('¥' + total);
      $('#result-total-with-tax').html('¥' + total_with_tax);
    }).fail(function(jqXHR, textStatus,errorThrown) {
      alert("サーバとの通信に失敗しました...");
    });
    return false;
  });
});

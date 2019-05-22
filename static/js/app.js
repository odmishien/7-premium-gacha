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
      $('#twitter-share-area').empty();
      var products_text_for_twitter = '';

      for(let product of products) {
        $('#result-products').append(`<tr><td>${product.ProductName}</td><td>${product.Price}</td><td>${product.PriceWithTax}</td></tr>`);
        products_text_for_twitter = products_text_for_twitter + product.ProductName + '\n'
      }
      $('#result-total').html('¥' + total);
      $('#result-total-with-tax').html('¥' + total_with_tax);
      $('#twitter-share-area').append(`<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-text="セブンプレミアムガチャを回したよ \n ${products_text_for_twitter}みんなも回してね\n" data-url="https://seven-premium-gacha.herokuapp.com/" data-lang="ja" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>`);
    }).fail(function(jqXHR, textStatus,errorThrown) {
      alert("サーバとの通信に失敗しました...");
    });
    return false;
  });
});

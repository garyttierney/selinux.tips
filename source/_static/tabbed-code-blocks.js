$(function() {

	$('.tabbed-code-block-container').each(function () {
		var el = $(this);
		var codeBlocks = el.find('.tabbed-code-block');

		var list = $("<ul>", {
			class: 'tabs'
		});

		var clickHandler = function (e) {
			var li = $(this);
			var key = li.attr('data-key');
			var block = el.find('.tabbed-code-block[data-key="' + key + '"]');

			el.find('li, .tabbed-code-block').removeClass('active');
			li.addClass('active');
			block.addClass('active');
		};

		codeBlocks.each(function () {
			var codeBlock = $(this),
			    language = codeBlock.children('strong').text();

			codeBlock.attr('data-key', language);

			var listItem = $("<li>");
			listItem.html(language);
			listItem.attr('data-key', language);
			listItem.on('click', clickHandler);

			list.append(listItem);
		});

		var firstListItem = list.find('li').first();
		firstListItem.click();

		el.prepend(list);
	});

});

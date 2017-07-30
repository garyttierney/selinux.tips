import os
import re

from docutils.parsers.rst import Directive, directives
from docutils import nodes

from sphinx.directives import container_wrapper

class TabbedCodeBlockDirective(Directive):
	has_content = True
	option_spec = {
		'caption': directives.unchanged_required
	}

	def run(self):
		text = '\n'.join(self.content)
		dummy_node = nodes.container(text)

		self.state.nested_parse(self.content, self.content_offset, dummy_node)

		container = nodes.container('')
		container['classes'].append('tabbed-code-block-container')

		for code_block in dummy_node:
			code_block_container = nodes.container(code_block.astext())
			code_block_container['classes'].append('tabbed-code-block')

			language = re.sub(r"[\-_]", " ", code_block['language'])
			code_block_label = nodes.strong(text=language)
			code_block_label.set_class('language-label')

			code_block_container.append(code_block_label)
			code_block_container.append(code_block)

			container.append(code_block_container)

		self.add_name(container)

		caption = self.options.get('caption')
		if caption:
			return [container_wrapper(self, container, caption)]

		return [container]

def setup(app):
	app.add_directive('tabbed-code-block', TabbedCodeBlockDirective)

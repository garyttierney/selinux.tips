import os
import re

from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from docutils import nodes


def container_wrapper(directive, literal_node, caption):
    # type: (SphinxDirective, nodes.Node, str) -> nodes.container
    container_node = nodes.container(
        "", literal_block=True, classes=["literal-block-wrapper"]
    )
    parsed = nodes.Element()
    directive.state.nested_parse(
        StringList([caption], source=""), directive.content_offset, parsed
    )
    if isinstance(parsed[0], nodes.system_message):
        msg = "Invalid caption: %s" % parsed[0].astext()
        raise ValueError(msg)
    elif isinstance(parsed[0], nodes.Element):
        caption_node = nodes.caption(parsed[0].rawsource, "", *parsed[0].children)
        caption_node.source = literal_node.source
        caption_node.line = literal_node.line
        container_node += caption_node
        container_node += literal_node
        return container_node
    else:
        raise RuntimeError  # never reached


class TabbedCodeBlockDirective(Directive):
    has_content = True
    option_spec = {"caption": directives.unchanged_required}

    def run(self):
        text = "\n".join(self.content)
        dummy_node = nodes.container(text)

        self.state.nested_parse(self.content, self.content_offset, dummy_node)

        container = nodes.container("")
        container["classes"].append("tabbed-code-block-container")

        for code_block in dummy_node:
            code_block_container = nodes.container(code_block.astext())
            code_block_container["classes"].append("tabbed-code-block")

            language = re.sub(r"[\-_]", " ", code_block["language"])
            code_block_label = nodes.strong(text=language)
            code_block_label.set_class("language-label")

            code_block_container.append(code_block_label)
            code_block_container.append(code_block)

            container.append(code_block_container)

        self.add_name(container)

        caption = self.options.get("caption")
        if caption:
            return [container_wrapper(self, container, caption)]

        return [container]


def setup(app):
    app.add_directive("tabbed-code-block", TabbedCodeBlockDirective)

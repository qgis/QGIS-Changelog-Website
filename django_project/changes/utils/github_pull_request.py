""" Tools for parsing the GitHub pull request. """

import re
from typing import Optional

_NEXT_HEADING = r'^[ \t]{0,3}#{1,6}[ \t]'

_AI_USAGE_SECTION = re.compile(
    r'^[ \t]{0,3}#{1,6}[ \t]*AI tool usage[ \t#]*$'
    r'.*?(?=<!--|' + _NEXT_HEADING + r'|\Z)',
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

# The bold QEP 408 paragraph is optional and may not cross a blank line.
_AI_CERTIFY_BLOCK = re.compile(
    r'^[ \t]*(?:[-*+][ \t]+)?\[[ \t]*x?[ \t]*\][ \t]*'
    r'I certify that no AI tool[^\n]*'
    r'(?:\n(?:[ \t]*\n)*[ \t]*\*\*(?:(?!\n[ \t]*\n).)*?'
    r'See \[QEP 408\]\([^)\n]*\) for details\.\*\*)?',
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

_HTML_COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)

_TEMPLATE_MARKERS = (
    'BEFORE HITTING SUBMIT',
    'IMPORTANT NOTES FOR FIRST TIME CONTRIBUTORS',
)


def _drop_template_comment(match: re.Match) -> str:
    comment = match.group(0)
    if any(marker in comment for marker in _TEMPLATE_MARKERS):
        return ''
    return comment


def strip_pr_boilerplate(body: Optional[str]) -> Optional[str]:
    """Remove the QGIS pull request template boilerplate from a PR body.

    It removes the AI tool usage disclosure (heading or certify variant)
    and the template HTML comment. A body without any of them is returned
    unchanged, so running this twice gives the same result.
    """
    if not body:
        return body

    text = body.replace('\r\n', '\n')
    text, ai_sections = _AI_USAGE_SECTION.subn('', text)
    text, certify_blocks = _AI_CERTIFY_BLOCK.subn('', text)
    cleaned = _HTML_COMMENT.sub(_drop_template_comment, text)
    if not (ai_sections or certify_blocks or cleaned != text):
        return body

    cleaned = re.sub(r'\n(?:[ \t]*\n){2,}', '\n\n', cleaned)
    return cleaned.strip()


def parse_funded_by(content: str) -> tuple:
    """ Parse the pull request content and find a 'funded by'.

    It returns the content but without the funder in it if was found.
    """
    token = (
        'funded by', 'sponsored by', 'this is funded by',
        'this is sponsored by',
    )
    funded_regex = r'^({})([\s:]*)'.format('|'.join(token))
    url_regex = r'(https?://\S+)'

    new_content = []
    funded_by = ''
    funded_by_url = ''

    # noinspection PyBroadException
    try:
        lines = content.split('\n')
        for line in lines:

            # If it starts by a markdown bullet list
            cleaned = line.lstrip('* ').strip()
            if cleaned.lower().startswith(token):

                # Remove the "funded by"
                cleaned = re.sub(
                    funded_regex, '', cleaned, flags=re.IGNORECASE)

                # Look for URL
                urls = re.findall(url_regex, cleaned)
                if urls:
                    funded_by_url = urls[0]

                # Remove the URL
                funder = re.sub(url_regex, '', cleaned)
                funded_by = funder.strip()
            else:
                new_content.append(line)

        content = '\n'.join(new_content)
        content = content.strip()
        return content, funded_by, funded_by_url

    except Exception:
        # Let's be safe
        return content, '', ''

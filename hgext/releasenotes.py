# Copyright 2017-present Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

"""generate release notes from commit messages (EXPERIMENTAL)

It is common to maintain files detailing changes in a project between
releases. Maintaining these files can be difficult and time consuming.
The :hg:`releasenotes` command provided by this extension makes the
process simpler by automating it.
"""



import errno
import re
import sys
import textwrap

from mercurial.i18n import _
from mercurial import (
    config,
    error,
    minirst,
    registrar,
    scmutil,
    util,
)

cmdtable = {}
command = registrar.command(cmdtable)

# Note for extension authors: ONLY specify testedwith = 'ships-with-hg-core' for
# extensions which SHIP WITH MERCURIAL. Non-mainline extensions should
# be specifying the version(s) of Mercurial they are tested with, or
# leave the attribute unspecified.
testedwith = 'ships-with-hg-core'

DEFAULT_SECTIONS = [
    ('feature', _('New Features')),
    ('bc', _('Backwards Compatibility Changes')),
    ('fix', _('Bug Fixes')),
    ('perf', _('Performance Improvements')),
    ('api', _('API Changes')),
]

RE_DIRECTIVE = re.compile('^\.\. ([a-zA-Z0-9_]+)::\s*([^$]+)?$')

BULLET_SECTION = _('Other Changes')

class parsedreleasenotes(object):
    def __init__(self):
        self.sections = {}

    def __contains__(self, section):
        return section in self.sections

    def __iter__(self):
        return iter(sorted(self.sections))

    def addtitleditem(self, section, title, paragraphs):
        """Add a titled release note entry."""
        self.sections.setdefault(section, ([], []))
        self.sections[section][0].append((title, paragraphs))

    def addnontitleditem(self, section, paragraphs):
        """Adds a non-titled release note entry.

        Will be rendered as a bullet point.
        """
        self.sections.setdefault(section, ([], []))
        self.sections[section][1].append(paragraphs)

    def titledforsection(self, section):
        """Returns titled entries in a section.

        Returns a list of (title, paragraphs) tuples describing sub-sections.
        """
        return self.sections.get(section, ([], []))[0]

    def nontitledforsection(self, section):
        """Returns non-titled, bulleted paragraphs in a section."""
        return self.sections.get(section, ([], []))[1]

    def hastitledinsection(self, section, title):
        return any(t[0] == title for t in self.titledforsection(section))

    def merge(self, ui, other):
        """Merge another instance into this one.

        This is used to combine multiple sources of release notes together.
        """
        for section in other:
            for title, paragraphs in other.titledforsection(section):
                if self.hastitledinsection(section, title):
                    # TODO prompt for resolution if different and running in
                    # interactive mode.
                    ui.write(_('%s already exists in %s section; ignoring\n') %
                             (title, section))
                    continue

                # TODO perform similarity comparison and try to match against
                # existing.
                self.addtitleditem(section, title, paragraphs)

            for paragraphs in other.nontitledforsection(section):
                if paragraphs in self.nontitledforsection(section):
                    continue

                # TODO perform similarily comparison and try to match against
                # existing.
                self.addnontitleditem(section, paragraphs)

class releasenotessections(object):
    def __init__(self, ui, repo=None):
        if repo:
            sections = util.sortdict(DEFAULT_SECTIONS)
            custom_sections = getcustomadmonitions(repo)
            if custom_sections:
                sections.update(custom_sections)
            self._sections = list(sections.items())
        else:
            self._sections = list(DEFAULT_SECTIONS)

    def __iter__(self):
        return iter(self._sections)

    def names(self):
        return [t[0] for t in self._sections]

    def sectionfromtitle(self, title):
        for name, value in self._sections:
            if value == title:
                return name

        return None

def getcustomadmonitions(repo):
    ctx = repo['.']
    p = config.config()

    def read(f, sections=None, remap=None):
        if f in ctx:
            data = ctx[f].data()
            p.parse(f, data, sections, remap, read)
        else:
            raise error.Abort(_(".hgreleasenotes file \'%s\' not found") %
                              repo.pathto(f))

    if '.hgreleasenotes' in ctx:
        read('.hgreleasenotes')
    return p['sections']

def parsenotesfromrevisions(repo, directives, revs):
    notes = parsedreleasenotes()

    for rev in revs:
        ctx = repo[rev]

        blocks, pruned = minirst.parse(ctx.description(),
                                       admonitions=directives)

        for i, block in enumerate(blocks):
            if block['type'] != 'admonition':
                continue

            directive = block['admonitiontitle']
            title = block['lines'][0].strip() if block['lines'] else None

            if i + 1 == len(blocks):
                raise error.Abort(_('release notes directive %s lacks content')
                                  % directive)

            # Now search ahead and find all paragraphs attached to this
            # admonition.
            paragraphs = []
            for j in range(i + 1, len(blocks)):
                pblock = blocks[j]

                # Margin blocks may appear between paragraphs. Ignore them.
                if pblock['type'] == 'margin':
                    continue

                if pblock['type'] != 'paragraph':
                    raise error.Abort(_('unexpected block in release notes '
                                        'directive %s') % directive)

                if pblock['indent'] > 0:
                    paragraphs.append(pblock['lines'])
                else:
                    break

            # TODO consider using title as paragraph for more concise notes.
            if not paragraphs:
                raise error.Abort(_('could not find content for release note '
                                    '%s') % directive)

            if title:
                notes.addtitleditem(directive, title, paragraphs)
            else:
                notes.addnontitleditem(directive, paragraphs)

    return notes

def parsereleasenotesfile(sections, text):
    """Parse text content containing generated release notes."""
    notes = parsedreleasenotes()

    blocks = minirst.parse(text)[0]

    def gatherparagraphsbullets(offset, title=False):
        notefragment = []

        for i in range(offset + 1, len(blocks)):
            block = blocks[i]

            if block['type'] == 'margin':
                continue
            elif block['type'] == 'section':
                break
            elif block['type'] == 'bullet':
                if block['indent'] != 0:
                    raise error.Abort(_('indented bullet lists not supported'))
                if title:
                    lines = [l[1:].strip() for l in block['lines']]
                    notefragment.append(lines)
                    continue
                else:
                    lines = [[l[1:].strip() for l in block['lines']]]

                    for block in blocks[i + 1:]:
                        if block['type'] in ('bullet', 'section'):
                            break
                        if block['type'] == 'paragraph':
                            lines.append(block['lines'])
                    notefragment.append(lines)
                    continue
            elif block['type'] != 'paragraph':
                raise error.Abort(_('unexpected block type in release notes: '
                                    '%s') % block['type'])
            if title:
                notefragment.append(block['lines'])

        return notefragment

    currentsection = None
    for i, block in enumerate(blocks):
        if block['type'] != 'section':
            continue

        title = block['lines'][0]

        # TODO the parsing around paragraphs and bullet points needs some
        # work.
        if block['underline'] == '=':  # main section
            name = sections.sectionfromtitle(title)
            if not name:
                raise error.Abort(_('unknown release notes section: %s') %
                                  title)

            currentsection = name
            bullet_points = gatherparagraphsbullets(i)
            if bullet_points:
                for para in bullet_points:
                    notes.addnontitleditem(currentsection, para)

        elif block['underline'] == '-':  # sub-section
            if title == BULLET_SECTION:
                bullet_points = gatherparagraphsbullets(i)
                for para in bullet_points:
                    notes.addnontitleditem(currentsection, para)
            else:
                paragraphs = gatherparagraphsbullets(i, True)
                notes.addtitleditem(currentsection, title, paragraphs)
        else:
            raise error.Abort(_('unsupported section type for %s') % title)

    return notes

def serializenotes(sections, notes):
    """Serialize release notes from parsed fragments and notes.

    This function essentially takes the output of ``parsenotesfromrevisions()``
    and ``parserelnotesfile()`` and produces output combining the 2.
    """
    lines = []

    for sectionname, sectiontitle in sections:
        if sectionname not in notes:
            continue

        lines.append(sectiontitle)
        lines.append('=' * len(sectiontitle))
        lines.append('')

        # First pass to emit sub-sections.
        for title, paragraphs in notes.titledforsection(sectionname):
            lines.append(title)
            lines.append('-' * len(title))
            lines.append('')

            wrapper = textwrap.TextWrapper(width=78)
            for i, para in enumerate(paragraphs):
                if i:
                    lines.append('')
                lines.extend(wrapper.wrap(' '.join(para)))

            lines.append('')

        # Second pass to emit bullet list items.

        # If the section has titled and non-titled items, we can't
        # simply emit the bullet list because it would appear to come
        # from the last title/section. So, we emit a new sub-section
        # for the non-titled items.
        nontitled = notes.nontitledforsection(sectionname)
        if notes.titledforsection(sectionname) and nontitled:
            # TODO make configurable.
            lines.append(BULLET_SECTION)
            lines.append('-' * len(BULLET_SECTION))
            lines.append('')

        for paragraphs in nontitled:
            wrapper = textwrap.TextWrapper(initial_indent='* ',
                                           subsequent_indent='  ',
                                           width=78)
            lines.extend(wrapper.wrap(' '.join(paragraphs[0])))

            wrapper = textwrap.TextWrapper(initial_indent='  ',
                                           subsequent_indent='  ',
                                           width=78)
            for para in paragraphs[1:]:
                lines.append('')
                lines.extend(wrapper.wrap(' '.join(para)))

            lines.append('')

    if lines[-1]:
        lines.append('')

    return '\n'.join(lines)

@command('releasenotes',
    [('r', 'rev', '', _('revisions to process for release notes'), _('REV'))],
    _('[-r REV] FILE'))
def releasenotes(ui, repo, file_, rev=None):
    """parse release notes from commit messages into an output file

    Given an output file and set of revisions, this command will parse commit
    messages for release notes then add them to the output file.

    Release notes are defined in commit messages as ReStructuredText
    directives. These have the form::

       .. directive:: title

          content

    Each ``directive`` maps to an output section in a generated release notes
    file, which itself is ReStructuredText. For example, the ``.. feature::``
    directive would map to a ``New Features`` section.

    Release note directives can be either short-form or long-form. In short-
    form, ``title`` is omitted and the release note is rendered as a bullet
    list. In long form, a sub-section with the title ``title`` is added to the
    section.

    The ``FILE`` argument controls the output file to write gathered release
    notes to. The format of the file is::

       Section 1
       =========

       ...

       Section 2
       =========

       ...

    Only sections with defined release notes are emitted.

    If a section only has short-form notes, it will consist of bullet list::

       Section
       =======

       * Release note 1
       * Release note 2

    If a section has long-form notes, sub-sections will be emitted::

       Section
       =======

       Note 1 Title
       ------------

       Description of the first long-form note.

       Note 2 Title
       ------------

       Description of the second long-form note.

    If the ``FILE`` argument points to an existing file, that file will be
    parsed for release notes having the format that would be generated by this
    command. The notes from the processed commit messages will be *merged*
    into this parsed set.

    During release notes merging:

    * Duplicate items are automatically ignored
    * Items that are different are automatically ignored if the similarity is
      greater than a threshold.

    This means that the release notes file can be updated independently from
    this command and changes should not be lost when running this command on
    that file. A particular use case for this is to tweak the wording of a
    release note after it has been added to the release notes file.
    """
    sections = releasenotessections(ui, repo)

    revs = scmutil.revrange(repo, [rev or 'not public()'])
    incoming = parsenotesfromrevisions(repo, sections.names(), revs)

    try:
        with open(file_, 'rb') as fh:
            notes = parsereleasenotesfile(sections, fh.read())
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise

        notes = parsedreleasenotes()

    notes.merge(ui, incoming)

    with open(file_, 'wb') as fh:
        fh.write(serializenotes(sections, notes))

@command('debugparsereleasenotes', norepo=True)
def debugparsereleasenotes(ui, path, repo=None):
    """parse release notes and print resulting data structure"""
    if path == '-':
        text = sys.stdin.read()
    else:
        with open(path, 'rb') as fh:
            text = fh.read()

    sections = releasenotessections(ui, repo)

    notes = parsereleasenotesfile(sections, text)

    for section in notes:
        ui.write(_('section: %s\n') % section)
        for title, paragraphs in notes.titledforsection(section):
            ui.write(_('  subsection: %s\n') % title)
            for para in paragraphs:
                ui.write(_('    paragraph: %s\n') % ' '.join(para))

        for paragraphs in notes.nontitledforsection(section):
            ui.write(_('  bullet point:\n'))
            for para in paragraphs:
                ui.write(_('    paragraph: %s\n') % ' '.join(para))
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import glob
import re

import docutils.core
import testtools


# Used for new sections introduced during a release.
# - "History" introduced in Liberty should be
# mandatory for M.
OPTIONAL_SECTIONS = ("History",)


class TestTitles(testtools.TestCase):
    def _get_title(self, section_tree):
        section = {
            'subtitles': [],
        }
        for node in section_tree:
            if node.tagname == 'title':
                section['name'] = node.rawsource
            elif node.tagname == 'section':
                subsection = self._get_title(node)
                section['subtitles'].append(subsection['name'])
        return section

    def _get_titles(self, spec):
        titles = {}
        for node in spec:
            if node.tagname == 'section':
                # Note subsection subtitles are thrown away
                section = self._get_title(node)
                titles[section['name']] = section['subtitles']
        return titles

    def _check_titles(self, filename, expect, actual):
        missing_sections = [x for x in expect.keys() if (
            x not in actual.keys()) and (x not in OPTIONAL_SECTIONS)]
        extra_sections = [x for x in actual.keys() if x not in expect.keys()]

        msgs = []
        if len(missing_sections) > 0:
            msgs.append("Missing sections: %s" % missing_sections)
        if len(extra_sections) > 0:
            msgs.append("Extra sections: %s" % extra_sections)

        for section in expect.keys():
            missing_subsections = [x for x in expect[section]
                                   if x not in actual.get(section, {})]
            # extra subsections are allowed
            if len(missing_subsections) > 0:
                msgs.append("Section '%s' is missing subsections: %s"
                            % (section, missing_subsections))

        if len(msgs) > 0:
            self.fail("While checking '%s':\n  %s"
                      % (filename, "\n  ".join(msgs)))

    def _check_lines_wrapping(self, tpl, raw):
        code_block = False
        for i, line in enumerate(raw.split("\n")):
            # NOTE(ndipanov): Allow code block lines to be longer than 79 ch
            if code_block:
                if not line or line.startswith(" "):
                    continue
                else:
                    code_block = False
            if "::" in line:
                code_block = True
            if "http://" in line or "https://" in line:
                continue
            if line.startswith("..") and "image::" in line:
                continue
            # Allow lines which do not contain any whitespace
            if re.match("\s*[^\s]+$", line):
                continue
            self.assertTrue(
                len(line) < 80,
                msg="%s:%d: Line limited to a maximum of 79 characters." %
                (tpl, i + 1))

    def _check_no_cr(self, tpl, raw):
        matches = re.findall('\r', raw)
        self.assertEqual(
            len(matches), 0,
            "Found %s literal carriage returns in file %s" %
            (len(matches), tpl))

    def _check_trailing_spaces(self, tpl, raw):
        for i, line in enumerate(raw.split("\n")):
            trailing_spaces = re.findall(" +$", line)
            self.assertEqual(len(trailing_spaces), 0,
                    "Found trailing spaces on line %s of %s" % (i + 1, tpl))

    def test_template(self):
        releases = [x.split('/')[1] for x in glob.glob('specs/*/')]
        self.assertTrue(len(releases), "Not able to find spec directories")
        for release in releases:
            with open("specs/%s-template.rst" % release) as f:
                template = f.read()
            spec = docutils.core.publish_doctree(template)
            template_titles = self._get_titles(spec)

            files = glob.glob("specs/%s/*/*" % release)
            for filename in files:
                self.assertTrue(filename.endswith(".rst"),
                                "spec %s must use 'rst' extension."
                                % filename)
                with open(filename) as f:
                    data = f.read()

                spec = docutils.core.publish_doctree(data)
                titles = self._get_titles(spec)
                self._check_titles(filename, template_titles, titles)
                self._check_lines_wrapping(filename, data)
                self._check_no_cr(filename, data)
                self._check_trailing_spaces(filename, data)

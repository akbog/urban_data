from collections import defaultdict
import re

class CategorizedCorpusReader(object):

    def __init__(self, kwargs):
        self._f2c = None  #: file-to-category mapping
        self._c2f = None  #: category-to-file mapping

        self._pattern = None  #: regexp specifying the mapping
        self._map = None  #: dict specifying the mapping
        self._file = None  #: fileid of file containing the mapping
        self._delimiter = None  #: delimiter for ``self._file``

        if "cat_pattern" in kwargs:
            self._pattern = kwargs["cat_pattern"]
            del kwargs["cat_pattern"]
        elif "cat_map" in kwargs:
            self._map = kwargs["cat_map"]
            del kwargs["cat_map"]
        elif "cat_file" in kwargs:
            self._file = kwargs["cat_file"]
            del kwargs["cat_file"]
            if "cat_delimiter" in kwargs:
                self._delimiter = kwargs["cat_delimiter"]
                del kwargs["cat_delimiter"]
        else:
            raise ValueError(
                "Expected keyword argument cat_pattern or " "cat_map or cat_file."
            )

        if "cat_pattern" in kwargs or "cat_map" in kwargs or "cat_file" in kwargs:
            raise ValueError(
                "Specify exactly one of: cat_pattern, " "cat_map, cat_file."
            )

    def _init(self):
        self._f2c = defaultdict(set)
        self._c2f = defaultdict(set)

        if self._pattern is not None:
            for file_id in self._fileids:
                # print(file_id)
                # print(self._pattern)
                category = re.match(self._pattern, file_id).group(0)
                self._add(file_id, category)

        elif self._map is not None:
            for (file_id, categories) in self._map.items():
                for category in categories:
                    self._add(file_id, category)

        elif self._file is not None:
            for line in self.open(self._file).readlines():
                line = line.strip()
                file_id, categories = line.split(self._delimiter, 1)
                if file_id not in self.fileids():
                    raise ValueError(
                        "In category mapping file %s: %s "
                        "not found" % (self._file, file_id)
                    )
                for category in categories.split(self._delimiter):
                    self._add(file_id, category)

    def _add(self, file_id, category):
        self._f2c[file_id].add(category)
        self._c2f[category].add(file_id)

    def categories(self, fileids=None):
        """
        Return a list of the categories that are defined for this corpus,
        or for the file(s) if it is given.
        """
        if self._f2c is None:
            self._init()
        if fileids is None:
            return sorted(self._c2f)
        if isinstance(fileids, str):
            fileids = [fileids]
        return sorted(set.union(*[self._f2c[d] for d in fileids]))


    def fileids(self, categories=None):
        """
        Return a list of file identifiers for the files that make up
        this corpus, or that make up the given category(s) if specified.
        """
        if categories is None:
            return super(CategorizedCorpusReader, self).fileids()
        elif isinstance(categories, str):
            if self._f2c is None:
                self._init()
            """
            Get matching categories to return the proper fileids (this should consider regex only)
            """
            matches = []
            for cat in self._c2f:
                # print(categories)
                # print(cat)
                if re.match(categories, cat):
                    matches.append(cat)
            if len(matches):
                return sorted(set.union(*[self._c2f[c] for c in matches]))
            else:
                raise ValueError("Category %s not found" % categories)
        else:
            if self._f2c is None:
                self._init()
            return sorted(set.union(*[self._c2f[c] for c in categories]))

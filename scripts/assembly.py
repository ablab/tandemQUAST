from os.path import basename, join, splitext, exists

from slugify import slugify

import config


class Assembly:
    def __init__(self, raw_fname=None, out_dir=None, fname=None, name=None):
        self.raw_fname = raw_fname
        self.fname = fname
        self.label = name or slugify(splitext(basename(raw_fname))[0])
        self.name = slugify(splitext(basename(raw_fname))[0])
        self.kmers_fname = join(out_dir, "%s_%s" % (self.name, config.KMERS_FILENAME))
        self.solid_kmers_fname = join(out_dir, "%s_%s" % (self.name, config.SOLID_KMERS_FILENAME))
        self.good_kmers_fname = join(out_dir, "%s_%s" % (self.name, config.GOODKMERS_FILENAME))
        self.all_kmers_fname = join(out_dir, "%s_%s" % (self.name, config.ALLKMERS_FILENAME))
        self.chains_fname = join(out_dir, "%s_%s" % (self.name, config.CHAINS_FILENAME))
        self.bed_fname = join(out_dir, "%s_%s" % (self.name, config.ALIGNMENTS_FILENAME))
        self.sam_fname = join(out_dir, "%s_%s" % (self.name, config.SAM_FILENAME))